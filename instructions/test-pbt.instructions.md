---
description: Property-based testing rules (fast-check).
applyTo: "**/*.test.ts,**/*.test.js,**/*.spec.ts,**/*.spec.js"
---

# Property-Based Testing

Goal: assert invariants that hold for _any_ valid input, not just hand-picked examples. Use `fast-check` (`fc.assert(fc.property(...))`) alongside example-based tests — PBT complements, doesn't replace them.

## 1. When to reach for PBT

Pure functions with a clear invariant: serialization round-trips, sort/parse/encode, math, normalization, idempotent operations. Skip PBT for functions dominated by I/O or side effects — property test the pure core instead.

```ts
// good candidate — pure, invertible
it("round-trips any valid order through encode/decode", () => {
  fc.assert(
    fc.property(orderArbitrary(), (order) => {
      expect(decodeOrder(encodeOrder(order))).toEqual(order);
    })
  );
});
```

## 2. Build arbitraries from fast-check primitives, not ad-hoc randomness

Shrinking only works when values come from `fc.*` combinators (`fc.record`, `fc.array`, `fc.integer`, `fc.oneof`, ...). Hand-rolled `Math.random()` generators can't shrink and hide the minimal failing case.

```ts
// bad — opaque, doesn't shrink
const randomOrder = () => ({ id: Math.random(), total: Math.random() * 1000 });

// good — composable, shrinkable
const orderArbitrary = () =>
  fc.record({
    id: fc.uuid(),
    total: fc.float({ min: 0, max: 100_000, noNaN: true }),
    items: fc.array(itemArbitrary(), { minLength: 1 })
  });
```

## 3. State the real invariant, not a tautology

`expect(fn(x)).toBeDefined()` passes for almost anything and kills nothing. The property must encode a fact a broken implementation would violate.

```ts
// bad — trivially true, catches nothing
fc.assert(
  fc.property(fc.integer(), (n) => {
    expect(sort([n])).toBeDefined();
  })
);

// good — actual invariant: output is sorted and same length
fc.assert(
  fc.property(fc.array(fc.integer()), (arr) => {
    const sorted = sort(arr);
    expect(sorted).toHaveLength(arr.length);
    for (let i = 1; i < sorted.length; i++) {
      expect(sorted[i - 1]).toBeLessThanOrEqual(sorted[i]);
    }
  })
);
```

Common invariant shapes:

- **Round-trip**: `decode(encode(x)) === x`
- **Idempotence**: `f(f(x)) === f(x)`
- **Metamorphic**: relate output of related inputs (e.g. `sort(arr).length === arr.length`, `reverse(reverse(arr)) === arr`)
- **Oracle comparison**: same result as a trusted reference/naive implementation
- **Invariant preservation**: a precondition on input implies a postcondition on output

## 4. Narrow input space with `fc.pre`, not a broadened arbitrary that hides bugs

If only some generated values are valid, filter with `fc.pre(condition)` inside the property (or `.filter()` on the arbitrary) instead of loosening assertions.

```ts
fc.assert(
  fc.property(fc.integer(), fc.integer(), (a, b) => {
    fc.pre(b !== 0); // divisor can't be 0
    expect(divide(a, b) * b).toBeCloseTo(a);
  })
);
```

## 5. On a counterexample: fix the code first, the arbitrary last

fast-check shrinks failures to a minimal reproducer and prints it (`Counterexample: [...]`, `Seed: ...`). Reproduce with the printed seed before touching anything:

```ts
fc.assert(fc.property(...), { seed: 1234567, path: "12:3:0" });
```

Narrowing the arbitrary to make a real failure disappear hides a genuine bug — only narrow when the counterexample is actually invalid input (fix the arbitrary) or truly out of scope (add `fc.pre`).

## 6. Bound runs and pin flaky failures

Default 100 runs is usually enough for unit-level properties; bump `{ numRuns: 1000 }` only for critical invariants (money, security, parsers) where the cost is justified. Once a bug is fixed, keep the failing seed as a regression example test — PBT finding a bug once doesn't guarantee the same input is regenerated later.

```ts
fc.assert(
  fc.property(pathArbitrary(), (p) => {
    expect(() => resolvePath(p)).not.toThrow();
  }),
  { numRuns: 1000 }
);
```
