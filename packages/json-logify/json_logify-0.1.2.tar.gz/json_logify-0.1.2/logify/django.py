"""
Django integration for json-logify structured logging.
"""

import logging

import structlog

from .core import clear_request_context, configure_logging, generate_request_id, set_request_context

# Global settings storage for when Django settings are not available
_global_settings = {}


def _set_global_setting(key: str, value):
    """Set a global setting value."""
    _global_settings[key] = value


def _get_setting(key: str, default=None):
    """Get setting value from global settings only."""
    # Return value from global settings (set by get_logging_config parameters)
    return _global_settings.get(key, default)


def get_logging_config(
    service_name: str = "django",
    level: str = "INFO",
    json_logs: bool = True,
    excluded_fields: list = None,
    sensitive_fields: list = None,
    max_string_length: int = None,
    ignore_paths: list = None,
):
    """
    Get Django logging configuration for json-logify.

    Args:
        service_name: Name of the service for logging
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        json_logs: Whether to enable JSON logging
        excluded_fields: List of fields to exclude from logs
        sensitive_fields: List of fields to mask with *** (also used for sensitive headers)
        max_string_length: Maximum length for string truncation
        ignore_paths: List of URL paths to ignore from logging

    Usage in settings.py:
        from logify.django import get_logging_config
        LOGGING = get_logging_config(
            service_name="myapp",
            level="INFO",
            excluded_fields=["custom_field"],
            sensitive_fields=["password", "secret", "authorization"],
            max_string_length=200,
            ignore_paths=["/health/", "/static/"]
        )
    """
    if json_logs:
        configure_logging(service_name=service_name, level=level)

    # Store settings globally for the processors to use
    _set_global_setting("SERVICE_NAME", service_name)
    if excluded_fields is not None:
        _set_global_setting("LOGIFY_EXCLUDED_FIELDS", excluded_fields)
    if sensitive_fields is not None:
        _set_global_setting("LOGIFY_SENSITIVE_FIELDS", sensitive_fields)
    if max_string_length is not None:
        _set_global_setting("LOGIFY_MAX_STRING_LENGTH", max_string_length)
    if ignore_paths is not None:
        _set_global_setting("LOGIFY_IGNORE_PATHS", ignore_paths)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
            },
            "structlog": {
                "()": "logify.django.StructlogHandler",
            },
        },
        "root": {
            "handlers": ["structlog"],
            "level": level,
        },
        "loggers": {
            "django": {
                "handlers": ["structlog"],
                "level": level,
                "propagate": False,
            },
            service_name: {
                "handlers": ["structlog"],
                "level": level,
                "propagate": False,
            },
        },
    }


