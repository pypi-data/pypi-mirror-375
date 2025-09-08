"""
Core structured logging functionality for json-logify.
Provides universal structured logging with exact JSON schema using orjson and structlog.
"""

import time
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any, Dict

import orjson
import structlog

# Context variables for request tracking
_request_context: ContextVar[Dict[str, Any]] = ContextVar("request_context", default={})


def orjson_serializer(_, __, event_dict):
    """Serialize log entries using orjson for performance."""
    return orjson.dumps(event_dict).decode("utf-8")


def add_timestamp(_, __, event_dict):
    """Add ISO timestamp to log entries."""
    # Unresolved attribute reference 'UTC' for class 'datetime'
    event_dict["timestamp"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return event_dict


def format_log_entry(logger, name, event_dict):
    """Format log entry according to json-logify schema."""
    message = event_dict.pop("event", "")

    # Get the correct log level from the logger name if available
    # or from the event dict, defaulting to INFO
    level = name or event_dict.get("level", "INFO")

    # Remove level from event_dict to avoid duplication
    event_dict.pop("level", None)

    # Get context
    try:
        context = _request_context.get({})
    except LookupError:
        context = {}

    # Extract error from event_dict if present
    error_field = event_dict.pop("error", None)

    # Build the standardized log entry
    formatted_entry = {
        "timestamp": event_dict.pop("timestamp", datetime.now(UTC).isoformat().replace("+00:00", "Z")),
        "message": message,
        "level": level.upper(),
        "payload": {**context, **event_dict},
    }

    # Add optional error field at top level
    if error_field:
        formatted_entry["error"] = str(error_field)

    return formatted_entry


# Configure structlog with the right processors
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        add_timestamp,
        format_log_entry,
        orjson_serializer,
    ],
    wrapper_class=structlog.BoundLogger,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)


# Get the default logger
logger = structlog.get_logger("json-logify")


# Convenience functions
def debug(message: str, **kwargs):
    """Log debug message."""
    logger.debug(message, **kwargs)


def info(message: str, **kwargs):
    """Log info message."""
    logger.info(message, **kwargs)


def warning(message: str, **kwargs):
    """Log warning message."""
    logger.warning(message, **kwargs)


def warn(message: str, **kwargs):
    """Alias for warning."""
    logger.warning(message, **kwargs)


def error(message: str, error: Exception = None, **kwargs):
    """Log error message."""
    if error:
        kwargs["error"] = error  # Will be moved to top-level by format_log_entry
        kwargs["error_type"] = type(error).__name__
    logger.error(message, **kwargs)


def critical(message: str, **kwargs):
    """Log critical message."""
    logger.critical(message, **kwargs)


def exception(message: str, **kwargs):
    """Log exception with traceback."""
    import traceback

    kwargs["traceback"] = traceback.format_exc()
    logger.error(message, **kwargs)


def get_logger(name: str = "json-logify", service: str = "app"):
    """Get a named logger instance."""
    bound_logger = structlog.get_logger(name)
    return bound_logger.bind(service=service)


def configure_logging(service_name: str = "app", level: str = "INFO"):
    """Configure logging for the application."""
    import logging

    # Set logging level on stdlib logger
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO))

    structlog.configure(
        processors=[
            add_timestamp,
            format_log_entry,
            orjson_serializer,
        ],
        wrapper_class=structlog.BoundLogger,  # type: ignore
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Bind service name to the default logger
    global logger
    logger = structlog.get_logger("json-logify").bind(service=service_name)


def bind(**kwargs):
    """Create a bound logger with additional context."""
    return logger.bind(**kwargs)


def set_request_context(**kwargs):
    """Set request-level context variables."""
    try:
        current = _request_context.get({})
        _request_context.set({**current, **kwargs})
    except LookupError:
        _request_context.set(kwargs)


def clear_request_context():
    """Clear request-level context."""
    _request_context.set({})


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def track_performance(func):
    """Decorator to track function performance."""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        request_id = generate_request_id()

        info("Function started", function=func.__name__, request_id=request_id)

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            info("Function completed", function=func.__name__, request_id=request_id, duration_seconds=duration)
            return result
        except Exception as e:
            duration = time.time() - start_time
            error("Function failed", function=func.__name__, request_id=request_id, duration_seconds=duration, error=e)
            raise

    return wrapper
