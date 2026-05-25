---
description: Rules for code generation and modification tasks.
applyTo: "**/*.ts, **/*.js, **/*.jsx, **/*.tsx"
---

## JSDoc Requirements

Every `FunctionDeclaration`, `MethodDefinition`, and `FunctionExpression` **must** have a JSDoc block that includes:

| Requirement                | Rule                                | Detail                                                                                                                                                      |
| -------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Block description          | `jsdoc/require-description`         | A non-empty sentence describing what the function does.                                                                                                     |
| `@param` tag per parameter | `jsdoc/require-param`               | One tag for each parameter, including destructured members (e.g. `root0.field`). Auto-fixer is **disabled** — write them manually.                          |
| `@param` name              | `jsdoc/require-param-name`          | Each `@param` must include the parameter name.                                                                                                              |
| `@param` description       | `jsdoc/require-param-description`   | Each `@param` must include a human-readable description.                                                                                                    |
| `@returns` tag             | `jsdoc/require-returns`             | Required when the function has an explicit `return` statement. Async functions that return `Promise<void>` are **exempt** (`forceReturnsWithAsync: false`). |
| `@returns` description     | `jsdoc/require-returns-description` | The `@returns` tag must describe what is returned.                                                                                                          |

### Examples

```ts
// ✅ Good — all required tags present
/**
 * Finds a user by their unique identifier.
 * @param id - The UUID of the user to retrieve.
 * @returns The matching User entity, or null if not found.
 */
async findById(id: string): Promise<User | null> { ... }

// ✅ Good — destructured params documented with dot notation
/**
 * Creates a new order for the given tenant.
 * @param root0 - Input object.
 * @param root0.tenantId - Tenant that owns the order.
 * @param root0.items - Line items to include in the order.
 * @returns The persisted Order entity.
 */
async createOrder({ tenantId, items }: CreateOrderInput): Promise<Order> { ... }

// ✅ Good — void async method, @returns omitted
/**
 * Sends a welcome email to the provided address.
 * @param email - Recipient email address.
 */
async sendWelcomeEmail(email: string): Promise<void> { ... }

// ❌ Bad — missing description and @param tags
/**
 *
 */
async findById(id: string): Promise<User | null> { ... }

// ❌ Bad — @param present but missing description
/**
 * Finds a user by ID.
 * @param id
 * @returns The user.
 */
async findById(id: string): Promise<User | null> { ... }
```

> **Test files are exempt** (`**/*.spec.ts`, `**/*.test.ts`): `jsdoc/require-jsdoc`, `jsdoc/require-param`, `jsdoc/require-returns`, and `jsdoc/require-description` are all turned off for test files.''''
