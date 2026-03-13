import sys
from pathlib import Path
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

    name = frontmatter.get("name", "").replace('"', '\\"')
    description = frontmatter.get("description", "").replace('"', '\\"')
    developer_instructions = parts[2].strip()

    # Escape triple quotes in developer_instructions if they exist
    escaped_instructions = developer_instructions.replace('"""', '\\"\\"\\"')

    toml_content = f"""name = "{name}"
description = "{description}"
developer_instructions = \"\"\"{escaped_instructions}
\"\"\"
"""

    # toml2md adds '.prompt' to the stem, so we remove it if present
    output_stem = input_file.stem
    if output_stem.endswith(".prompt"):
        output_stem = output_stem[:-7]

    output_file = output_dir / f"{output_stem}.toml"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(toml_content)

    print(f"Generated: {output_file}")


def convert_directory(source_dir: str, output_dir: str):
    source = Path(source_dir)
    output = Path(output_dir)

    output.mkdir(parents=True, exist_ok=True)

    for md_file in source.glob("*.md"):
        convert_file(md_file, output)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python md2toml.py <source_dir> <output_dir>")
        sys.exit(1)

    convert_directory(sys.argv[1], sys.argv[2])
