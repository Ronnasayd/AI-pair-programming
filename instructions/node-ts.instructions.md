---
description: Node.js/JavaScript/TypeScript rules and guidelines.
applyTo: "**/*.ts, **/*.js,**/*.vue, **/*.jsx, **/*.tsx"
---

Node.js/JavaScript/TypeScript

- All source code in TypeScript.

- Use `npm` for deps + scripts. Do not use other tools.

```bash
npm install axios
npm run build
```

- If needed, install library types. Example: `jest` + `@types/jest`.

```bash
npm install jest @types/jest --save-dev
```

- Before done, always validate typing.

- Prefer `const` over `let`.

```ts
// Good
const maxRetries = 3;
// Use let only when reassignment is needed
let currentAttempt = 0;
```

- Never use `var`.

- Class props must be `private` or `readonly`. Avoid `public`.

```ts
class User {
  private name: string;
  readonly id: string;
}
```

- Prefer `find`/`filter`/`map`/`reduce` over `for`/`while`.

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

- Prefer arrow functions when possible.

```ts
const sum = (a: number, b: number): number => a + b;
```

- Use `async`/`await` for promises. Avoid callbacks.

```ts
// Good
const data = await fetchData();

// Bad
fetchData().then(data => { ... });
```

- Never use `any`. Use existing types or create types for all implemented code.

```ts
// Good
interface UserInput { name: string; email: string; }
function createUser(input: UserInput): User { ... }

// Bad
function createUser(input: any): any { ... }
```

- Never use `require`. Always use `import`.

```ts
// Good
import express from "express";

// Bad
const express = require("express");
```

- Never use `module.exports`. Always use `export`.

```ts
// Good
export default class User {}
export { calculateTotal };

// Bad
module.exports = User;
```

- If file exports one thing, use `default`. If many, use named exports.

```ts
// Single export — default
export default class PaymentService {}

// Multiple exports — named
export function formatDate() {}
export function parseDate() {}
```
