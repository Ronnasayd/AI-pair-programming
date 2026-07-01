import yaml
from glob import glob

agents = glob("./agents/**/*.agent.md", recursive=True)
skills = glob("./skills/**/SKILL.md", recursive=True) + glob(
    "./.agents/skills/**/SKILL.md", recursive=True
)


def generate_descriptions(agents):
    values = []
    for agent in agents:
        with open(agent, "r", encoding="utf-8") as f:
            content = f.read()
        parts = content.split("---", 2)
        if len(parts) < 3:
            print(f"Skipping {agent}: Invalid format (missing frontmatter)")
            continue
        try:
            frontmatter = yaml.safe_load(parts[1])
            values.append(
                dict(
                    name=[frontmatter.get("name")],
                    description=frontmatter.get("description"),
                )
            )
            # print(f"  name: \"{frontmatter.get('name')}\"")
            # print(f"  description: \"{frontmatter.get('description')}\"")
            # print()
        except yaml.YAMLError as e:
            print(f"Skipping {agent}: Error parsing frontmatter: {e}")
            continue
    return values


skill_values = generate_descriptions(agents)
data = {"agents": skill_values}
yaml_string = yaml.dump(data, sort_keys=False, allow_unicode=True)
with open("./agents/index.yaml", "w", encoding="utf-8") as f:
    f.write(yaml_string)
# print(yaml_string)

skill_values = generate_descriptions(skills)
data = {"skills": skill_values}
yaml_string = yaml.dump(data, sort_keys=False, allow_unicode=True)
with open("./skills/index.yaml", "w", encoding="utf-8") as f:
    f.write(yaml_string)
# print(yaml_string)
