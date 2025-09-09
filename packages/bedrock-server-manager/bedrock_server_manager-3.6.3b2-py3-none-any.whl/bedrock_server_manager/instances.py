from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .context import AppContext

_app_context: AppContext | None = None


def set_app_context(app_context: AppContext):
    """
    Sets the global application context.

    Args:
        app_context (AppContext): The application context to set.
    """
    global _app_context
    _app_context = app_context


def get_app_context() -> AppContext:
    """
    Gets the global application context.

    Returns:
        AppContext: The global application context.

    Raises:
        RuntimeError: If the application context has not been set.
    """
    if _app_context is None:
        raise RuntimeError("Application context has not been set.")
    return _app_context
    # global _app_context
    # if _app_context is None:
    #    from .context import AppContext
    #    from .config.settings import Settings
    #    from .core.manager import BedrockServerManager
    #    settings = Settings()
    #    manager = BedrockServerManager(settings)
    #    _app_context = AppContext(settings=settings, manager=manager)
    # return _app_context


def get_settings_instance():
    warnings.warn(
        "get_settings_instance is deprecated and will be removed in 3.7.0. "
        "Use the application context instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    return get_app_context().settings


def get_manager_instance(settings_instance=None):
    warnings.warn(
        "get_manager_instance is deprecated and will be removed in 3.7.0. "
        "Use the application context instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    return get_app_context().manager


def get_server_instance(server_name: str, settings_instance=None):
    warnings.warn(
        "get_server_instance is deprecated and will be removed in 3.7.0. "
        "Use the application context instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    return get_app_context().get_server(server_name)


def get_bedrock_process_manager(settings_instance=None):
    warnings.warn(
        "get_bedrock_process_manager is deprecated and will be removed in 3.7.0. "
        "Use the application context instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    return get_app_context().bedrock_process_manager


def get_db():
    warnings.warn(
        "get_db is deprecated and will be removed in 3.7.0. "
        "Use the application context instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_app_context().db
