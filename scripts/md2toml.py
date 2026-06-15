import sys
from pathlib import Path
import yaml
import json


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
    escaped_instructions = prompt.replace('"""', '\\"\\"\\"')

    metadata_lines = []
    for key, value in frontmatter.items():
        if isinstance(value, str):
            escaped_val = value.replace('"', '\\"')
            metadata_lines.append(f'{key} = "{escaped_val}"')
        elif isinstance(value, bool):
            metadata_lines.append(f"{key} = {str(value).lower()}")
        elif isinstance(value, (int, float)):
            metadata_lines.append(f"{key} = {value}")
        elif isinstance(value, list):
            json_list = json.dumps(value)
            metadata_lines.append(f"{key} = {json_list}")
        elif value is None:
            metadata_lines.append(f'{key} = ""')
        else:
            json_val = json.dumps(value)
            metadata_lines.append(f"{key} = {json_val}")

    metadata_section = "\n".join(metadata_lines) if metadata_lines else ""

    toml_content = f"""[metadata]
{metadata_section}

[content]
prompt = \"\"\"{escaped_instructions}
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
