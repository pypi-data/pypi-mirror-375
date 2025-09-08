import fcntl
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import IO, Any

from bear_dereth.config._settings_manager._base_classes import Storage
from bear_dereth.tools.general.files import touch


class JSONFileManager(Storage):
    def __init__(self, filename: str | Path, file_mode: str = "r+", encoding: str = "utf-8") -> None:
        super().__init__()
        self.filename: Path = touch(filename, mkdir=True)
        self.temp_handle: IO[Any] = self.open(mode="temp", file_mode=file_mode, encoding=encoding)
        self.file_handle: IO[Any] = self.open(self.filename, file_mode, encoding)
        self.handle_map: dict[str, IO[Any]] = {"default": self.file_handle, "temp": self.temp_handle}

    def open(
        self,
        filename: Path = Path("/dev/null"),
        file_mode: str = "r+",
        encoding: str = "utf-8",
        mode: str = "default",
        **kwargs,
    ) -> IO[Any]:
        if mode == "temp":
            with NamedTemporaryFile(delete_on_close=True, mode=file_mode, encoding=encoding, **kwargs) as f:
                return f

        with open(filename, file_mode, encoding=encoding, **kwargs) as f:
            return f

    def read(self, mode: str = "default") -> dict[str, dict[str, Any]] | None:
        handle: IO[Any] = self.handle_map.get(mode, self.file_handle)
        fcntl.flock(handle.fileno(), fcntl.LOCK_SH)
        handle.seek(0)
        try:
            data: dict[str, dict[str, Any]] = json.load(handle)
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        return data

    def write(self, data: dict[str, Any], mode: str = "default") -> None:
        handle: IO[Any] = self.handle_map.get(mode, self.file_handle)
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            handle.seek(0)
            handle.truncate()  # Clear file
            json.dump(data, handle, indent=2)
            handle.flush()  # Force write to disk
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def close(self) -> None:
        for handle in self.handle_map.values():
            handle.close()
