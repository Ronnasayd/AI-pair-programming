---
name: golang-style-guide
description: "Conventions and best practices for writing readable, maintainable Go code based on the Google Go Style Guide. Use this skill when: Writing new Go packages, services, or command-line tools. Refactoring Go code to improve clarity and maintainability. Enforcing idiomatic Go naming, formatting, and structure. Designing APIs and libraries for long-term maintainability. Avoiding unnecessary abstraction or complexity in Go programs."
---

# Skill: Go (Google Style Guide)

## Overview

This skill implements conventions from the Google Go Style Guide.

The goal is to produce Go code that is:

- Clear and easy to read
- Simple and idiomatic
- Concise with a high signal-to-noise ratio
- Maintainable over time
- Consistent with the broader Go ecosystem

Readable code is prioritized over clever or complex solutions.

---

# Core Principles

## 1. Clarity

Code must be easy to understand.

Guidelines:

- Prefer self-describing names instead of explanatory comments.
- Comments should explain **why**, not **what**.
- Avoid clever tricks or surprising patterns.
- Make the flow of values and decisions obvious.
- Ensure APIs clearly express their intent.

Readable code should allow a new reader to understand the purpose quickly.

---

## 2. Simplicity

Use the simplest approach that solves the problem.

Prefer:

1. Core language features
2. Standard library tools
3. External dependencies only when necessary

Avoid:

- Unnecessary abstraction
- Over-engineering
- Premature optimization

Complexity is acceptable only when justified (e.g., performance).

When complexity exists, document it clearly.

---

## 3. Concision

Code should have a high **signal-to-noise ratio**.

Reduce unnecessary:

- Repetition
- Boilerplate
- Indirection
- Verbose naming

Use common Go idioms so readers recognize patterns quickly.

Example:

```go
if err := doSomething(); err != nil {
    return err
}
```

---

## 4. Maintainability

Code should be easy to modify correctly.

Maintainable code:

- Has clear structure
- Avoids tight coupling
- Uses abstractions only when useful
- Includes tests with meaningful failures
- Provides APIs that evolve gracefully

Remember:

Code is **read and modified far more often than it is written**.

---

# Formatting

## Always Use `gofmt`

All Go source code must be formatted with:

```
gofmt
```

Never manually enforce formatting styles that conflict with gofmt.

Generated code should also be formatted.

---

# Naming

## MixedCaps

Use camel case instead of underscores.

Examples:

```go
MaxLength
maxLength
userID
parseConfig
```

Avoid:

```
max_length
MAX_LENGTH
user_id
```

---

## Naming Guidelines

Good names:

- Reflect intent
- Avoid redundancy
- Use context effectively
- Are shorter when scope is small

Examples:

Good:

```go
func Parse(r io.Reader)
```

Bad:

```go
func ParseReaderInputStream(reader io.Reader)
```

---

# Line Length

There is **no fixed line length** in Go.

If a line becomes too long:

- Refactor the code
- Introduce intermediate variables

Avoid splitting lines unnecessarily.

Do not split:

- Function signatures awkwardly
- Long strings (e.g. URLs)

---

# Comments

Comments should:

- Explain **why the code exists**
- Document non-obvious decisions
- Clarify complex behavior

Avoid comments that restate the code.

Bad:

```go
// Increment i
i++
```

Better:

```go
// Retry counter to prevent infinite loop
i++
```

---

# Error Handling

Use idiomatic Go error handling patterns.

Preferred style:

```go
if err != nil {
    return err
}
```

Avoid:

- Deep nesting
- Ignoring errors
- Clever error abstractions

Error messages should be informative.

---

# Abstraction Guidelines

Only introduce abstraction when it adds real value.

Prefer:

- Concrete types
- Small interfaces
- Explicit behavior

Avoid:

- Large generic interfaces
- Overuse of dependency injection frameworks
- Java-style architecture patterns

---

# Testing

Maintain a comprehensive test suite.

Tests should:

- Be deterministic
- Provide clear failure messages
- Focus on behavior

Use table-driven tests when appropriate.

Example:

```go
tests := []struct{
    input string
    want  string
}{
    {"a", "A"},
    {"b", "B"},
}
```

---

# Consistency

Consistency within a project is important.

If the style guide is silent:

- Follow existing local conventions
- Maintain consistency within the package

Avoid introducing new patterns unnecessarily.

---

# Summary

Priorities for Go code readability:

1. Clarity
2. Simplicity
3. Concision
4. Maintainability
5. Consistency

Prefer code that is straightforward, idiomatic, and easy to maintain.
