from enum import Enum
from os import getenv as os_getenv


class EnvVar:
    """Environment variable wrapper with type conversion methods."""

    def __init__(self, value: str | None):
        self._value = value

    def __str__(self) -> str:
        return self._value or ""

    def __repr__(self) -> str:
        return f"EnvVar({self._value!r})"

    @property
    def value(self) -> str | None:
        """Get the raw string value."""
        return self._value

    def as_bool(self) -> bool:
        """Convert to boolean. True for 'true', '1', 'yes', 'on' (case-insensitive)."""
        if not self._value:
            return False
        return self._value.lower() in ("true", "1", "y", "yes", "on")

    def as_int(self, default: int | None = None) -> int | None:
        """Convert to integer."""
        if not self._value:
            return default
        try:
            return int(self._value)
        except ValueError:
            return default

    def as_float(self, default: float | None = None) -> float | None:
        """Convert to float."""
        if not self._value:
            return default
        try:
            return float(self._value)
        except ValueError:
            return default

    def as_list(self, separator: str = ",") -> list[str]:
        """Convert comma-separated string to list."""
        if not self._value:
            return []
        return [item.strip() for item in self._value.split(separator) if item.strip()]

    def as_enum(self, enum_class: type[Enum], default: Enum | None = None) -> Enum | None:
        """Convert to enum value."""
        if not self._value:
            return default
        try:
            return enum_class(self._value)
        except ValueError:
            return default

    def is_set(self) -> bool:
        """Check if the environment variable is set (not None or empty)."""
        return self._value is not None and self._value.strip() != ""


def getenv(key: str, default: str | None = None) -> EnvVar:
    """Get environment variable wrapped with type conversion methods."""
    return EnvVar(os_getenv(key, default))
