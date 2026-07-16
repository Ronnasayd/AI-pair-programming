---
description: Node/TS conventions — npm only, TypeScript everywhere, no any/var/require/module.exports, private/readonly class props, prefer find/filter/map/reduce and arrow functions, async/await over callbacks, default vs named exports. Apply to any .ts/.js/.vue/.jsx/.tsx file. Do NOT use for React-specific rules (see react.instructions.md) or general naming/style (see code.instructions.md).
applyTo: "**/*.ts, **/*.js,**/*.vue, **/*.jsx, **/*.tsx"
---

# Node.js/JavaScript/TypeScript

All source in TypeScript. Use `npm` only (deps + scripts, no other tool). Install lib types when needed (`npm install jest @types/jest --save-dev`). Always validate typing before done.

| Rule                                              | ✅ Good                                  | ❌ Bad                                |
| ------------------------------------------------- | ---------------------------------------- | ------------------------------------- |
| `const` over `let`; never `var`                   | `const maxRetries = 3`                   | `var maxRetries = 3`                  |
| Class props `private`/`readonly`, avoid `public`  | `private name: string`                   | `public name: string`                 |
| `find`/`filter`/`map`/`reduce` over `for`/`while` | `users.filter(u => u.isActive)`          | manual `for` loop + push              |
| Prefer arrow functions                            | `const sum = (a, b) => a + b`            | `function sum(a, b) { return a + b }` |
| `async`/`await` over callbacks                    | `const data = await fetchData()`         | `fetchData().then(data => {...})`     |
| Never `any` — define real types                   | `function createUser(input: UserInput)`  | `function createUser(input: any)`     |
| `import`, never `require`                         | `import express from "express"`          | `const express = require("express")`  |
| `export`, never `module.exports`                  | `export default class User {}`           | `module.exports = User`               |
| Single export → `default`; multiple → named       | `export default class PaymentService {}` | mixing style inconsistently           |
