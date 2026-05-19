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
