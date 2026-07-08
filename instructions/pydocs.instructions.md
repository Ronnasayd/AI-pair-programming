---
description: Google-style docstring rules for Python — summary line, Args (no type duplication), Returns, Raises, class Attributes. Apply when writing/reviewing any .py function, class, or module. Test files (test_*.py, *_test.py) exempt except module docstring. Do NOT use for JS/TS JSDoc (see jsdocs.instructions.md).
applyTo: "**/*.py"
---

## Docstring Requirements

Every `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, and module **must** have a Google-style docstring that includes:

| Requirement       | Rule                                                       | Detail                                                                                                           |
| ----------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Summary line      | Required                                                   | Non-empty sentence describing what the function/class/module does, in imperative mood.                           |
| `Args` section    | Required when function has params (excluding `self`/`cls`) | One entry per parameter, including `**kwargs`/`*args`. Each entry: `name: description`.                          |
| Arg type          | Not repeated in docstring                                  | Type comes from the type hint in the signature, not the docstring — do not duplicate it in `Args`.               |
| `Returns` section | Required when function has explicit non-`None` `return`    | Describes what is returned. Omit for functions returning `None` or with no `return` statement.                   |
| `Raises` section  | Required when function explicitly raises                   | One entry per exception type raised, with the condition that triggers it: `ExceptionType: condition`.            |
| Class docstring   | Required                                                   | Describes the class's responsibility. `Attributes` section required if the class has public instance attributes. |

### Examples

```python
# ✅ Good — all required sections present, no type duplication
def find_by_id(user_id: int) -> "User | None":
    """Find a user by their unique identifier.

    Args:
        user_id: The ID of the user to retrieve.

    Returns:
        The matching User entity, or None if not found.
    """
    ...

# ✅ Good — Raises documented
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

# ✅ Good — void function, Returns omitted
def send_welcome_email(email: str) -> None:
    """Send a welcome email to the provided address.

    Args:
        email: Recipient email address.
    """
    ...

# ✅ Good — class docstring with Attributes
class OrderProcessor:
    """Processes orders through payment and fulfillment.

    Attributes:
        gateway: Payment gateway used to charge orders.
        retries: Number of retry attempts on transient failures.
    """

    def __init__(self, gateway: "PaymentGateway", retries: int = 3) -> None:
        self.gateway = gateway
        self.retries = retries

# ❌ Bad — missing summary and Args
def find_by_id(user_id: int) -> "User | None":
    """"""
    ...

# ❌ Bad — Args present but type duplicated, no description
def find_by_id(user_id: int) -> "User | None":
    """Find user by ID.

    Args:
        user_id (int): user_id
    """
    ...
```

> **Test files are exempt** (`test_*.py`, `*_test.py`): docstring requirements are turned off for test files, except for module-level docstrings describing what the test suite covers.
