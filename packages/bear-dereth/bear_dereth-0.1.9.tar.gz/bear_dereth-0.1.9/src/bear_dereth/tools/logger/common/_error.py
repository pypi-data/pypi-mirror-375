from collections.abc import Callable
from typing import IO, TextIO

from bear_dereth.tools.general.textio_utility import stderr
from bear_dereth.tools.stringing.flatten_data import flatten


class ErrorLogger:
    """A simple error logger that writes messages to a specified TextIO stream."""

    def __init__(
        self,
        file_callback: Callable[[], TextIO | IO[str]] = stderr,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Initialize the ErrorLogger.

        Args:
            file_callback: A callable that returns a TextIO object to write to. Defaults to stderr.
            sep: Separator between values. Defaults to a single space.
            end: String appended after the last value. Defaults to a newline.
            flush: Whether to forcibly flush the stream. Defaults to False.
        """
        self.file_callback: Callable[[], TextIO | IO[str]] = file_callback
        self.sep: str = sep
        self.end: str = end
        self.flush: bool = flush

    @property
    def file(self) -> TextIO | IO[str]:
        """Get the current output file."""
        return self.file_callback()

    @file.setter
    def file(self, file_callback: Callable[[], TextIO | IO[str]]) -> None:
        """Set the output file callback."""
        self.file_callback = file_callback

    def print_kwargs(self, **kwargs) -> str:
        """Format keyword arguments into a string.

        Args:
            **kwargs: Keyword arguments to format.

        Returns:
            A formatted string of key=value pairs.
        """
        return " ".join(f"{key}={value}" for key, value in kwargs.items())

    def flatten_data(self, values: dict | list, prefix: str = "") -> str:
        """Flatten nested tuples in the values.

        Args:
            values: A dictionary or list of values to flatten.
            prefix: An optional prefix to prepend to each flattened value.

        Returns:
            A single flattened string with values separated by the instance's sep.
        """
        return flatten(values, prefix, combine=True)

    def __call__(
        self,
        *values: object,
        sep: str | None = None,
        end: str | None = None,
        flush: bool | None = None,
        file: TextIO | IO[str] | None = None,
        **kwargs,
    ) -> None:
        """Print the error message to the specified file with optional formatting.

        Args:
            *values: Values to be printed.
            sep: Separator between values. Defaults to the instance's sep.
            end: String appended after the last value. Defaults to the instance's end.
            flush: Whether to forcibly flush the stream. Defaults to the instance's flush.
            file: The file to write to. Defaults to the instance's file.
        """
        sep = sep if sep is not None else self.sep
        end = end if end is not None else self.end
        flush = flush if flush is not None else self.flush
        file = file if file is not None else self.file
        kwargs_str: str = self.print_kwargs(**kwargs) if kwargs else ""
        values = (*values, kwargs_str) if kwargs_str else values
        print(values, end=end, sep=sep, file=file, flush=flush)
