Node.js/JavaScript/TypeScript

- All source code must be written in TypeScript.

- Use npm as the default tool for managing dependencies and running scripts. Never use different tools for this purpose.

```bash
npm install axios
npm run build
```

- If necessary, install the types for libraries. For example: jest and @types/jest.

```bash
npm install jest @types/jest --save-dev
```

- Before finishing a task, always validate that the typing is correct.

- Use const instead of let wherever possible.

```ts
// Good
const maxRetries = 3;
// Use let only when reassignment is needed
let currentAttempt = 0;
```

- Never use var to declare a variable.

- Always declare class properties as private or readonly, avoiding the use of public.

```ts
class User {
  private name: string;
  readonly id: string;
}
```

- Prefer the use of find, filter, map, and reduce instead of for and while.

```ts
// Good
const activeUsers = users.filter((u) => u.isActive);
const names = users.map((u) => u.name);

// Bad
const activeUsers = [];
for (let i = 0; i < users.length; i++) {
  if (users[i].isActive) activeUsers.push(users[i]);
}
```

- Prefer the use of arrow functions wherever possible.

```ts
const sum = (a: number, b: number): number => a + b;
```

- Always use async/await to handle promises. Avoid the use of callbacks.

```ts
// Good
const data = await fetchData();

// Bad
fetchData().then(data => { ... });
```

- Never use any. Always use existing types or create types for everything that is implemented.

```ts
// Good
interface UserInput { name: string; email: string; }
function createUser(input: UserInput): User { ... }

// Bad
function createUser(input: any): any { ... }
```

- Never use require to import modules. Always use import.

```ts
// Good
import express from "express";

// Bad
const express = require("express");
```

- Never use module.exports to export modules. Always use export.

```ts
// Good
export default class User {}
export { calculateTotal };

// Bad
module.exports = User;
```

- If the file has only one thing being exported, use default. Otherwise, use named exports.

```ts
// Single export — default
export default class PaymentService {}

// Multiple exports — named
export function formatDate() {}
export function parseDate() {}
```
