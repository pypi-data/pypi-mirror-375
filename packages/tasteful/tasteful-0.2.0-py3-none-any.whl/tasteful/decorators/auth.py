"""Decorators for authentication and authorization in Tasteful applications."""

from functools import wraps
from typing import Callable


def public(func: Callable) -> Callable:
    """Mark a route as public, bypassing authentication requirements."""
    setattr(func, "is_public_route", True)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    return wrapper
