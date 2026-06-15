import sys
from pathlib import Path
import json
import yaml


def convert_file(input_file: Path, output_dir: Path):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    metadata = data.get("metadata", {})
    prompt = data.get("prompt", "")

    frontmatter_yaml = yaml.dump(
        metadata, default_flow_style=False, allow_unicode=True, sort_keys=False
    )

    markdown = f"""---
{frontmatter_yaml}---

{prompt}
"""

    output_file = output_dir / f"{input_file.stem}.prompt.md"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Generated: {output_file}")


def convert_directory(source_dir: str, output_dir: str):
    source = Path(source_dir)
    output = Path(output_dir)

    output.mkdir(parents=True, exist_ok=True)

    for json_file in source.glob("*.json"):
        convert_file(json_file, output)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python json2md.py <source_dir> <output_dir>")
        sys.exit(1)

    convert_directory(sys.argv[1], sys.argv[2])
