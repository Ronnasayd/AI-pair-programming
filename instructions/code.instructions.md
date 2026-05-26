---
description: Rules for code generation and modification tasks.
applyTo: "**/*.ts, **/*.js, **/*.py, **/*.java, **/*.go, **/*.css, **/*.cpp, **/*.c, **/*.vue, **/*.jsx, **/*.tsx"
---

# Code Standards

## Language

All code, comments, variable names, and documentation must be written in **English**.

```ts
// ✅ Good
const userAge = 25;
// ❌ Bad
const idadeUsuario = 25;
```

---

## Naming Conventions

### camelCase — variables, methods, functions

```ts
// ✅ Good
const maxRetries = 3;
function fetchUserData(userId: string) {}
const handleSubmit = () => {};

// ❌ Bad
const MaxRetries = 3;
function FetchUserData(UserId: string) {}
```

### PascalCase — classes and interfaces

```ts
// ✅ Good
class UserRepository {}
interface PaymentGateway {}

// ❌ Bad
class userRepository {}
interface payment_gateway {}
```

---

## Methods and Functions Must Start with a Verb

```ts
// ✅ Good
function getUserById(id: string): User {}
function validateEmail(email: string): boolean {}
function sendWelcomeEmail(user: User): void {}

// ❌ Bad
function userData(id: string): User {}
function emailCheck(email: string): boolean {}
```

---

## No Magic Numbers — use named constants

```ts
// ✅ Good
const MAX_LOGIN_ATTEMPTS = 5;
if (loginAttempts >= MAX_LOGIN_ATTEMPTS) {
  lockAccount();
}

// ❌ Bad
if (loginAttempts >= 5) {
  lockAccount();
}
```

---

## Avoid Nesting More Than 2 if/else Levels

Deeply nested conditionals harm readability. Use early returns or extract functions.

```ts
// ✅ Good
function processOrder(order: Order): void {
  if (!order) return;
  if (!order.isPaid) return;
  shipOrder(order);
}

// ❌ Bad
function processOrder(order: Order): void {
  if (order) {
    if (order.isPaid) {
      if (order.items.length > 0) {
        shipOrder(order);
      }
    }
  }
}
```

---

## Avoid More Than 3 Parameters

When more arguments are needed, use an object parameter.

```ts
// ✅ Good
function createUser({ name, email, role }: CreateUserParams): User {}

// ❌ Bad
function createUser(
  name: string,
  email: string,
  role: string,
  age: number
): User {}
```

---

## Avoid switch/case — prefer object maps or polymorphism

```ts
// ✅ Good
const statusLabels: Record<OrderStatus, string> = {
  pending: "Pending",
  paid: "Paid",
  shipped: "Shipped"
};
const label = statusLabels[status];

// ❌ Bad
switch (status) {
  case "pending":
    return "Pending";
  case "paid":
    return "Paid";
  case "shipped":
    return "Shipped";
}
```

---

## Prefer `const` and `let` — never use `var`

```ts
// ✅ Good
const BASE_URL = "https://api.example.com";
let retryCount = 0;

// ❌ Bad
var BASE_URL = "https://api.example.com";
var retryCount = 0;
```

---

## Keep Methods and Functions Below 30 Lines

If a function exceeds 30 lines, extract sub-responsibilities into smaller functions.

```ts
// ✅ Good
function processPayment(payment: Payment): PaymentResult {
  validatePayment(payment);
  const charged = chargeCard(payment);
  return buildPaymentResult(charged);
}

function validatePayment(payment: Payment): void {
  if (!payment.amount || payment.amount <= 0) throw new Error("Invalid amount");
  if (!payment.cardToken) throw new Error("Missing card token");
}

// ❌ Bad — everything crammed into one long function
function processPayment(payment: Payment): PaymentResult {
  if (!payment.amount || payment.amount <= 0) throw new Error("Invalid amount");
  if (!payment.cardToken) throw new Error("Missing card token");
  // ... 25 more lines of mixed logic
}
```

---

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
