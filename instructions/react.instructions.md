---
description: React/JSX rules — functional components only, .tsx + typed props, local state placement, explicit prop passing, ~100-line component limit, Tailwind styling, useMemo, use-prefixed hooks, purity/idempotency, hooks-only-at-top-level, no mutating props/state. Apply to any .jsx/.tsx file. Do NOT use for Vue (see vue.instructions.md) or generic TS rules (see node-ts.instructions.md).
applyTo: "**/*.jsx, **/*.tsx"
---

# React Standards

## Use Functional Components

Always use function components. Never use class components.

```tsx
// ✅ Good
function UserCard({ name, email }: UserCardProps) {
  return (
    <div>
      <p>{name}</p>
      <p>{email}</p>
    </div>
  );
}

// ❌ Bad
class UserCard extends React.Component<UserCardProps> {
  render() {
    return <div>{this.props.name}</div>;
  }
}
```

---

## Use TypeScript — Files Must Use `.tsx` Extension

All React component files must be `.tsx`. Type all props with explicit interfaces or types.

```tsx
// ✅ Good — UserCard.tsx
interface UserCardProps {
  name: string;
  email: string;
  isActive?: boolean;
}

function UserCard({ name, email, isActive = false }: UserCardProps) {
  return <div className={isActive ? "active" : "inactive"}>{name}</div>;
}

// ❌ Bad — UserCard.jsx with no types
function UserCard({ name, email }) {
  return <div>{name}</div>;
}
```

---

## Keep State as Close as Possible to Where It Is Used

Do not lift state higher than necessary. Only move state up when it genuinely needs to be shared.

```tsx
// ✅ Good — modal state lives in the component that controls it
function OrderList() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  return (
    <>
      <button onClick={() => setIsModalOpen(true)}>New Order</button>
      {isModalOpen && (
        <CreateOrderModal onClose={() => setIsModalOpen(false)} />
      )}
    </>
  );
}

// ❌ Bad — modal state elevated to a parent that doesn't need it
function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  return (
    <OrderList isModalOpen={isModalOpen} setIsModalOpen={setIsModalOpen} />
  );
}
```

---

## Pass Props Explicitly

Avoid spreading unknown props or passing all state down as a blob. Be explicit about what each component needs.

```tsx
// ✅ Good
<UserCard name={user.name} email={user.email} />

// ❌ Bad
<UserCard {...user} />
<UserCard data={user} />
```

---

## Avoid Large Components — Split by Responsibility

If a component exceeds ~100 lines or handles multiple concerns, extract sub-components.

```tsx
// ✅ Good
function ProductPage() {
  return (
    <main>
      <ProductHeader />
      <ProductDetails />
      <ProductReviews />
    </main>
  );
}

// ❌ Bad — one massive component with hundreds of lines mixing header, details, and reviews
function ProductPage() {
  return <main>{/* 300 lines of mixed header, details, reviews JSX */}</main>;
}
```

---

## Use Tailwind for Styling

Apply styles via Tailwind utility classes. Do not use inline styles or CSS modules unless Tailwind cannot cover the use case.

```tsx
// ✅ Good
<button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded">
  Submit
</button>

// ❌ Bad
<button style={{ backgroundColor: "blue", color: "white", padding: "8px 16px" }}>
  Submit
</button>
```

---

## Use `useMemo` to Avoid Expensive Computations

Memoize derived values that are computationally expensive and depend on specific inputs.

```tsx
// ✅ Good
const sortedUsers = useMemo(
  () => [...users].sort((a, b) => a.name.localeCompare(b.name)),
  [users]
);

// ❌ Bad — re-sorts on every render regardless of whether users changed
const sortedUsers = [...users].sort((a, b) => a.name.localeCompare(b.name));
```

---

## Prefix Custom Hooks with `use`

All custom hooks must start with `use` to follow React conventions and ensure linting rules (react-hooks/rules-of-hooks) work correctly.

```ts
// ✅ Good
function useCurrentUser() {
  const [user, setUser] = useState<User | null>(null);
  // ...
  return user;
}

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

// ❌ Bad — missing `use` prefix; linting rules won't enforce hook constraints
function currentUser() {}
function debounce<T>(value: T, delay: number): T {
  return value;
}
```

---

## Write All Code in English

All identifiers, comments, strings, and documentation must be written in English. No exceptions — this ensures consistency across contributors and tooling.

```tsx
// ✅ Good
function UserProfile({ name, role }: UserProfileProps) {
  // Renders the profile header for a given user
  return (
    <h1>
      {name} — {role}
    </h1>
  );
}

// ❌ Bad
function PerfilUsuario({ nome, cargo }: PerfilUsuarioProps) {
  // Renderiza o cabeçalho do perfil
  return (
    <h1>
      {nome} — {cargo}
    </h1>
  );
}
```

---

## Purity in Components and Hooks

Components and hooks must be pure functions with respect to their inputs. Given the same props and state, they must always produce the same output with no observable side effects during render.

```tsx
// ✅ Good — output determined entirely by props
function PriceTag({ amount, currency }: PriceTagProps) {
  const formatted = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency
  }).format(amount);
  return <span>{formatted}</span>;
}

// ❌ Bad — reads external mutable state during render
let globalCounter = 0;

function Counter() {
  globalCounter += 1; // mutation during render — impure
  return <span>{globalCounter}</span>;
}
```

---

## Components Must Be Idempotent

Rendering a component multiple times with the same inputs must always produce the same result. React may invoke the render function more than once (e.g., Strict Mode).

