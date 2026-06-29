#!/usr/bin/env python3
"""Build SQLite vector index from skills/index.yaml."""

import argparse
import sqlite3
import sys
from pathlib import Path

import yaml


def format_hint(desc):
    if not desc:
        return ""
    sentences = desc.split(". ")
    first = sentences[0]
    if not first.endswith("."):
        first += "."
    return first


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="skills/index.yaml")
    parser.add_argument("--output", default="skills/skills.db")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    index_path = Path(args.index)
    db_path = Path(args.output)

    if not index_path.exists():
        print(f"Error: {index_path} not found", file=sys.stderr)
        sys.exit(1)

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
        vector = list(model.embed([text]))[0]
        hint = format_hint(desc)
        rows.append((name, desc, hint, vector.tobytes()))

    conn.executemany(
        "INSERT INTO skills (name, description, hint, embedding) VALUES (?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()

    print(f"Built index: {len(rows)} skills → {db_path}")


if __name__ == "__main__":
    main()
