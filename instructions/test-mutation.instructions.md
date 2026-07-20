---
description: Mutation-testing rules — how to write assertions that survive Stryker mutants (exact values not shape, isolate && / || operands, explicit default/fallback tests, boundary comparisons, no skipped specs). Apply to any *.test.ts/js or *.spec.ts/js file. Complements test.instructions.md (general test structure) — use this one when chasing mutation-score gaps.
applyTo: "**/*.test.ts,**/*.test.js,**/*.spec.ts,**/*.spec.js"
---

# Mutation-Survivor-Proof Tests

Goal: assertions that die when a mutant changes the code, not just when the code is fully broken.

## 1. Assert value, not just shape/status

`toHaveBeenCalled()` / `toMatchObject({ statusCode })` alone isn't enough — check literal content.

- Error assertions check the literal `.message`, not just `statusCode`/type.
- Every I/O mock (`fetch`, repository, use case, adapter) has one test asserting exact args via `toHaveBeenCalledWith(...)` — URL, headers, body, method.

```ts
// bad — mutant in the message survives
await expect(fn()).rejects.toMatchObject({ statusCode: 502 });

// good
await expect(fn()).rejects.toMatchObject({
  statusCode: 502,
  message: "Failed to discover Keycloak OIDC configuration: ..."
});
```

## 2. Isolate each operand of `&&`/`||`

Failing all operands at once doesn't kill a mutant that flips only 1.

- `if (!a || !b || !c)` → N operands = N tests, each isolating 1 failing operand (rest valid).
- Sequential calls (`fetch` #1, #2, ...) need a test breaking each call individually, not just the last.

```ts
// bad — tests all 3 together
delete process.env.A; delete process.env.B; delete process.env.C;

// good — 3 separate tests
it("throws when only A missing", () => { ... });
it("throws when only B missing", () => { ... });
it("throws when only C missing", () => { ... });
```

## 3. Defaults/fallbacks need an explicit test

`?? true`, `?? ""`, `a || b` counts as tested only if test **omits** the value and compares against the literal default — not just echoing what the mock returned.

```ts
// bad — only echoes the mock, doesn't prove the default
mockRepo.save.mockImplementation((u) => u);
const result = await useCase.execute(input);
expect(result.mfaEnabled).toBe(input.mfaEnabled); // doesn't test the default

// good — omit field, compare against literal
const useCaseInput = { ...input, mfaEnabled: undefined };
await useCase.execute(useCaseInput);
expect(mockRepo.save).toHaveBeenCalledWith(
  expect.objectContaining({ mfaEnabled: false })
);
```

## 4. Exact boundary in time/numeric comparisons

Testing only "before"/"after" won't kill `>` → `>=` mutants.

- Every `<`, `>`, `<=`, `>=` on time or numbers needs a test at the exact boundary value.
- Computed values (`Date.now() + TTL`): tolerate a few ms in comparison, but the `+`/`-` computation itself still needs an assertion the operator-swap mutant can't survive.

```ts
it("returns true when expiresAt equals now exactly", () => {
  const now = new Date();
  jest.useFakeTimers().setSystemTime(now);
  const entity = Entity.reconstruct("id", { ...props, expiresAt: now });
  expect(entity.isExpired()).toBe(true); // or false — define the business rule
});
```
