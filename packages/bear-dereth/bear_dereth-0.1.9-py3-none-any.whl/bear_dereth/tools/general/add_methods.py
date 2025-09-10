"""A module for adding rich comparison methods to classes based on an attribute."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from types import NotImplementedType  # noqa: TC003
from typing import Any, cast

from bear_dereth.tools.logger.config import LoggerTheme

PRIMITIVE_TYPES: tuple[type[str], type[int], type[float], type[bool]] = (str, int, float, bool)


def add_comparison_methods[T](attribute: str) -> Callable[[type[T]], type[T]]:
    """Class decorator that adds rich comparison methods based on a specific attribute.

    This decorator adds __eq__, __ne__, __lt__, __gt__, __le__, __ge__, and __hash__ methods
    to a class, all of which delegate to the specified attribute. This allows instances
    of the decorated class to be compared with each other, as well as with primitive values
    that the attribute can be compared with.

    Args:
        attribute: Name of the instance attribute to use for comparisons

    Returns:
        Class decorator function that adds comparison methods to a class

    Example:
        @add_comparison_methods('name')
        class Person:
            def __init__(self, name):
                self.name = name
    """

    def decorator(cls: type[T]) -> type[T]:
        def extract_comparable_value(self: object, other: Any) -> NotImplementedType | Any:  # noqa: ARG001
            """Helper to extract the comparable value from the other object."""
            if isinstance(other, PRIMITIVE_TYPES):
                return other

            if hasattr(other, attribute):
                return getattr(other, attribute)

            return NotImplemented

        def eq(self: object, other: Any) -> NotImplementedType | bool:
            """Equal comparison method (__eq__)."""
            other_val: NotImplementedType | Any = extract_comparable_value(self, other)
            if other_val is NotImplemented:
                return NotImplemented
            return getattr(self, attribute) == other_val

        def ne(self: object, other: Any) -> NotImplementedType | bool:
            """Not equal comparison method (__ne__)."""
            other_val: NotImplementedType | Any = extract_comparable_value(self, other)
            if other_val is NotImplemented:
                return NotImplemented
            return getattr(self, attribute) != other_val

        def lt(self: object, other: Any) -> NotImplementedType | bool:
            """Less than comparison method (__lt__)."""
            other_val: NotImplementedType | Any = extract_comparable_value(self, other)
            if other_val is NotImplemented:
                return NotImplemented
            return getattr(self, attribute) < other_val

        def gt(self: object, other: Any) -> NotImplementedType | bool:
            """Greater than comparison method (__gt__)."""
            other_val: NotImplementedType | Any = extract_comparable_value(self, other)
            if other_val is NotImplemented:
                return NotImplemented
            return getattr(self, attribute) > other_val

        def le(self: object, other: Any) -> NotImplementedType | bool:
            """Less than or equal comparison method (__le__)."""
            other_val: NotImplementedType | Any = extract_comparable_value(self, other)
            if other_val is NotImplemented:
                return NotImplemented
            return getattr(self, attribute) <= other_val

        def ge(self: object, other: Any) -> NotImplementedType | bool:
            """Greater than or equal comparison method (__ge__)."""
            other_val: NotImplementedType | Any = extract_comparable_value(self, other)
            if other_val is NotImplemented:
                return NotImplemented
            return getattr(self, attribute) >= other_val

        def hash_method(self: object) -> int:
            """Generate hash based on the attribute used for equality."""
            return hash(getattr(self, attribute))

        cls.__eq__ = eq
        cls.__ne__ = ne
        cls.__lt__ = lt  # type: ignore[assignment]
        cls.__gt__ = gt  # type: ignore[assignment]
        cls.__le__ = le  # type: ignore[assignment]
        cls.__ge__ = ge  # type: ignore[assignment]
        cls.__hash__ = hash_method

        return cls

    return decorator


def init_factory(cls: type, from_config: Mapping | Callable, create_method: Callable) -> type:
    """Helper to modify __init__ to add methods from a config callable."""
    original_init: Callable[..., Any] = cls.__init__
    callable_config: Callable = cast("Callable", from_config)

    def new_init(self: object, *args, **kwargs) -> None:
        original_init(self, *args, **kwargs)
        config: Any = callable_config(self)
        for name, data in config.items():
            if not hasattr(self, name):
                setattr(self, name, create_method(name, data).__get__(self, cls))

            cls.__init__ = new_init

    return cls


def dynamic_methods(
    from_config: Mapping | Callable,
    using_method: str,
    with_pattern: Callable,
) -> Callable[[type], type]:
    """Class decorator that adds methods dynamically based on a configuration source."""

    def decorator(cls: type) -> type:
        def create_method(name: str, data: Any) -> Callable:
            def method(self: object, *args, **kwargs) -> Any:
                pattern_kwargs: Any = with_pattern(name, data)
                base_method: Any = getattr(self, using_method)
                return base_method(*args, **{**pattern_kwargs, **kwargs})

            method.__name__ = name
            method.__doc__ = f"Auto-generated method for {name}."
            return method

        if isinstance(from_config, Mapping):
            for name, data in from_config.items():
                if not hasattr(cls, name):
                    setattr(cls, name, create_method(name, data))
        elif callable(from_config):
            cls = init_factory(cls, from_config, create_method)

        return cls

    return decorator


if __name__ == "__main__":

    @dynamic_methods(
        from_config=LoggerTheme().model_dump(),
        using_method="_wrapped_print",
        with_pattern=lambda name, data: {"style": name, "level": name.upper()},
    )
    class MyLogger:
        """A simple logger class to demonstrate dynamic method addition."""

        def _wrapped_print(self, msg: object, style: str, level: str, **kwargs) -> None:
            print(f"[{level}] ({style}): {msg}", **kwargs)

        def __getattr__(self, name: str) -> Any:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    logger = MyLogger()
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.exception("This is an exception message.")
