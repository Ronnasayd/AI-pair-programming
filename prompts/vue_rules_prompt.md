let's create inside instructions/vue.instructions.md file the rules for code standards
for this project. In this file we should:

- all the code must be written in english,
- Use multi-word component names,
- Use detailed prop definitions,
- Use keyed v-for,
- Avoid v-if with v-for,
- Use component-scoped styling,
- Each component should be in its own file,
- Filenames of Single-File Components should either be always PascalCase or always kebab-case,
- Base components (a.k.a. presentational, dumb, or pure components) that apply app-specific styling and conventions should all begin with a specific prefix, such as Base, App, or V.
- Child components that are tightly coupled with their parent should include the parent component name as a prefix.
- Component names should start with the highest-level (often most general) words and end with descriptive modifying words.
- Components with no content should be self-closing in Single-File Components, string templates, and JSX - but never in in-DOM templates.
- In most projects, component names should always be PascalCase in Single-File Components and string templates - but kebab-case in in-DOM templates.
- Component names should prefer full words over abbreviations.
- Elements with multiple attributes should span multiple lines, with one attribute per line.
- Component templates should only include simple expressions, with more complex expressions refactored into computed properties or methods.
- Complex computed properties should be split into as many simpler properties as possible.

Remember to create examples for each of this
rules and also to bind this rule (vue.instructions.md) to the AGENTS.md file
