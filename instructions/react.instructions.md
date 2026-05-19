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

## Use TypeScript — files must use `.tsx` extension

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
// ✅ Good — modal open state lives in the component that controls it
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

## Avoid Large Components — split by responsibility

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

// ❌ Bad — re-sorts on every render
const sortedUsers = [...users].sort((a, b) => a.name.localeCompare(b.name));
```

---

## Prefix Custom Hooks with `use`

All custom hooks must start with `use` to follow React conventions and enable linting rules.

```ts
// ✅ Good
function useCurrentUser() {
  const [user, setUser] = useState<User | null>(null);
  // ...
  return user;
}

function useDebounce<T>(value: T, delay: number): T {
  // ...
}

// ❌ Bad
function currentUser() {}
function debounce<T>(value: T, delay: number): T {}
```
