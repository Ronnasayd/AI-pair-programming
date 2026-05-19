---
description: Rules for code generation and modification tasks.
applyTo: "**/*.ts, **/*.js, **/*.py, **/*.java, **/*.go, **/*.css, **/*.cpp, **/*.c, **/*.vue, **/*.jsx, **/*.tsx"
---

## Context

This file applies exclusively to code generation and modification tasks.
Code review, auditing, or diff inspection are handled separately — do not perform those unless explicitly requested.

## Rules

- **Integrate new code compatibly with the existing codebase; follow established patterns and boundaries.**

  ```ts
  // ❌ BAD: Inventing a new fetch wrapper when the codebase already uses apiClient
  const res = await fetch("/api/users");

  // ✅ GOOD: Reuse the existing abstraction
  const res = await apiClient.get("/users");
  ```

- **Avoid breaking backward compatibility unless required; document migration steps if you do.**

  ```ts
  // ❌ BAD: Renaming a public function used in 30 places without notice
  export function fetchUser(id: string) { ... }  // was getUser()

  // ✅ GOOD: Keep the old name as an alias and note the deprecation
  /** @deprecated Use fetchUser instead */
  export const getUser = fetchUser;
  ```

- **Include automated tests, examples, or validation instructions whenever technically feasible.**

  ```ts
  // ❌ BAD: Shipping a new formatCurrency() utility with no tests
  export function formatCurrency(amount: number) { ... }

  // ✅ GOOD: Add at least a basic test alongside
  it('formats USD correctly', () => {
    expect(formatCurrency(1000)).toBe('$1,000.00');
  });
  ```

- **Include clear documentation when introducing significant new components, endpoints, or public interfaces.**

  ```ts
  // ❌ BAD: Exporting a new hook with no JSDoc
  export function usePayment() { ... }

  // ✅ GOOD: Document purpose, params, and return value
  /**
   * Handles payment submission and tracks status.
   * @returns { submit, status, error }
   */
  export function usePayment() { ... }
  ```

## Anti-Patterns

- **Do not use confusing, generic, or abbreviated identifiers.**

  ```ts
  // ❌ BAD
  const x = users.filter((u) => u.a > 0);

  // ✅ GOOD
  const activeUsers = users.filter((user) => user.age > 0);
  ```

- **Do not duplicate code; prefer reuse through functions, modules, or abstractions.**

  ```ts
  // ❌ BAD: Same validation logic copy-pasted in three components
  if (!email.includes("@")) throw new Error("Invalid email");

  // ✅ GOOD: Extract once
  import { validateEmail } from "@/utils/validation";
  validateEmail(email);
  ```

- **Do not use magic values; use named constants or enums.**

  ```ts
  // ❌ BAD
  if (user.role === 3) { ... }

  // ✅ GOOD
  const UserRole = { Admin: 3 } as const;
  if (user.role === UserRole.Admin) { ... }
  ```

- **Do not mix multiple responsibilities in a single function, class, or module.**

  ```ts
  // ❌ BAD: One function fetches data, formats it, and sends an email
  async function processOrder(id: string) {
    const order = await db.find(id);
    const formatted = formatOrder(order);
    await mailer.send(formatted);
  }

  // ✅ GOOD: Split into focused units
  const order = await fetchOrder(id);
  const formatted = formatOrder(order);
  await sendOrderConfirmation(formatted);
  ```

- **Do not ignore performance in critical paths (inefficient loops, heavy queries, blocking calls).**

  ```ts
  // ❌ BAD: N+1 query inside a loop
  for (const user of users) {
    user.orders = await db.orders.findMany({ where: { userId: user.id } });
  }

  // ✅ GOOD: Batch fetch
  const orders = await db.orders.findMany({
    where: { userId: { in: userIds } }
  });
  ```

- **Do not leave dead code, commented-out code, or unused functions.**

  ```ts
  // ❌ BAD
  // const oldHandler = () => { ... };
  export function unusedHelper() { ... }

  // ✅ GOOD: Delete unused code; use version control to recover it if needed
  ```

- **Do not catch overly broad exceptions without justification; prefer specific exception types.**

  ```ts
  // ❌ BAD
  try { ... } catch (e) { console.log(e); }

  // ✅ GOOD
  try { ... } catch (e) {
    if (e instanceof NetworkError) handleNetworkError(e);
    else throw e;
  }
  ```

- **Avoid circular dependencies and excessive coupling; respect dependency inversion.**

  ```ts
  // ❌ BAD: services/user.ts imports from services/order.ts which imports services/user.ts
  import { getUser } from "./user"; // inside order.ts — circular

  // ✅ GOOD: Extract shared types/interfaces to a shared layer both can import
  import type { UserId } from "@/types/user";
  ```

- **Avoid hardcoded configs or absolute paths; do not create environment inconsistencies.**

  ```ts
  // ❌ BAD
  const API_URL = "http://localhost:3000/api";

  // ✅ GOOD
  const API_URL = process.env.NEXT_PUBLIC_API_URL;
  ```

- **Avoid outdated cryptographic algorithms or security practices.**

  ```ts
  // ❌ BAD: MD5 for password hashing
  const hash = crypto.createHash("md5").update(password).digest("hex");

  // ✅ GOOD: Use bcrypt or argon2
  const hash = await bcrypt.hash(password, 12);
  ```
