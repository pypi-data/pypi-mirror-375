"""
json-logify - Universal structured logging with exact JSON schema for Python frameworks.

Simple usage:
    from logify import info, error

    info("User logged in", user_id="12345")
    error("Database error", error="Connection timeout")

For more examples, see: https://github.com/yourusername/json-logify
"""

from .core import (  # Convenience functions; Configuration; Context management; Utilities
    bind,
    clear_request_context,
    configure_logging,
    critical,
    debug,
    error,
    exception,
    generate_request_id,
    get_logger,
    info,
    set_request_context,
    track_performance,
    warning,
)
from .version import __version__

__all__ = [
    # Version
    "__version__",
    # Convenience functions
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "exception",
    # Configuration
    "configure_logging",
    "get_logger",
    # Context management
    "bind",
    "set_request_context",
    "clear_request_context",
    # Utilities
    "generate_request_id",
    "track_performance",
]
