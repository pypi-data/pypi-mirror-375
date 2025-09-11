"""Core environment variable utilities for Foundation."""

import os

from provide.foundation.errors import ValidationError


def get_env(key: str, default: str | None = None) -> str | None:
    """
    Get environment variable with Foundation tracking.

    Args:
        key: Environment variable name
        default: Default value if variable not found

    Returns:
        Environment variable value or default

    Example:
        >>> get_env("HOME")  # doctest: +SKIP
        '/Users/username'
        >>> get_env("NONEXISTENT", "fallback")
        'fallback'
    """
    return os.environ.get(key, default)


def set_env(key: str, value: str) -> None:
    """
    Set environment variable with validation.

    Args:
        key: Environment variable name
        value: Value to set

    Raises:
        ValidationError: If key or value is invalid

    Example:
        >>> set_env("TEST_VAR", "test_value")
        >>> get_env("TEST_VAR")
        'test_value'
    """
    if not isinstance(key, str) or not key:
        raise ValidationError("Environment variable key must be a non-empty string")
    if not isinstance(value, str):
        raise ValidationError("Environment variable value must be a string")

    os.environ[key] = value


def unset_env(key: str) -> None:
    """
    Remove environment variable if it exists.

    Args:
        key: Environment variable name to remove

    Example:
        >>> set_env("TEMP_VAR", "value")
        >>> unset_env("TEMP_VAR")
        >>> has_env("TEMP_VAR")
        False
    """
    os.environ.pop(key, None)


def has_env(key: str) -> bool:
    """
    Check if environment variable exists.

    Args:
        key: Environment variable name

    Returns:
        True if variable exists, False otherwise

    Example:
        >>> has_env("PATH")
        True
        >>> has_env("DEFINITELY_NOT_SET")
        False
    """
    return key in os.environ


def get_env_int(key: str, default: int | None = None) -> int | None:
    """
    Get environment variable as integer.

    Args:
        key: Environment variable name
        default: Default value if variable not found or invalid

    Returns:
        Integer value or default

    Raises:
        ValidationError: If value exists but cannot be converted to int

    Example:
        >>> set_env("PORT", "8080")
        >>> get_env_int("PORT")
        8080
        >>> get_env_int("MISSING_PORT", 3000)
        3000
    """
    value = os.environ.get(key)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError as e:
        raise ValidationError(
            f"Environment variable {key}='{value}' cannot be converted to int"
        ) from e


def get_env_bool(key: str, default: bool | None = None) -> bool | None:
    """
    Get environment variable as boolean.

    Recognizes: true/false, yes/no, 1/0, on/off (case insensitive)

    Args:
        key: Environment variable name
        default: Default value if variable not found

    Returns:
        Boolean value or default

    Raises:
        ValidationError: If value exists but cannot be converted to bool

    Example:
        >>> set_env("DEBUG", "true")
        >>> get_env_bool("DEBUG")
        True
        >>> set_env("VERBOSE", "no")
        >>> get_env_bool("VERBOSE")
        False
    """
    value = os.environ.get(key)
    if value is None:
        return default

    value_lower = value.lower().strip()
    if value_lower in ("true", "yes", "1", "on"):
        return True
    elif value_lower in ("false", "no", "0", "off"):
        return False
    else:
        raise ValidationError(
            f"Environment variable {key}='{value}' cannot be converted to bool"
        )


def get_env_float(key: str, default: float | None = None) -> float | None:
    """
    Get environment variable as float.

    Args:
        key: Environment variable name
        default: Default value if variable not found or invalid

    Returns:
        Float value or default

    Raises:
        ValidationError: If value exists but cannot be converted to float

    Example:
        >>> set_env("TIMEOUT", "30.5")
        >>> get_env_float("TIMEOUT")
        30.5
    """
    value = os.environ.get(key)
    if value is None:
        return default

    try:
        return float(value)
    except ValueError as e:
        raise ValidationError(
            f"Environment variable {key}='{value}' cannot be converted to float"
        ) from e


def get_env_list(
    key: str, separator: str = ",", default: list[str] | None = None
) -> list[str] | None:
    """
    Get environment variable as list of strings.

    Args:
        key: Environment variable name
        separator: Character to split on (default: comma)
        default: Default value if variable not found

    Returns:
        List of strings or default

    Example:
        >>> set_env("ALLOWED_HOSTS", "localhost,127.0.0.1,example.com")
        >>> get_env_list("ALLOWED_HOSTS")
        ['localhost', '127.0.0.1', 'example.com']
        >>> get_env_list("MISSING", default=["fallback"])
        ['fallback']
    """
    value = os.environ.get(key)
    if value is None:
        return default

    if not value.strip():
        return []

    return [item.strip() for item in value.split(separator) if item.strip()]
