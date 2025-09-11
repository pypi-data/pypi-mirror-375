"""Test utility functions."""

from pydantic import ValidationError


def error_locations(ve: ValidationError) -> list[tuple[str, ...]]:
    """Return all the error locations from a ValidationError."""
    return [e["loc"] for e in ve.errors()]
