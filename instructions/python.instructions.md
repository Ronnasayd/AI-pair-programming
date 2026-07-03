---
description: Python Code Standards.
applyTo: "**/*.py"
---

# Python Code Standards

## All Code Must Be Written in English

Names, comments, docstrings, and log messages must be written in English.

```python
# ✅ Good
is_user_logged_in = False


def handle_submit():
    pass

# ❌ Bad
esta_logado = False


def enviar_formulario():
    pass
```

---

## Use `snake_case` for Variables and Functions, `PascalCase` for Classes

Follow PEP 8 naming conventions consistently.

```python
# ✅ Good
class UserRepository:
    def find_by_id(self, user_id: int) -> "User":
        ...

# ❌ Bad
class user_repository:
    def FindById(self, UserId: int) -> "User":
        ...
```

---

## Use Type Hints on All Public Functions

Every public function/method must declare parameter and return types. Avoid `Any` unless truly unavoidable.

```python
# ✅ Good
def calculate_discount(price: float, rate: float) -> float:
    return price * (1 - rate)

# ❌ Bad
def calculate_discount(price, rate):
    return price * (1 - rate)
```

---

## Never Use Mutable Default Arguments

Default arguments are evaluated once at function definition time. Use `None` and initialize inside the function.

```python
# ✅ Good
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items

# ❌ Bad
def add_item(item: str, items: list[str] = []) -> list[str]:
    items.append(item)
    return items
```

---

## Use f-strings for String Formatting

Prefer f-strings over `%` formatting or `.format()` for readability.

```python
# ✅ Good
message = f"User {user.name} logged in at {timestamp}"

# ❌ Bad
message = "User %s logged in at %s" % (user.name, timestamp)
```

---

## Use Context Managers for Resource Handling

Always use `with` for files, locks, connections, and other resources that must be closed/released.

```python
# ✅ Good
with open("data.csv") as f:
    rows = f.readlines()

# ❌ Bad
f = open("data.csv")
rows = f.readlines()
f.close()
```

---

## Catch Specific Exceptions, Never Bare `except`

Catch the narrowest exception type that can occur. Bare `except:` hides bugs and swallows `KeyboardInterrupt`/`SystemExit`.

```python
# ✅ Good
try:
    value = int(raw_input)
except ValueError as exc:
    raise ValueError(f"Expected integer, got {raw_input!r}") from exc

# ❌ Bad
try:
    value = int(raw_input)
except:
    pass
```

---

## Use Dataclasses for Simple Data Containers

Prefer `@dataclass` over hand-written `__init__`/`__eq__`/`__repr__` boilerplate for plain data objects.

```python
# ✅ Good
from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float

# ❌ Bad
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
```

---

## Use List/Dict Comprehensions Only for Simple Expressions

Comprehensions should stay short and readable. Refactor complex logic into a loop or a named function.

```python
# ✅ Good
active_ids = [user.id for user in users if user.is_active]

# ❌ Bad
result = [
    transform(x)
    for x in items
    if x.is_valid and not x.is_archived
    for y in x.children
    if y.matches(filter_criteria(x))
]
```

---

## Docstrings on All Public Functions and Classes

Public functions, classes, and modules must have a docstring describing intent, not implementation. Non-trivial functions must document `Args`, `Returns`, and `Raises` (Google style) — skip these sections only for trivial one-liners where the signature already says it all.

```python
# ✅ Good
def calculate_discount(price: float, rate: float) -> float:
    """Apply a percentage discount to a price.

    Args:
        price: Original price before discount.
        rate: Discount rate between 0 and 1.

    Returns:
        Discounted price.

    Raises:
        ValueError: If rate is not between 0 and 1.
    """
    if not 0 <= rate <= 1:
        raise ValueError(f"Expected rate in [0, 1], got {rate}")
    return price * (1 - rate)

# ❌ Bad
def calculate_discount(price: float, rate: float) -> float:
    """Apply discount."""
    if not 0 <= rate <= 1:
        raise ValueError(f"Expected rate in [0, 1], got {rate}")
    return price * (1 - rate)
```

---

## Avoid Deep Nesting — Use Early Returns / Guard Clauses

Prefer guard clauses over nested `if` blocks. Keep indentation to a maximum of 2 levels.

```python
# ✅ Good
def process_order(order: "Order") -> None:
    if order is None:
        return
    if not order.is_paid:
        return
    ship(order)

# ❌ Bad
def process_order(order: "Order") -> None:
    if order is not None:
        if order.is_paid:
            ship(order)
```

---

## One Class per File for Non-Trivial Classes

Keep modules focused. A file that defines a substantial, independently reusable class should carry that class's name.

```
# ✅ Good
models/
  user.py        # class User
  order.py       # class Order

# ❌ Bad
models/
  entities.py    # class User, class Order, class Payment all in one file
```

---

## Use `Enum` Instead of Magic Strings/Numbers

Represent a fixed set of related constants with `Enum` rather than raw literals scattered through the code.

```python
# ✅ Good
from enum import Enum


class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"


if order.status == OrderStatus.PAID:
    ship(order)

# ❌ Bad
if order.status == "paid":
    ship(order)
```

---

## Raise Exceptions with the Offending Value and Expected Shape

Exception messages must state what was received and what was expected, so failures are debuggable without a stack-trace dive.

```python
# ✅ Good
if not isinstance(payload, dict):
    raise TypeError(f"Expected dict payload, got {type(payload).__name__}: {payload!r}")

# ❌ Bad
if not isinstance(payload, dict):
    raise TypeError("Invalid payload")
```
