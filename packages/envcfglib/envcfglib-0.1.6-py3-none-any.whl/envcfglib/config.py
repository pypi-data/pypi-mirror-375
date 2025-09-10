from os import environ
from typing import Any, Self
from collections.abc import Callable

__all__ = [
    "Config",
]


class Config:
    _instances: dict[str, Self] = dict()

    _loaded_configuration: dict[str, dict[str, Any]] = dict()
    _prefix_key: str = ""

    def __init__(self, prefix_key: str = ""):
        """
        Initialize the Config instance with a specific key prefix.
        Args:
            prefix_key (str): The prefix key for the configuration instance.
        """
        self._prefix_key = prefix_key
        if prefix_key not in self._loaded_configuration:
            self._loaded_configuration[prefix_key] = dict()

    def __new__(cls, key: str = "", *args, **kwargs) -> Self:
        """Singleton pattern implementation to ensure one instance per prefix key."""
        if key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[key] = instance
        return cls._instances[key]

    def __getattr__(self, name: str):
        return self._get_value(name)

    def _get_value(self, key: str) -> Any:
        return self._loaded_configuration[self._prefix_key][key]

    def _set_value(self, key: str, value: Any) -> None:
        self._loaded_configuration[self._prefix_key][key] = value

    def _get_environ_key(self, key: str) -> str:
        if self._prefix_key:
            return f"{self._prefix_key}_{key}".upper()
        return key.upper()

    def load_configuration(
        self,
        key: str,
        *,
        factory: Callable[[str], Any] = str,
        default: Any | None = None,
        force: bool = False,
    ) -> None:
        """
        Load a configuration value from environment variables.
        If the values was already loaded, the function call will be ignored unless force=True.

        Args:
            key: The environment variable key to load.
            factory: A factory function to convert the string value to the desired type.
            default: A default value to use if the environment variable is not set.

        Returns:
            None

        Raises:
            KeyError: If the environment variable is not set and no default is provided.
        """

        if not force and key in self._loaded_configuration[self._prefix_key]:
            return

        try:
            val = environ[self._get_environ_key(key)]
        except KeyError:
            if default is None:
                raise
            self._set_value(key, default)
        else:
            self._set_value(key, factory(val))

    def get_value(
        self, key: str, *, factory: Callable[[Any], Any] | None = None
    ) -> Any:
        """
        Retrieve a loaded configuration value, optionally applying a factory function.

        Args:
            key: The key of the configuration value to retrieve.
            factory: A factory function to convert the value to the desired type.

        Returns:
            The requested value. If a factory is provided, the value is processed through it before returning.

        Raises:
            KeyError: If the key is not found in the loaded configuration.
        """
        val = self._get_value(key)

        if factory is None:
            return val

        return factory(val)
