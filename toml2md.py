import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib


def convert_file(input_file: Path, output_dir: Path):
    with open(input_file, "rb") as f:
        data = tomllib.load(f)

    name = data.get("name", "")
    description = data.get("description", "")
    prompt = data.get("prompt", "")

    markdown = f"""---
name: {name}
description: {description}
---

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

    for toml_file in source.glob("*.toml"):
        convert_file(toml_file, output)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python toml2md.py <source_dir> <output_dir>")
        sys.exit(1)

    convert_directory(sys.argv[1], sys.argv[2])
