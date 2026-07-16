---
description: React/JSX rules — functional components only, .tsx + typed props, local state placement, explicit prop passing, ~100-line component limit, Tailwind styling, useMemo, use-prefixed hooks, purity/idempotency, hooks-only-at-top-level, no mutating props/state. Apply to any .jsx/.tsx file. Do NOT use for Vue (see vue.instructions.md) or generic TS rules (see node-ts.instructions.md).
applyTo: "**/*.jsx, **/*.tsx"
---

# React Standards

## Quick rules

| Rule                                                           | ✅ Good                                              | ❌ Bad                                               |
| -------------------------------------------------------------- | ---------------------------------------------------- | ---------------------------------------------------- |
| Functional components only, never class                        | `function UserCard(props) {...}`                     | `class UserCard extends React.Component`             |
| `.tsx` files, typed props via interface                        | `interface UserCardProps {...}`                      | `.jsx` with untyped destructured props               |
| State stays local to where it's used; don't lift unless shared | modal state lives in `OrderList`                     | modal state lifted to `App` unnecessarily            |
| Pass props explicitly                                          | `<UserCard name={user.name} />`                      | `<UserCard {...user} />`, `<UserCard data={user} />` |
| Split components over ~100 lines by responsibility             | `<ProductHeader/><ProductDetails/><ProductReviews/>` | one 300-line component mixing all three              |
| Tailwind for styling, not inline/CSS modules                   | `className="bg-blue-600 px-4 py-2"`                  | `style={{ backgroundColor: "blue" }}`                |
| `useMemo` for expensive derived values                         | `useMemo(() => sort(users), [users])`                | re-sorting on every render unconditionally           |
| Custom hooks prefixed `use`                                    | `function useCurrentUser()`                          | `function currentUser()`                             |
| All code/comments in English                                   | —                                                    | —                                                    |
| Never call component functions directly — always via JSX       | `<UserCard name="Alice" />`                          | `UserCard({ name: "Alice" })`                        |
| Never pass hooks around as values                              | call `useState` directly inside the component        | `return useState("")` from a helper, pass as prop    |

## Rules of Hooks — call order must stay stable

**Only at the top level** — never in loops/conditionals/nested functions:

```tsx
// ❌ hook called after an early return — breaks call order
function NotificationBell({ userId }) {
  if (!userId) return null;
  const user = useUser(userId);
}
```

**Only from React functions** — components or other custom hooks, never plain utilities/class methods/callbacks:

```tsx
// ❌ invalid — not a component or hook
function getUser() {
  return useCurrentUser();
}
```

## Purity & immutability — needs the shape, not just the rule

**Pure render** — same props/state → same output, no side effects during render:

```tsx
// ❌ mutation during render
let globalCounter = 0;
function Counter() {
  globalCounter += 1;
  return <span>{globalCounter}</span>;
}
```

**Idempotent** — React may invoke render more than once (Strict Mode); repeated calls with same inputs must match:

```tsx
// ❌ result changes on repeated calls
let rendered = false;
function OnceOnlyBanner() {
  if (rendered) return null;
  rendered = true;
  return <div>Welcome!</div>;
}
```

**Side effects only in `useEffect` or event handlers**, never in the render body:

```tsx
// ❌ fetch triggered directly during render
function UserDetails({ userId }) {
  fetchUser(userId);
  return <div>...</div>;
}
```

**Never mutate props/state directly** — derive new values, use the setter:

```tsx
// ❌ direct mutation — React won't re-render
function addTag(tag: string) {
  localTags.push(tag);
  setLocalTags(localTags);
}
// ✅
function addTag(tag: string) {
  setLocalTags((prev) => [...prev, tag]);
}
```

**Never mutate hook return values/arguments**:

```tsx
// ❌ mutating the value returned by useState
form.email = email;
setForm(form);
// ✅
setForm((prev) => ({ ...prev, email }));
```

**Treat values as frozen once passed to JSX**:

```tsx
// ❌ mutating an array right after passing it to a child
<ItemList items={items} />;
{
  items.push({ id: "x", name: "Extra" });
}
// ✅ snapshot before passing
const snapshot = [...items];
<ItemList items={snapshot} />;
```
