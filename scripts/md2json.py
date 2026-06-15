import sys
from pathlib import Path
import json
import yaml


def convert_file(input_file: Path, output_dir: Path):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split frontmatter and body
    parts = content.split("---", 2)
    if len(parts) < 3:
        print(f"Skipping {input_file}: Invalid format (missing frontmatter)")
        return

    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        print(f"Skipping {input_file}: Error parsing frontmatter: {e}")
        return

    prompt = parts[2].strip()

    json_content = {"metadata": frontmatter, "prompt": prompt}

    output_file = output_dir / f"{input_file.stem}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json_content, f, indent=2, ensure_ascii=False)

    print(f"Generated: {output_file}")


def convert_directory(source_dir: str, output_dir: str):
    source = Path(source_dir)
    output = Path(output_dir)

    output.mkdir(parents=True, exist_ok=True)

    for md_file in source.glob("*.md"):
        convert_file(md_file, output)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python md2json.py <source_dir> <output_dir>")
        sys.exit(1)

    convert_directory(sys.argv[1], sys.argv[2])