class LogifyMiddleware:
    """Django middleware for structured logging with request context."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip logging for ignored paths
        if self._should_ignore_path(request.path):
            return self.get_response(request)

        # Import here to avoid circular imports
        from .core import info

        # Generate request ID and set context
        request_id = generate_request_id()
        request.logify_request_id = request_id

        # Get service name from global settings or use default
        service_name = _get_setting("SERVICE_NAME", "django-app")

        # Get user info
        user_info = self._get_user_info(request)

        # Get and scrub headers
        scrubbed_headers = self._scrub_headers(dict(request.headers))

        # Get request body (no scrubbing - core processors will handle)
        request_body = self._get_request_body(request)

        # Log request start with all context information ONCE
        info(
            "Request started",
            request_id=request_id,
            service=service_name,
            method=request.method,
            path=request.path,
            user_info=user_info,
            headers=scrubbed_headers,
            query_params=dict(request.GET) if request.GET else None,
            request_body=request_body,
        )

        # Set minimal context for other logs (only request_id)
        set_request_context(request_id=request_id)

        try:
            response = self.get_response(request)

            # Get response body with content type filtering (no scrubbing)
            response_body = self._get_response_body(response)

            # Log request completion with response info
            info(
                "Request completed",
                request_id=request_id,
                user_info=user_info,
                status_code=response.status_code,
                content_length=len(response.content) if hasattr(response, "content") else None,
                response_body=response_body,
            )

            return response
        finally:
            clear_request_context()

    def _should_ignore_path(self, path):
        """Check if path should be ignored from logging."""
        # Get ignore paths from global settings
        default_ignore_paths = ["/health/", "/healthz/", "/api/schema/", "/static/", "/favicon.ico", "/robots.txt"]

        try:
            ignore_paths = _get_setting("LOGIFY_IGNORE_PATHS", default_ignore_paths)
        except Exception:
            ignore_paths = default_ignore_paths

        if isinstance(ignore_paths, (list, tuple)):
            for ignore_path in ignore_paths:
                if path.startswith(ignore_path):
                    return True
        return False

    def _get_user_info(self, request):
        """Get user information from request."""
        if hasattr(request, "user") and request.user.is_authenticated:
            return f"User ID: {request.user.id}: {request.user.username}"
        return "Anonymous user"

    def _scrub_headers(self, headers):
        """Mask sensitive headers using sensitive_fields settings."""
        # Get sensitive fields which will be used for headers too
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
            "authorization",
            "cookie",
            "x-api-key",
            "x-auth-token",
            "x-csrf-token",
        ]

        try:
            sensitive_fields = _get_setting("LOGIFY_SENSITIVE_FIELDS", default_sensitive)
        except Exception:
            sensitive_fields = default_sensitive

        if isinstance(sensitive_fields, (list, tuple)):
            sensitive_fields = set(field.lower() for field in sensitive_fields)
        else:
            sensitive_fields = set(field.lower() for field in default_sensitive)

        scrubbed = {}
        for key, value in headers.items():
            key_lower = key.lower().replace("-", "_")  # Convert dashes to underscores for matching
            # Check if header name contains any sensitive substring
            if any(s in key_lower for s in sensitive_fields):
                scrubbed[key] = "[FILTERED]"
            else:
                scrubbed[key] = value
        return scrubbed

    def _get_request_body(self, request):
        """Get request body with size limits (no scrubbing - core processors will handle)."""
        if not request.body:
            return None

        try:
            # Limit body size for logging (max 10KB)
            body_bytes = request.body[:10240]

            if request.content_type and "json" in request.content_type:
                import json

                request_body = json.loads(body_bytes.decode("utf-8"))
                return request_body
            else:
                # For non-JSON data, try to parse as form data
                if request.method in ["POST", "PUT", "PATCH"]:
                    try:
                        # Try form data first
                        form_data = dict(request.POST)
                        if form_data:
                            return form_data
                    except Exception:
                        pass

                # Fall back to raw string (truncated)
                return body_bytes.decode("utf-8", errors="replace")[:1000]

        except Exception:
            return "<non-readable body>"

    def _get_response_body(self, response):
        """Get response body with content type filtering (no scrubbing - core processors will handle)."""
        if not hasattr(response, "content") or not response.content:
            return None

        content_type = response.get("Content-Type", "") if hasattr(response, "get") else ""

        # Skip HTML, JavaScript, CSS, and other non-data content types
        skip_content_types = [
            "text/html",
            "text/css",
            "application/javascript",
            "text/javascript",
            "image/",
            "video/",
            "audio/",
            "application/pdf",
            "application/octet-stream",
        ]

        if any(skip_type in content_type for skip_type in skip_content_types):
            return f"<skipped: {content_type}>"

        try:
            # Limit response body size for logging (max 10KB)
            body_bytes = response.content[:10240]

            if "json" in content_type:
                import json

                response_body = json.loads(body_bytes.decode("utf-8"))
                return response_body
            else:
                # For non-JSON responses, return truncated text
                return body_bytes.decode("utf-8", errors="replace")[:1000]

        except Exception:
            return "<non-readable body>"


def setup_django_logging(service_name: str = "django"):
    """
    Set up Django logging with json-logify.
    Call this in your Django settings or apps.py
    """
    # Configure json-logify structlog
    configure_logging(service_name=service_name)

    # Configure structlog to intercept standard logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


class StructlogHandler(logging.Handler):
    """Custom handler that routes standard logging to structlog."""

    def __init__(self):
        super().__init__()
        self.structlog_logger = structlog.get_logger()

    def emit(self, record):
        # Convert logging record to structlog format
        level_name = record.levelname.lower()
        structlog_method = getattr(self.structlog_logger, level_name, self.structlog_logger.info)

        # Get excluded fields from settings
        default_excluded = [
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
            "exc_info",
            "exc_text",
            "stack_info",
            "getMessage",
            # Add Django-specific problematic fields
            "request",
            "response",
            "server_time",
            "status_code",
        ]

        excluded_fields = _get_setting("LOGIFY_EXCLUDED_FIELDS", default_excluded)
        if isinstance(excluded_fields, (list, tuple)):
            excluded_fields = set(excluded_fields)
        elif not isinstance(excluded_fields, set):
            excluded_fields = set(default_excluded)

        # Get sensitive fields from settings
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
        sensitive_fields = _get_setting("LOGIFY_SENSITIVE_FIELDS", default_sensitive)
        if isinstance(sensitive_fields, (list, tuple)):
            sensitive_fields = set(field.lower() for field in sensitive_fields)
        elif not isinstance(sensitive_fields, set):
            sensitive_fields = set(field.lower() for field in default_sensitive)

        # Extract extra fields, excluding specified fields and masking sensitive ones
        extra = {}
        for key, value in record.__dict__.items():
            if key not in excluded_fields:
                # Skip complex objects that can't be JSON serialized
                if hasattr(value, "__dict__") and not isinstance(value, (str, int, float, bool, list, dict)):
                    continue

                # Mask sensitive fields
                if key.lower() in sensitive_fields:
                    if value and str(value).strip():
                        extra[key] = "***"
                    else:
                        extra[key] = value
                else:
                    extra[key] = value

        # Log with structlog
        structlog_method(
            record.getMessage(),
            logger=record.name,
            module=record.module,
            funcName=record.funcName,
            lineno=record.lineno,
            **extra,
        )
