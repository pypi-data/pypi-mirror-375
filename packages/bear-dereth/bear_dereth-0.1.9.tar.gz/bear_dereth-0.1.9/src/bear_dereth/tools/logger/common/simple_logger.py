"""Simple logger implementation with log levels and timestamped output."""

import traceback
from typing import IO, TextIO

from bear_epoch_time import EpochTimestamp

from bear_dereth.constants.enums.log_level import LogLevel
from bear_dereth.tools.general.textio_utility import NULL_FILE
from bear_dereth.tools.stringing.flatten_data import flatten


class SimpleLogger[T: TextIO | IO]:
    """A simple logger that writes messages to stdout, stderr, or StringIO with a timestamp."""

    def __init__(self, file: T = NULL_FILE, level: str | int | LogLevel = "DEBUG") -> None:
        """Initialize the logger with a minimum log level and output file.

        Args:
            level (str | int | LogLevel): The minimum log level for messages to be logged.
            file (TextIO): The file-like object to write log messages to. Defaults to STDERR.
        """
        self.level: LogLevel = LogLevel.get(level, default=LogLevel.DEBUG)
        self.file: T = file
        self.buffer: list[str] = []

    def set_file(self, file: T) -> None:
        """Set the output file for the logger."""
        self.file = file

    def print(self, msg: object, end: str = "\n") -> None:
        """Print the message to the specified file with an optional end character."""
        print(msg, end=end, file=self.file)

    def log(self, level: LogLevel, msg: object, *args, **kwargs) -> None:
        """Log a message at the specified level."""
        if level.value >= self.level.value:
            timestamp: str = EpochTimestamp.now().to_string()
            end: str = kwargs.pop("end", "\n")
            try:
                self.buffer.append(f"[{timestamp}] {level.text}: {msg}")
                if args:
                    self.buffer.append(flatten(list(args), prefix="args", combine=True))
                if kwargs:
                    self.buffer.append(flatten(kwargs, prefix="kwargs", combine=True))
                self.print(f"{end}".join(self.buffer))
            except Exception as e:
                self.print(f"[{timestamp}] {level.value}: {msg} - Error: {e}")
            finally:
                self.buffer.clear()

    def verbose(self, msg: object, *args, **kwargs) -> None:
        """Alias for debug level logging."""
        self.log(LogLevel.VERBOSE, msg, *args, **kwargs)

    def debug(self, msg: object, *args, **kwargs) -> None:
        """Log a debug message."""
        self.log(LogLevel.DEBUG, msg, *args, **kwargs)

    def info(self, msg: object, *args, **kwargs) -> None:
        """Log an info message."""
        self.log(LogLevel.INFO, msg, *args, **kwargs)

    def warning(self, msg: object, *args, **kwargs) -> None:
        """Log a warning message."""
        self.log(LogLevel.WARNING, msg, *args, **kwargs)

    def error(self, msg: object, *args, **kwargs) -> None:
        """Log an error message."""
        self.log(LogLevel.ERROR, msg, *args, **kwargs)

    def success(self, msg: object, *args, **kwargs) -> None:
        """Log a success message."""
        self.log(LogLevel.SUCCESS, msg, *args, **kwargs)

    def failure(self, msg: object, *args, **kwargs) -> None:
        """Log a failure message."""
        self.log(LogLevel.FAILURE, msg, *args, **kwargs)

    def exception(self, msg: object, *args, **kwargs) -> None:
        """Log an exception message with optional exception info."""
        self.log(
            LogLevel.EXCEPTION,
            msg,
            *args,
            exc_info=traceback.format_exc(),
            **kwargs,
        )


__all__ = ["SimpleLogger"]
