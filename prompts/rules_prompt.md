<!-- extraido de: https://github.com/rodrigobranas/aidev_axon_5/blob/main/rules_prompt.md -->

let's create inside instructions/code-standards.instructions.md file the rules for code standards
for this project. In this file we should: all the code must be written in english,
variables, methods and functions must use camelCase, classes and interfaces should use
PascalCase, avoid magic numbers (they must be constants), avoid nesting more than 2 if/
else statements, avoid passing more than 3 parameters, avoid using switch/case, methods
and functions must start with a verb, do not use var prefer let and const, keep methods
and functions below 30 lines of code. Remember to create examples for each of this
rules and also to bind this rule (code-standards.instructions.md) to the AGENTS.md file

let's create inside instructions/folder-structure.instructions.md file the rules for folder structure
for this project. In this file we should define that the folder structure for frontend will be assets, components, constants, hooks, services, types, utils, views and for backend will be routes, services, data. Add that as a directory structure notation and also define besides each directory it's purpose. Remember to also bind this rule (folder-structure.instructions.md) to the AGENTS.md file

let's create inside instructions/http.instructions.md file with the rules to define the API. In this file we should follow REST standards, use kebab-case for compound resources, use plural resource names, avoid more than 3 nested resources, use JSON for request and response payloads, return 200 for success, 422 for business rules error and 500 for other errors. Remember to bind that rule to AGENTS.md file

let's create inside instructions/react.instructions.md file with rules like use functional components, use typescript as .tsx files, keep component state as close as possible to it, pass props explicitly, avoid large components, use tailwind for styling, use usememo to avoid complex computation, prefix hooks with use. Add examples and remember to bind that rule to AGENTS.md file

let's create inside instructions/test.instructions.md file with rules like cover code with tests, keep tests independent, use given, when then or arrange, act, assert as standard, mock date when behavior depends on that, keep test cases under 100 lines of code, make tests very clear and objetive, use beforeeach for similar scenarios and aftereach to clear things like database connections. Add examples and remember to bind that rule to AGENTS.md file
