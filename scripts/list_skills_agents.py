"""Generate agents/index.yaml, skills/index.yaml and instructions/index.yaml.

Globs every SKILL.md, *.agent.md, and instructions/*.md file, extracts
name + description from frontmatter, and writes one index.yaml per
category next to its source directory.
"""

from glob import glob
import os

import yaml

agents = glob("./agents/**/*.agent.md", recursive=True)
skills = glob("./skills/**/SKILL.md", recursive=True)
instructions = glob("./instructions/*.md")


def generate_descriptions(paths: list, name_from_filename: bool = False) -> list:
    """Extract {name, description} entries from each path's frontmatter.

    Args:
        paths: Files to parse (must have a YAML frontmatter block).
        name_from_filename: Use the file's basename as the entry's name
            instead of the frontmatter's "name" field. Agents and
            instructions are keyed by filename elsewhere in the toolkit
            (aipp-settings.json catalog, backend installers); skills are
            keyed by their frontmatter "name".

    Returns:
        A list of {"name": [name], "description": str | None} dicts, one
        per successfully-parsed path.
    """
    values = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        parts = content.split("---", 2)
        if len(parts) < 3:
            print(  # noqa: T201 -- CLI stdout output
                f"Skipping {path}: Invalid format (missing frontmatter)"
            )
            continue
        try:
            frontmatter = yaml.safe_load(parts[1])
            if name_from_filename:
                name = os.path.basename(path)
            else:
                name = frontmatter.get("name")
            values.append(
                {"name": [name], "description": frontmatter.get("description")}
            )
        except yaml.YAMLError as e:
            print(f"Skipping {path}: Error parsing frontmatter: {e}")  # noqa: T201
            continue
    return values


skill_values = generate_descriptions(agents, name_from_filename=True)
data = {"agents": skill_values}
yaml_string = yaml.dump(data, sort_keys=False, allow_unicode=True)
with open("./agents/index.yaml", "w", encoding="utf-8") as f:
    f.write(yaml_string)

skill_values = generate_descriptions(skills)
data = {"skills": skill_values}
yaml_string = yaml.dump(data, sort_keys=False, allow_unicode=True)
with open("./skills/index.yaml", "w", encoding="utf-8") as f:
    f.write(yaml_string)

instruction_values = generate_descriptions(instructions, name_from_filename=True)
data = {"instructions": instruction_values}
yaml_string = yaml.dump(data, sort_keys=False, allow_unicode=True)
with open("./instructions/index.yaml", "w", encoding="utf-8") as f:
    f.write(yaml_string)
