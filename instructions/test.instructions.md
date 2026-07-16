---
description: General test-writing rules — independent tests, Arrange/Act/Assert or Given/When/Then, mock the clock for time-dependent logic, <100-line test cases, descriptive names, beforeEach/afterEach usage. Apply to any *.test.ts/js or *.spec.ts/js file. Do NOT use for backend integration/SQLite specifics (see test-typescript-node-backend.instructions.md).
applyTo: "**/*.test.ts,**/*.test.js,**/*.spec.ts,**/*.spec.js"
---

# Test Standards

Every non-trivial function/service/component needs tests, aiming for high coverage on business logic. Keep test cases under 100 lines — extract helpers or split when exceeded.

## Quick rules

| Rule                                                | ✅ Good                                                        | ❌ Bad                                              |
| --------------------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------- |
| Independent tests — no shared/order-dependent state | each test creates its own data via `createUser(...)`           | `getUserById(globalUserId)` depends on a prior test |
| Descriptive names (scenario + expected outcome)     | `"should throw an error when the email is already registered"` | `"test email"`, `"works correctly"`                 |

## Nuance — needs the shape, not just the rule

**Arrange/Act/Assert or Given/When/Then** — clear setup/action/assertion phases:

```ts
it("should apply a 10% discount for premium users", () => {
  // Arrange
  const user = buildUser({ isPremium: true });
  const order = buildOrder({ total: 100 });
  // Act
  const discounted = applyDiscount(order, user);
  // Assert
  expect(discounted.total).toBe(90);
});
```

**Mock the clock** for any time-dependent behavior — never rely on the real system clock:

```ts
it("should mark the subscription as expired", () => {
  jest.useFakeTimers().setSystemTime(new Date("2026-01-01"));
  const subscription = buildSubscription({ expiresAt: new Date("2025-12-31") });
  expect(isExpired(subscription)).toBe(true);
  jest.useRealTimers();
});
```

**`beforeEach` for shared setup** across tests in a `describe`:

```ts
describe("UserService", () => {
  let userService: UserService;
  beforeEach(() => {
    userService = new UserService(mockRepository);
  });
  it("should create a user", async () => { ... });
});
```

**`afterEach` to clean up** — close DB connections, reset mocks, clear side effects. Leaving connections open between tests causes leaks and flaky tests:

```ts
describe("OrderRepository", () => {
  let db: Database;
  beforeEach(async () => {
    db = await connectTestDatabase();
  });
  afterEach(async () => {
    await db.clear();
    await db.close();
  });
});
```
