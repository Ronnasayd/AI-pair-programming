#!/usr/bin/env python3
"""Build SQLite vector index and name->path manifest from skills/index.yaml."""

import argparse
import hashlib
import json
import logging
from pathlib import Path
import re
import sqlite3
import sys

from fastembed import TextEmbedding
import yaml

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

_FRONTMATTER_NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)


def build_manifest(skills_dir: Path) -> dict:
    """Walk skills_dir for SKILL.md files, mapping frontmatter name to path + files.

    Args:
        skills_dir: Directory to search recursively for SKILL.md files.

    Returns:
        Mapping of skill name to its skill_md path and adjacent file list.
    """
    manifest = {}
    for skill_md in sorted(skills_dir.glob("**/SKILL.md")):
        match = _FRONTMATTER_NAME_RE.search(skill_md.read_text(encoding="utf-8"))
        if not match:
            continue
        name = match.group(1).strip().strip("'\"")
        skill_dir = skill_md.parent
        files = sorted(
            str(p.relative_to(skill_dir))
            for p in skill_dir.rglob("*")
            if p.is_file() and p != skill_md
        )
        manifest[name] = {
            "skill_md": str(skill_md.relative_to(skills_dir)),
            "files": files,
        }
    return manifest


def _file_hash(path: Path) -> str:
    """Return the sha256 hex digest of path's contents.

    Args:
        path: File to hash.

    Returns:
        Hex-encoded sha256 digest.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_embedding_model(cache_dir: Path) -> TextEmbedding:
    """Load the fastembed TextEmbedding model, caching weights under cache_dir.

    Args:
        cache_dir: Directory where downloaded model weights are cached.

    Returns:
        A loaded fastembed TextEmbedding instance.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Loading model (cache: %s)...", cache_dir)
    return TextEmbedding(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        cache_dir=str(cache_dir),
    )


def _build_rows(
    skills: list, model: TextEmbedding
) -> list[tuple[str, str, str, bytes]]:
    """Embed each skill's name+description into a (name, desc, hint, embedding) row.

    Args:
        skills: Parsed skill entries from index.yaml.
        model: A loaded fastembed TextEmbedding instance.

    Returns:
        List of rows ready for insertion into the skills table.
    """
    rows = []
    for skill in skills:
        names = skill.get("name", [])
        name = names[0] if isinstance(names, list) else names
        desc = skill.get("description", "")
        text = f"{name}: {desc}"
        vector = next(iter(model.embed([text]))).astype("float32")
        rows.append((name, desc, desc, vector.tobytes()))
    return rows


def _write_db(db_path: Path, rows: list[tuple[str, str, str, bytes]]) -> None:
    """Create the skills + skills_fts tables and insert the given rows.

    Args:
        db_path: Destination SQLite database path.
        rows: Rows as produced by _build_rows.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("DROP TABLE IF EXISTS skills")
    conn.execute("DROP TABLE IF EXISTS skills_fts")
    conn.execute("""
        CREATE TABLE skills (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            description TEXT NOT NULL,
            hint        TEXT NOT NULL,
            embedding   BLOB NOT NULL
        )
    """)
    conn.execute("""
        CREATE VIRTUAL TABLE skills_fts USING fts5(
            name, description, content='skills', content_rowid='id'
        )
    """)

    for name, desc, hint, embedding in rows:
        cur = conn.execute(
            "INSERT INTO skills (name, description, hint, embedding) "
            "VALUES (?, ?, ?, ?)",
            (name, desc, hint, embedding),
        )
        conn.execute(
            "INSERT INTO skills_fts (rowid, name, description) VALUES (?, ?, ?)",
            (cur.lastrowid, name, desc),
        )
    conn.commit()
    conn.close()


def main() -> None:
    """Build the skill manifest and, if stale, the embedding index database."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="skills/index.yaml")
    parser.add_argument("--output", default="skills/skills.db")
    parser.add_argument("--manifest", default="skills/manifest.json")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    index_path = Path(args.index)
    db_path = Path(args.output)
    manifest_path = Path(args.manifest)

    if not index_path.exists():
        logger.error("Error: %s not found", index_path)
        sys.exit(1)

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(index_path.parent)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    logger.info("Built manifest: %d skills -> %s", len(manifest), manifest_path)

    hash_path = db_path.with_suffix(db_path.suffix + ".sha256")
    current_hash = _file_hash(index_path)
    index_is_stale = (
        args.force
        or not db_path.exists()
        or not hash_path.exists()
        or hash_path.read_text(encoding="utf-8").strip() != current_hash
    )
    if not index_is_stale:
        logger.info("Index up-to-date")
        sys.exit(0)

    with open(index_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    skills = data.get("skills", [])
    if not skills:
        logger.error("No skills found in index.yaml")
        sys.exit(1)

    model = _load_embedding_model(Path.home() / ".cache" / "fastembed")
    rows = _build_rows(skills, model)
    _write_db(db_path, rows)
    hash_path.write_text(current_hash, encoding="utf-8")

    logger.info("Built index: %d skills -> %s", len(rows), db_path)


if __name__ == "__main__":
    main()
