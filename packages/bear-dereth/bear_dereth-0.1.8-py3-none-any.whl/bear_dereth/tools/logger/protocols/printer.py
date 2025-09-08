"""BasePrinter protocol definition."""

import inspect as py_inspect
from pathlib import Path
from typing import IO, Any, Protocol, TextIO

from bear_dereth.constants.enums.log_level import LogLevel
from bear_dereth.tools.logger.config import CustomTheme, LoggerConfig
from bear_dereth.tools.logger.protocols.handler import Handler
from bear_dereth.tools.logger.protocols.handler_manager import BaseHandlerManager
from bear_dereth.tools.logger.simple._error import ErrorLogger


class BasePrinter[T: TextIO | IO](BaseHandlerManager, Protocol):
    """A protocol for a base printer with config, theme, and user API."""

    name: str | None
    config: LoggerConfig
    level: LogLevel
    theme: CustomTheme
    handlers: list[Handler[Any]]
    err: ErrorLogger  # Backup logger for error handling if the main logger fails
    start_no_handlers: bool

    def __init__(
        self,
        name: str | None = None,
        config: LoggerConfig | None = None,
        custom_theme: CustomTheme | None = None,  # noqa: ARG002
        file: T | None = None,  # noqa: ARG002
        level: int | str | LogLevel = LogLevel.DEBUG,
        error_logger: ErrorLogger | None = None,
        start_no_handlers: bool = False,
    ) -> None:
        """A constructor for the BasePrinter protocol."""
        self.name = name
        self.config = config or LoggerConfig()
        self.level = LogLevel.get(level, default=LogLevel.DEBUG)
        self.err = error_logger or ErrorLogger()
        self.start_no_handlers = start_no_handlers

    def get_level(self) -> LogLevel:
        """Get the current logging level."""
        return self.level

    def set_level(self, level: str | int | LogLevel) -> None:
        """Set the current logging level."""
        self.level = LogLevel.get(level, self.level)

    def on_error_callback(self, *msg, name: str, error: Exception) -> None:
        """Handle errors from handlers. Override to customize error handling."""
        stack: list[py_inspect.FrameInfo] = py_inspect.stack()
        stack_value = 0
        ignored_functions: set[str] = {"_wrapped_print", "on_error_callback", "emit", "_emit_to_handlers"}
        while stack_value < len(stack) and stack[stack_value].function in ignored_functions:
            stack_value += 1

        caller_frame: py_inspect.FrameInfo = stack[stack_value]
        caller_function: str = caller_frame.function
        filename: str = Path(caller_frame.filename).name
        line_number: int = caller_frame.lineno
        code_context: list[str] | None = caller_frame.code_context
        index: int | None = caller_frame.index

        self.err(
            *msg,
            related_name=name,
            caller_function=caller_function,
            code_context=code_context[index].strip() if code_context and index is not None else "<unknown>",
            filename=filename,
            line_number=line_number,
            error_class=type(error).__name__,
            error_text=f"'{error!s}'",
        )

    def print(self, msg: object, style: str, **kwargs) -> None:
        """A method to print a message with a specific style directly to the console."""

    def log(self, msg: object, *args, **kwargs) -> None:
        """A method to log a message via console.log()."""
