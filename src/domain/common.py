from collections.abc import Hashable
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any, Self, cast

TIMEZONE = timezone.utc


def now() -> datetime:
    return datetime.now(TIMEZONE)


class BaseEntity[T: Hashable]:
    """
    Base class for domain entities, defined by a unique identity (`id_`).
    - `id_`: Identity that remains constant throughout the entity's lifecycle.
    - Entities are mutable, but are compared solely by their `id_`.
    """

    def __new__(cls, *_args: Any, **_kwargs: Any) -> Self:
        if cls is BaseEntity:
            raise TypeError("BaseEntity cannot be instantiated directly.")
        return object.__new__(cls)

    def __init__(self, *, id_: T) -> None:
        self.id_ = id_

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevents modifying the `id_` after it's set."""
        if name == "id_" and getattr(self, "id_", None) is not None:
            raise AttributeError("Changing entity ID is not permitted.")
        object.__setattr__(self, name, value)

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other) and cast(Self, other).id_ == self.id_

    def __hash__(self) -> int:
        return hash((type(self), self.id_))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id_={self.id_!r})"


@dataclass(frozen=True, slots=True, repr=False)
class BaseValueObject:
    """
    Base class for immutable value objects (VO).
    Defined by instance attributes only; these must be immutable.
    For simple type tagging, consider `typing.NewType` instead of subclassing.

    Subclasses must be declared with `@dataclass(frozen=True, slots=True, repr=False)`.
    `__repr__` includes only fields with `repr=True`; if none, '<hidden>' is shown.
    """

    def __new__(cls, *_args: Any, **_kwargs: Any) -> Self:
        if cls is BaseValueObject:
            raise TypeError("BaseValueObject cannot be instantiated directly.")
        if not fields(cls):
            raise TypeError(f"{cls.__name__} must have at least one field!")
        return object.__new__(cls)

    def __post_init__(self) -> None:
        """Hook for ensuring invariants."""

    def __repr__(self) -> str:
        items = [f for f in fields(self) if f.repr]
        if not items:
            value = "<hidden>"
        elif len(items) == 1:
            value = f"{getattr(self, items[0].name)!r}"
        else:
            value = ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in items)
        return f"{type(self).__name__}({value})"
