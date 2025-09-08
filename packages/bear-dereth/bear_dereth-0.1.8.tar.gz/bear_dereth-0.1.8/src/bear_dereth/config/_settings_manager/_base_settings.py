"""A base class for handling a single dedicated setting in a context-aware manner."""

from __future__ import annotations

from os import getenv
from pathlib import Path
from types import SimpleNamespace as Namespace
from typing import Any

from singleton_base import SingletonBase

from bear_dereth.config.settings_manager import SettingsManager


def get_context() -> str:
    """Get the current context for the settings handler."""
    return getenv("DATABASE_FILENAME", "claude_memories.db").replace(".db", "")


def get_folder_path() -> Path:
    """Get the folder path for the settings manager."""
    return Path(getenv("DATABASE_PATH", Path() / ".config" / "bear_utils")) / "settings"


class BaseSetting:
    """Base Class for a single setting."""

    def __init__(self, settings_handler: BaseSettingHandler, name: str, default: Any = None) -> None:
        """Initialize the BaseSetting with a name and default value."""
        self.settings_handler: BaseSettingHandler = settings_handler
        self.context: str = settings_handler.context
        self.settings_manager: SettingsManager = settings_handler.settings_manager
        self.attr_name: str = name
        self.default: Any = default

    @property
    def name(self) -> str:
        """Get the name of the setting."""
        return f"{self.attr_name}_{self.context}"

    @property
    def value(self) -> Any:
        """Get the current value of the setting."""
        return self.settings_manager.get(self.name, default=self.default)

    @value.setter
    def value(self, value: Any) -> None:
        """Set a new value for the setting."""
        self.settings_manager.set(self.name, value)

    def get(self) -> Any:
        """Get the current value of the setting."""
        return self.value

    def set(self, value: Any) -> None:
        """Set a new value for the setting."""
        self.value = value

    def __str__(self) -> str:
        """Return a string representation of the setting."""
        return f"{self.name}: {self.value}"

    def __repr__(self) -> str:
        """Return a string representation of the setting for debugging."""
        return f"BaseSetting(name={self.name}, value={self.value})"


class BaseSettingHandler(SingletonBase):
    """Base Class for handling a single setting with specific focus that will change based upon the context of the server."""

    def __init__(self, context: str | None = None) -> None:
        """Initialize the BaseSettingHandler with a default setting value."""
        self.context: str = context or get_context()
        self.settings_manager = SettingsManager(name=self.context, path=get_folder_path())
        self.settings: Namespace = Namespace()
        self.settings_names: list[str] = list(self.get_names)

    @property
    def get_names(self) -> list[str]:
        """Get the names of all registered settings."""
        return list(self.settings.__dict__.keys())

    def register_setting[ValueType](self, setting_name: str, default_value: Any) -> None:
        """Register a new setting with a default value.

        This method is used to register a new setting dynamically.
        """
        if not hasattr(self.settings, setting_name):
            settings_class = BaseSetting(self, setting_name, default_value)
            setattr(self.settings, setting_name, settings_class)
            value: ValueType = settings_class.get()
            settings_class.set(value)
        self.settings_names = self.get_names

    def apply_settings[ValueType](self, settings_list: list[tuple[str, Any]]) -> Namespace:
        """Apply the settings to the current context."""
        space = Namespace()
        for setting_name, default_value in settings_list:
            if not hasattr(space, setting_name):
                settings_class = BaseSetting(self, setting_name, default_value)
                setattr(space, setting_name, settings_class)
                value: ValueType = settings_class.get()
                settings_class.set(value)
        return space

    def get_setting(self, key: str) -> BaseSetting:
        """Get a specific setting by its key."""
        return getattr(self.settings, key)

    def set(self, key: str, value: Any) -> None:
        """Set a specific setting value."""
        self.get_setting(key).set(value)

    def get(self, key: str) -> Any:
        """Get a specific setting value."""
        return self.get_setting(key).get()

    def clear(self) -> None:
        """Reset the setting to its default value."""
        for key in self.settings_names:
            setting: BaseSetting = self.get_setting(key)
            self.set(key, setting.default)
