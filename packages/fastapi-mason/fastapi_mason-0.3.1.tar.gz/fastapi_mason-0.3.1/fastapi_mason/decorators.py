"""
Decorators for FastAPI Mason viewsets.

Provides decorators for automatic viewset registration and configuration.
"""

from typing import Any, Callable, Optional, Type

from fastapi import APIRouter

from fastapi_mason.viewsets import GenericViewSet


def viewset(router: APIRouter):
    """Decorator for automatic viewset registration with FastAPI router."""

    def decorator(cls: Type[GenericViewSet]):
        """Apply viewset decorator to class."""
        # Store router on the class
        cls.router = router

        try:
            # Create instance to trigger route registration
            cls()

        except Exception as e:
            raise RuntimeError(
                f'Failed to initialize viewset {cls.__name__}: {e}. '
                f'Make sure all required attributes (model, schemas) are set.'
            ) from e

        return cls

    return decorator


def action(
    methods: Optional[list[str]] = None,
    detail: bool = False,
    path: Optional[str] = None,
    name: Optional[str] = None,
    response_model: Any = None,
    **kwargs,
):
    """Decorator to mark a viewset method as a routable action."""
    if methods is None:
        methods = ['GET']

    def decorator(func: Callable) -> Callable:
        # Store action metadata on the function
        func._is_action = True
        func._action_methods = [method.upper() for method in methods]
        func._action_detail = detail
        func._action_path = path
        func._action_name = name
        func._action_response_model = response_model
        func._action_kwargs = kwargs

        return func

    return decorator
