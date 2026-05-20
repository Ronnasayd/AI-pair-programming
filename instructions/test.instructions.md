---
description: Test Standards
applyTo: "**/*.test.ts,**/*.test.js"
---

# Test Standards

## Cover Code with Tests

Every non-trivial function, service, and component must have corresponding tests. Aim for high coverage on business logic.

---

## Keep Tests Independent

Each test must be able to run in isolation. Tests must not depend on the order of execution or shared mutable state.

```ts
// ✅ Good — each test sets up its own data
it("should return the user by id", async () => {
  const user = await createUser({ name: "Alice" });
  const result = await getUserById(user.id);
  expect(result.name).toBe("Alice");
});

// ❌ Bad — relies on a user created by a previous test
it("should return the user by id", async () => {
  const result = await getUserById(globalUserId); // depends on external state
  expect(result.name).toBe("Alice");
});
```

---

## Use Given/When/Then or Arrange/Act/Assert

Structure each test with a clear setup, action, and assertion phase. Use comments to separate phases when it improves clarity.

```ts
// ✅ Good — Arrange / Act / Assert
it("should apply a 10% discount for premium users", () => {
  // Arrange
  const user = buildUser({ isPremium: true });
  const order = buildOrder({ total: 100 });

  // Act
  const discounted = applyDiscount(order, user);

  // Assert
  expect(discounted.total).toBe(90);
});

// ✅ Good — Given / When / Then (comment style)
it("given a premium user, when discount is applied, then total is reduced by 10%", () => {
  const user = buildUser({ isPremium: true });
  const order = buildOrder({ total: 100 });
  const result = applyDiscount(order, user);
  expect(result.total).toBe(90);
});
```

---

## Mock the Date When Behavior Depends on It

Never rely on the real system clock in tests. Always control time explicitly.

```ts
// ✅ Good
it("should mark the subscription as expired", () => {
  jest.useFakeTimers().setSystemTime(new Date("2026-01-01"));
  const subscription = buildSubscription({ expiresAt: new Date("2025-12-31") });
  expect(isExpired(subscription)).toBe(true);
  jest.useRealTimers();
});

// ❌ Bad — result depends on when the test runs
it("should mark the subscription as expired", () => {
  const subscription = buildSubscription({ expiresAt: new Date("2020-01-01") });
  expect(isExpired(subscription)).toBe(true); // may fail in any year before 2020
});
```

---

## Keep Test Cases Under 100 Lines

If a test exceeds 100 lines, extract helpers or split into smaller focused tests.

---

## Make Tests Clear and Objective

Test names should describe the scenario and expected outcome. Avoid generic names.

```ts
// ✅ Good
it("should throw an error when the email is already registered");
it("should return an empty array when no orders exist for the user");
it("should format the date as DD/MM/YYYY");

// ❌ Bad
it("test email");
it("works correctly");
it("order test 2");
```

---

## Use `beforeEach` for Similar Scenarios

When multiple tests share the same setup, consolidate it in `beforeEach`.

```ts
// ✅ Good
describe("UserService", () => {
  let userService: UserService;

  beforeEach(() => {
    userService = new UserService(mockRepository);
  });

  it("should create a user", async () => {
    const user = await userService.create({
      name: "Alice",
      email: "alice@example.com"
    });
    expect(user.id).toBeDefined();
  });

  it("should throw when email is already taken", async () => {
    await expect(
      userService.create({ name: "Bob", email: "existing@example.com" })
    ).rejects.toThrow("Email already in use");
  });
});
```

---

## Use `afterEach` to Clean Up Resources

Use `afterEach` to close database connections, reset mocks, or clear side effects after each test.

```ts
// ✅ Good
describe("OrderRepository", () => {
  let db: Database;

  beforeEach(async () => {
    db = await connectTestDatabase();
  });

  afterEach(async () => {
    await db.clear();
    await db.close();
  });

  it("should persist a new order", async () => {
    const repo = new OrderRepository(db);
    const order = await repo.save(buildOrder());
    expect(order.id).toBeDefined();
  });
});

// ❌ Bad — leaving connections open between tests causes leaks and flaky tests
```
