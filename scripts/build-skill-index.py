#!/usr/bin/env python3
"""Build SQLite vector index and name->path manifest from skills/index.yaml."""

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

import yaml

_FRONTMATTER_NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)


def build_manifest(skills_dir: Path) -> dict:
    """Walk skills_dir for SKILL.md files, map frontmatter name -> path + adjacent files."""
    manifest = {}
    for skill_md in sorted(skills_dir.glob("**/SKILL.md")):
        match = _FRONTMATTER_NAME_RE.search(skill_md.read_text())
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


def main():
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
        print(f"Error: {index_path} not found", file=sys.stderr)
        sys.exit(1)

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(index_path.parent)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"Built manifest: {len(manifest)} skills → {manifest_path}")

    if not args.force and db_path.exists():
        if db_path.stat().st_mtime > index_path.stat().st_mtime:
            print("Index up-to-date")
            sys.exit(0)

    from fastembed import TextEmbedding

    print("Loading model...")
    model = TextEmbedding("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    with open(index_path) as f:
        data = yaml.safe_load(f)

    skills = data.get("skills", [])
    if not skills:
        print("No skills found in index.yaml", file=sys.stderr)
        sys.exit(1)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("DROP TABLE IF EXISTS skills")
    conn.execute("""
        CREATE TABLE skills (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            description TEXT NOT NULL,
            hint        TEXT NOT NULL,
            embedding   BLOB NOT NULL
        )
    """)

    rows = []
    for skill in skills:
        names = skill.get("name", [])
        name = names[0] if isinstance(names, list) else names
        desc = skill.get("description", "")
        text = f"{name}: {desc}"
        vector = list(model.embed([text]))[0].astype("float32")
        rows.append((name, desc, desc, vector.tobytes()))

    conn.executemany(
        "INSERT INTO skills (name, description, hint, embedding) VALUES (?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()

    print(f"Built index: {len(rows)} skills → {db_path}")


if __name__ == "__main__":
    main()
