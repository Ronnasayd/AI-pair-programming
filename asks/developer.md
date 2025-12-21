# 10 Questions to Validate Whether the LLM Understood the Prompt

1. Explain in a few words what the **LLM’s primary obligation** is before “returning to the user” when it receives a development task.
2. What should the LLM do if it identifies that **part of the source code required to solve the problem is missing**?
3. When the prompt says the LLM **“MUST iterate and continue working,”** what does that imply in terms of **testing and fixes**? Give a concrete example of an iteration.
4. What does **“NEVER end your action without having solved the problem”** mean in practice — what **criteria** should the LLM use to consider a problem solved?
5. How should the LLM proceed when stating that it will make a **tool call (MCP / tool call)**? What is **forbidden** in this behavior?
6. Which steps from the **“Workflow”** section would you follow **before modifying any project file**? List at least three.
7. What kind of **tests** should the LLM write/run before closing the task? Mention principles and examples of **scenarios that must not be forgotten**.
8. If the user interrupts with a **new request or suggestion**, how should the LLM react according to the prompt?
9. Does the prompt require any rule regarding **library and dependency versions** — what is it, and when does it apply?
10. Describe a case in which the LLM must use the **Internet or external documentation** during the task. What should be searched for and why?
