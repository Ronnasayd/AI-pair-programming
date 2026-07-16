---
description: Python code standards — English identifiers, snake_case/PascalCase, type hints on public functions, no mutable defaults, f-strings, context managers, specific exceptions (no bare except), dataclasses, Enum over magic values, exception messages with offending value. Apply to any .py file. Do NOT use for docstring format (see pydocs.instructions.md).
applyTo: "**/*.py"
---

# Python Code Standards

## Quick rules

| Rule                                                  | ✅ Good                                                      | ❌ Bad                                                     |
| ----------------------------------------------------- | ------------------------------------------------------------ | ---------------------------------------------------------- |
| English identifiers/comments/docstrings/logs          | `is_user_logged_in = False`                                  | `esta_logado = False`                                      |
| `snake_case` vars/funcs, `PascalCase` classes (PEP 8) | `class UserRepository: def find_by_id(self)`                 | `class user_repository: def FindById(self)`                |
| Type hints on all public functions; avoid `Any`       | `def calculate_discount(price: float, rate: float) -> float` | `def calculate_discount(price, rate)`                      |
| f-strings for formatting                              | `f"User {user.name} logged in"`                              | `"User %s logged in" % user.name`                          |
| Context managers for resources                        | `with open("data.csv") as f: ...`                            | `f = open(...); f.close()`                                 |
| Specific exceptions, never bare `except`              | `except ValueError as exc:`                                  | `except: pass`                                             |
| `@dataclass` for plain data containers                | `@dataclass class Point: x: float; y: float`                 | hand-written `__init__`/`__eq__` boilerplate               |
| Comprehensions only for simple expressions            | `[u.id for u in users if u.is_active]`                       | nested multi-condition comprehension — use a loop/function |
| One class per file for non-trivial classes            | `models/user.py` → `class User`                              | `models/entities.py` → `User`, `Order`, `Payment` together |
| `Enum` instead of magic strings/numbers               | `OrderStatus.PAID`                                           | `order.status == "paid"`                                   |

## Nuance — needs the shape, not just the rule

**Never mutable default arguments** — defaults evaluate once at def time:

```python
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

**Guard clauses over nested `if`** — max 2 indentation levels:

```python
def process_order(order: "Order") -> None:
    if order is None:
        return
    if not order.is_paid:
        return
    ship(order)
```

**Docstrings on all public functions/classes** — describe intent, not implementation. Non-trivial functions document `Args`/`Returns`/`Raises` (Google style); skip for trivial one-liners:

```python
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
```

**Exceptions must state received value + expected shape**, so failures are debuggable without a stack-trace dive:

```python
if not isinstance(payload, dict):
    raise TypeError(f"Expected dict payload, got {type(payload).__name__}: {payload!r}")
```
