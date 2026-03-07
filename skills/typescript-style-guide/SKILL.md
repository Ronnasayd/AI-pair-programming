---
name: typescript-style-guide
description: "Conventions and best practices for writing maintainable TypeScript code based on the Google TypeScript Style Guide. Use this skill when writing new TypeScript modules or services, refactoring TypeScript code to improve readability and maintainability, enforcing consistent naming, typing, and formatting conventions, designing strongly typed APIs, interfaces, and classes, avoiding unsafe patterns such as `any`, prototype modification, or loose equality, structuring large TypeScript codebases with predictable patterns, and implementing safe and maintainable code in Node.js or browser TypeScript projects. Emphasizes strong typing, clear naming conventions, strict equality usage, minimal visibility exposure, avoiding dangerous JavaScript features, and consistent formatting. Reference: https://google.github.io/styleguide/tsguide.html"
---

# Skill: TypeScript (Google Style Guide)

## Overview

This skill follows the Google TypeScript Style Guide and provides conventions and best practices for writing consistent, maintainable TypeScript code.

Reference: https://google.github.io/styleguide/tsguide.html

---

# 1. Source File Basics

## Encoding

- Use **UTF-8** for all source files.

## Whitespace

- Only ASCII space (`0x20`) is allowed outside of line terminators.
- Other whitespace must be escaped in strings.

## Escape Sequences

Prefer standard escape sequences:

```

' " \ \b \f \n \r \t \v

```

Avoid numeric escapes unless necessary.

## Non-ASCII Characters

- Prefer the real Unicode character when readable.

Example:

```ts
const units = "μs";
```

---

# 2. Variables

## Use `const` and `let`

- Prefer `const`.
- Use `let` only if reassignment is required.
- **Never use `var`.**

```ts
const foo = value;
let counter = 0;
```

## One variable per declaration

Correct:

```ts
let a = 1;
let b = 2;
```

Incorrect:

```ts
let a = 1,
  b = 2;
```

---

# 3. Classes

## Visibility

- Restrict symbol visibility as much as possible.
- Avoid explicit `public` modifier unless needed.

```ts
class Foo {
  bar = new Bar();
}
```

Avoid:

```ts
class Foo {
  public bar = new Bar();
}
```

## Avoid Prototype Manipulation

Do not modify prototypes directly.

Bad:

```ts
SomeClass.prototype.newMethod = function () {};
```

---

# 4. Functions

## Types of functions

- Function declaration
- Function expression
- Arrow function

Example:

```ts
function add(a: number, b: number): number {
  return a + b;
}

const addArrow = (a: number, b: number) => a + b;
```

---

# 5. Equality

Always use **strict equality**.

Correct:

```ts
if (a === b) {
}
```

Avoid:

```ts
if (a == b) {
}
```

Exception:

```ts
if (value == null) {
  // matches null or undefined
}
```

---

# 6. Type Safety

## Avoid `any`

Prefer:

- interfaces
- generics
- `unknown`

Example:

```ts
interface User {
  name: string;
  email: string;
}
```

Instead of:

```ts
let user: any;
```

---

# 7. Naming Conventions

## Identifiers

Allowed characters:

- letters
- numbers
- underscores
- `$` (rare)

## Naming style

| Type      | Style            |
| --------- | ---------------- |
| variables | `lowerCamelCase` |
| functions | `lowerCamelCase` |
| classes   | `UpperCamelCase` |
| constants | `CONSTANT_CASE`  |

Example:

```ts
const MAX_RETRIES = 5;

class UserService {}

function fetchUser() {}
```

---

# 8. Constants

Use `CONSTANT_CASE` for immutable values.

Example:

```ts
const UNIT_SUFFIXES = {
  milliseconds: "ms",
  seconds: "s",
};
```

Static constant example:

```ts
class MathUtils {
  static readonly MAX = 100;
}
```

---

# 9. Dangerous Features to Avoid

Do not use:

- `eval()`
- `new Function()`
- modifying built-in objects
- non-standard ECMAScript features

Bad:

```ts
eval("alert('hello')");
```

---

# 10. Type Assertions

Avoid unnecessary assertions:

```ts
value as SomeType;
```

Use only when absolutely required.

---

# 11. Compiler Directives

Avoid:

```ts
@ts-ignore
@ts-expect-error
@ts-nocheck
```

They hide real issues.

---

# 12. Comments

## Class Comments

Explain:

- purpose
- usage
- constraints

Example:

```ts
/**
 * Represents a coffee brewing machine.
 */
class CoffeeMachine {}
```

## Method Comments

Start with a verb phrase.

Example:

```ts
/**
 * Starts the brewing process.
 */
brew(amountLitres: number) {}
```

## Parameter Comments

Use when meaning is unclear:

```ts
startMachine(/* shouldHeatWater= */ true, /* cups= */ 2);
```

---

# 13. Consistency

If a style decision isn't defined:

1. Follow the existing file style.
2. Follow the directory style.
3. Default to Google style.

Consistency is more important than preference.

---

# Key Principles

1. Avoid patterns that cause bugs.
2. Maintain consistency across projects.
3. Optimize for long-term maintainability.
4. Prefer rules that can be automated.

---

# Recommended Tooling

Typical tooling stack:

- TypeScript compiler
- ESLint
- Prettier
- Strict compiler flags

---

# Summary

This guide emphasizes:

- strong typing
- strict equality
- clear naming
- avoiding unsafe language features
- consistent code style
