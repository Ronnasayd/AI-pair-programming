import yaml
from glob import glob

agents = glob("./agents/**/*", recursive=True)
skills = glob("./skills/**/SKILL.md", recursive=True)
def print_name_description(agents):
    for agent in agents:
        with open(agent, "r", encoding="utf-8") as f:
            content = f.read()
        parts = content.split("---", 2)
        if len(parts) < 3:
            print(f"Skipping {agent}: Invalid format (missing frontmatter)")
            continue
        try:
            frontmatter = yaml.safe_load(parts[1])
            print("name:", frontmatter.get("name"))
            print("description:", frontmatter.get("description"))
            print()
        except yaml.YAMLError as e:
            print(f"Skipping {agent}: Error parsing frontmatter: {e}")
            continue

print("## AGENTS ##\n")
print_name_description(agents)
print("## SKILLS ##\n")
print_name_description(skills)
