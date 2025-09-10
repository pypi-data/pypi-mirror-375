"""Files to handle conditional imports of dependency injector components."""

from importlib.util import find_spec

HAS_DEPENDENCY_INJECTOR: bool = find_spec("dependency_injector") is not None

if HAS_DEPENDENCY_INJECTOR:
    from dependency_injector.containers import DeclarativeContainer  # type: ignore[import]
    from dependency_injector.wiring import Provide, inject  # type: ignore[import]

    __all__ = ["HAS_DEPENDENCY_INJECTOR", "DeclarativeContainer", "Provide", "inject"]

else:
    from bear_dereth.tools.di.__container import DeclarativeContainer
    from bear_dereth.tools.di.__wiring import Provide, Provider, inject, parse_params
    from bear_dereth.tools.di._resources import Resource, Singleton

    __all__ = [
        "HAS_DEPENDENCY_INJECTOR",
        "DeclarativeContainer",
        "Provide",
        "Provider",
        "Resource",
        "Singleton",
        "inject",
        "parse_params",
    ]
