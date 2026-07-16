---
description: General code style — naming (camelCase/PascalCase/verb-first funcs), no magic numbers, max 2 nesting levels, max 3 params, no switch/case, const/let, 30-line function limit, anti-patterns (duplication, dead code, broad catch, circular deps, hardcoded config, weak crypto). Apply to any code edit/creation in JS/TS/Java/Go/CSS/C/C++/Vue/JSX/TSX. Do NOT use for docs, HTTP API shape, or test files (see test.instructions.md).
applyTo: "**/*.ts, **/*.js, **/*.py, **/*.java, **/*.go, **/*.css, **/*.cpp, **/*.c, **/*.vue, **/*.jsx, **/*.tsx"
---

# Code Standards

All code, comments, identifiers, and docs must be in **English**.

## Naming & style — quick rules

| Rule                              | ✅ Good                        | ❌ Bad                    |
| --------------------------------- | ------------------------------ | ------------------------- |
| camelCase for vars/funcs          | `const maxRetries = 3`         | `const MaxRetries = 3`    |
| PascalCase for classes/interfaces | `class UserRepository {}`      | `class userRepository {}` |
| Functions start with a verb       | `getUserById(id)`              | `userData(id)`            |
| No magic numbers                  | `if (n >= MAX_LOGIN_ATTEMPTS)` | `if (n >= 5)`             |
| `const`/`let` only, never `var`   | `let retryCount = 0`           | `var retryCount = 0`      |

## Nesting, params, branching, size — need the shape, not just the rule

**Max 2 levels of if/else nesting** — use early returns:

```ts
function processOrder(order: Order): void {
  if (!order) return;
  if (!order.isPaid) return;
  shipOrder(order);
}
```

**Max 3 params** — beyond that, use an object:

```ts
function createUser({ name, email, role }: CreateUserParams): User {}
```

**Avoid switch/case** — prefer object maps or polymorphism:

```ts
const statusLabels: Record<OrderStatus, string> = {
  pending: "Pending",
  paid: "Paid"
};
const label = statusLabels[status];
```

**Max 30 lines per function** — extract sub-responsibilities:

```ts
function processPayment(payment: Payment): PaymentResult {
  validatePayment(payment);
  const charged = chargeCard(payment);
  return buildPaymentResult(charged);
}
```

## Rules

| Rule                                                               | ❌ Bad                                        | ✅ Good                                                    |
| ------------------------------------------------------------------ | --------------------------------------------- | ---------------------------------------------------------- |
| Integrate compatibly with existing codebase/patterns               | `fetch("/api/users")` when `apiClient` exists | `apiClient.get("/users")`                                  |
| Avoid breaking backward compat; document migrations if unavoidable | rename `getUser` used in 30 places, silently  | keep `/** @deprecated */ export const getUser = fetchUser` |
| Add tests/examples when feasible                                   | ship `formatCurrency()` untested              | `expect(formatCurrency(1000)).toBe('$1,000.00')`           |
| Document significant new public interfaces                         | export `usePayment()` with no JSDoc           | add JSDoc: purpose, params, return                         |

## Anti-Patterns

| Anti-pattern                           | ❌ Bad                                                     | ✅ Good                                                           |
| -------------------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------- |
| Confusing/abbreviated identifiers      | `users.filter(u => u.a > 0)`                               | `users.filter(user => user.age > 0)`                              |
| Duplicated logic                       | same email check copy-pasted 3x                            | `import { validateEmail } from "@/utils/validation"`              |
| Magic values                           | `if (user.role === 3)`                                     | `if (user.role === UserRole.Admin)`                               |
| Mixed responsibilities in one function | fetch + format + email in one func                         | split into `fetchOrder` → `formatOrder` → `sendOrderConfirmation` |
| Ignoring perf in hot paths             | N+1 query in a loop                                        | batch fetch with `where: { userId: { in: userIds } }`             |
| Dead/commented-out code                | `// const oldHandler = ...` left in                        | delete; rely on git history                                       |
| Overly broad catch                     | `catch (e) { console.log(e) }`                             | `catch (e) { if (e instanceof NetworkError) ...; else throw e }`  |
| Circular deps / excessive coupling     | `services/user.ts` ↔ `services/order.ts` import each other | extract shared types to a shared layer                            |
| Hardcoded config/absolute paths        | `const API_URL = "http://localhost:3000/api"`              | `const API_URL = process.env.NEXT_PUBLIC_API_URL`                 |
| Outdated crypto                        | `crypto.createHash("md5")` for passwords                   | `bcrypt.hash(password, 12)`                                       |
