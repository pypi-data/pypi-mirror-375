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


def truncate_long_strings(_, __, event_dict):
    """Truncate long strings in log entries based on max_string_length setting."""
    # Get max length from global settings only
    max_length = 100
    try:
        from .django import _get_setting

        max_length = _get_setting("LOGIFY_MAX_STRING_LENGTH", 100)
    except ImportError:
        # Use default if django module not available
        pass

    # Truncate long strings - only if max_length is positive
    if max_length > 0:
        for key, value in event_dict.items():
            if isinstance(value, str) and len(value) > max_length:
                event_dict[key] = value[:max_length] + "..."

    return event_dict


def clean_non_serializable_objects(_, __, event_dict):
    """Clean non-serializable objects from log entries."""
    # Get settings for string length limits
    max_length = 100
    try:
        from .django import _get_setting

        max_length = _get_setting("LOGIFY_MAX_STRING_LENGTH", 100)
    except ImportError:
        pass

    cleaned = {}
    for key, value in event_dict.items():
        # Skip 'error' field - it will be handled specially in format_log_entry
        if key == "error":
            cleaned[key] = value
            continue

        try:
            # Test if value is JSON serializable
            orjson.dumps(value)
            cleaned[key] = value
        except TypeError:
            # Convert non-serializable objects to their string representation
            if hasattr(value, "__class__"):
                cleaned[key] = f"<{value.__class__.__name__}: {str(value)[:max_length]}>"
            else:
                cleaned[key] = str(value)[:max_length]
    return cleaned


def mask_sensitive_fields(_, __, event_dict):
    """Mask sensitive fields in log entries recursively."""
    # Default sensitive fields
    default_sensitive = [
        "password",
        "passwd",
        "pass",
        "pwd",
        "secret",
        "token",
        "key",
        "api_key",
        "access_token",
        "refresh_token",
        "auth_token",
        "session_key",
        "private_key",
        "credit_card",
        "card_number",
        "cvv",
        "ssn",
        "social_security_number",
    ]

    # Get sensitive fields from global settings only
    sensitive_fields = default_sensitive
    try:
        from .django import _get_setting

        sensitive_fields = _get_setting("LOGIFY_SENSITIVE_FIELDS", default_sensitive)
    except ImportError:
        # Use defaults if django module not available
        pass

    # Convert to set of lowercase strings
    if isinstance(sensitive_fields, (list, tuple)):
        sensitive_fields = set(field.lower() for field in sensitive_fields)
    elif isinstance(sensitive_fields, set):
        sensitive_fields = set(field.lower() for field in sensitive_fields)
    else:
        sensitive_fields = set(field.lower() for field in default_sensitive)

    def _mask_recursive(obj):
        """Recursively mask sensitive fields in dicts and lists."""
        if isinstance(obj, dict):
            masked = {}
            for k, v in obj.items():
                key_lower = k.lower()
                # Check if key contains any sensitive substring
                if any(s in key_lower for s in sensitive_fields):
                    if v and str(v).strip():
                        masked[k] = "***"
                    else:
                        masked[k] = v
                else:
                    masked[k] = _mask_recursive(v)
            return masked
        elif isinstance(obj, list):
            return [_mask_recursive(item) for item in obj]
        return obj

    # Apply masking to the entire event_dict (including top-level keys)
    event_dict = _mask_recursive(event_dict)

    return event_dict


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

    # Get only request_id from context to avoid duplication
    try:
        context = _request_context.get({})
        request_id_only = {"request_id": context.get("request_id")} if context.get("request_id") else {}
    except LookupError:
        request_id_only = {}

    # Extract error from event_dict if present
    error_field = event_dict.pop("error", None)

    # Build the standardized log entry
    formatted_entry = {
        "timestamp": event_dict.pop("timestamp", datetime.now(UTC).isoformat().replace("+00:00", "Z")),
        "message": message,
        "level": level.upper(),
        "payload": {**request_id_only, **event_dict},
    }

    # Add optional error field at top level
    if error_field:
        # Format as "ErrorType: message"
        if isinstance(error_field, Exception):
            if error_field.args:
                formatted_entry["error"] = f"{error_field.__class__.__name__}: {error_field.args[0]}"
            else:
                formatted_entry["error"] = f"{error_field.__class__.__name__}: No message"
        else:
            formatted_entry["error"] = str(error_field)

    return formatted_entry


# Configure structlog with the right processors
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        clean_non_serializable_objects,  # Clean non-serializable objects FIRST
        truncate_long_strings,  # Truncate long strings SECOND
        mask_sensitive_fields,  # Mask sensitive fields THIRD
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
        # error_type removed - now included in error field as "Type: message"
    logger.error(message, **kwargs)


def critical(message: str, **kwargs):
    """Log critical message."""
    logger.critical(message, **kwargs)


def exception(message: str, **kwargs):
    """Log exception with traceback."""
    import traceback

    kwargs["traceback"] = traceback.format_exc()
    logger.error(message, **kwargs)


def get_logger(name: str = "json-logify"):
    """Get a named logger instance."""
    bound_logger = structlog.get_logger(name)
    return bound_logger


def configure_logging(service_name: str = "app", level: str = "INFO"):
    """Configure logging for the application."""
    import logging

    # Set logging level on stdlib logger
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO))

    structlog.configure(
        processors=[
            clean_non_serializable_objects,  # Clean non-serializable objects FIRST
            truncate_long_strings,  # Truncate long strings SECOND
            mask_sensitive_fields,  # Mask sensitive fields THIRD
            add_timestamp,
            format_log_entry,
            orjson_serializer,
        ],
        wrapper_class=structlog.BoundLogger,  # type: ignore
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Set default logger without service binding
    global logger
    logger = structlog.get_logger("json-logify")


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