```tsx
// ✅ Good — idempotent: same props → same output every call
function StatusBadge({ status }: { status: "active" | "inactive" }) {
  return (
    <span className={status === "active" ? "text-green-600" : "text-gray-400"}>
      {status}
    </span>
  );
}

// ❌ Bad — result changes on repeated calls due to external mutation
let rendered = false;

function OnceOnlyBanner() {
  if (rendered) return null;
  rendered = true; // breaks idempotency
  return <div>Welcome!</div>;
}
```

---

## Side Effects Must Run Outside of Render

All side effects (data fetching, subscriptions, DOM mutations, logging) must be placed inside `useEffect` or event handlers — never directly in the render body.

```tsx
// ✅ Good — fetch runs after render inside useEffect
function UserDetails({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]);

  return <div>{user?.name ?? "Loading..."}</div>;
}

// ❌ Bad — fetch triggered directly during render
function UserDetails({ userId }: { userId: string }) {
  fetchUser(userId); // side effect in render body
  return <div>...</div>;
}
```

---

## Props and State Are Immutable

Never mutate props or state directly. Always derive new values and use the state setter to trigger updates.

```tsx
// ✅ Good — create a new array instead of mutating
function TagList({ tags }: { tags: string[] }) {
  const [localTags, setLocalTags] = useState(tags);

  function addTag(tag: string) {
    setLocalTags((prev) => [...prev, tag]);
  }

  return (
    <ul>
      {localTags.map((t) => (
        <li key={t}>{t}</li>
      ))}
    </ul>
  );
}

// ❌ Bad — mutating state directly
function TagList({ tags }: { tags: string[] }) {
  const [localTags, setLocalTags] = useState(tags);

  function addTag(tag: string) {
    localTags.push(tag); // direct mutation — React won't re-render
    setLocalTags(localTags);
  }

  return (
    <ul>
      {localTags.map((t) => (
        <li key={t}>{t}</li>
      ))}
    </ul>
  );
}
```

---

## Return Values and Arguments to Hooks Are Immutable

Do not mutate objects or arrays returned by hooks or passed as arguments to hooks.

```tsx
// ✅ Good — spread into a new object before modifying
function useUserForm(initial: User) {
  const [form, setForm] = useState(initial);

  function updateEmail(email: string) {
    setForm((prev) => ({ ...prev, email }));
  }

  return { form, updateEmail };
}

// ❌ Bad — mutating the value returned by useState
function useUserForm(initial: User) {
  const [form, setForm] = useState(initial);

  function updateEmail(email: string) {
    form.email = email; // mutation of hook return value
    setForm(form);
  }

  return { form, updateEmail };
}
```

---

## Values Are Immutable After Being Passed to JSX

Once a value is passed to JSX, treat it as frozen. Mutating it after the fact produces unpredictable results.

```tsx
// ✅ Good — snapshot created before passing to JSX
function OrderSummary({ items }: { items: OrderItem[] }) {
  const snapshot = [...items]; // new array; original untouched
  return <ItemList items={snapshot} />;
}

// ❌ Bad — mutating an array that was just passed to a child
function OrderSummary({ items }: { items: OrderItem[] }) {
  return (
    <>
      <ItemList items={items} />
      {items.push({ id: "x", name: "Extra" })} {/* mutation after JSX */}
    </>
  );
}
```

---

## Never Call Component Functions Directly

Always let React call components via JSX. Calling them as plain functions bypasses the component lifecycle, hooks, and reconciliation.

```tsx
// ✅ Good — React controls the call
function Page() {
  return <UserCard name="Alice" />;
}

// ❌ Bad — bypasses React's rendering pipeline
function Page() {
  return UserCard({ name: "Alice" }); // direct function call
}
```

---

## Never Pass Around Hooks as Regular Values

Hooks must be called directly inside a component or custom hook. They cannot be stored in variables, passed as props, or returned from non-hook functions.

```tsx
// ✅ Good — hook called directly inside the component
function SearchBar() {
  const [query, setQuery] = useState("");
  return <input value={query} onChange={(e) => setQuery(e.target.value)} />;
}

// ❌ Bad — hook stored and passed as a value
function createStateHook() {
  return useState(""); // hook called outside a component/hook context
}

function SearchBar({ stateHook }: { stateHook: ReturnType<typeof useState> }) {
  const [query, setQuery] = stateHook; // hooks passed as props
  return <input value={query} />;
}
```

---

## Only Call Hooks at the Top Level

Never call hooks inside loops, conditionals, or nested functions. This ensures hook call order is stable across renders.

```tsx
// ✅ Good — hooks at the top level of the component
function NotificationBell({ userId }: { userId: string }) {
  const [count, setCount] = useState(0);
  const user = useUser(userId);

  return <bell count={count} />;
}

// ❌ Bad — hook inside a conditional
function NotificationBell({ userId }: { userId: string }) {
  if (!userId) return null;
  const user = useUser(userId); // hook called after an early return — breaks hook order
  return <bell />;
}
```

---

## Only Call Hooks from React Functions

Hooks must only be called from function components or other custom hooks — never from plain utility functions, class methods, or event callbacks.

```tsx
// ✅ Good — hook inside a custom hook
function useAuthenticatedUser() {
  const { token } = useAuth();
  const user = useFetchUser(token);
  return user;
}

// ❌ Bad — hook called from a plain utility function
function getUser() {
  const user = useCurrentUser(); // invalid — not a component or hook
  return user;
}
```

---
