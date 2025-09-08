"""
Django integration for json-logify structured logging.
"""

from .core import clear_request_context, configure_logging, generate_request_id, set_request_context


def get_logging_config(service_name: str = "django", level: str = "INFO", json_logs: bool = True):
    """
    Get Django logging configuration for json-logify.

    Usage in settings.py:
        from logify.django import get_logging_config
        LOGGING = get_logging_config(service_name="myapp")
    """
    if json_logs:
        configure_logging(service_name=service_name, level=level)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {"format": "%(message)s"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": level,
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": level,
                "propagate": False,
            },
            service_name: {
                "handlers": ["console"],
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
        # Generate request ID and set context
        request_id = generate_request_id()
        request.logify_request_id = request_id

        set_request_context(
            request_id=request_id,
            method=request.method,
            path=request.path,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            remote_addr=request.META.get("REMOTE_ADDR", ""),
        )

        try:
            response = self.get_response(request)

            # Add response info to context
            set_request_context(
                status_code=response.status_code,
                content_length=len(response.content) if hasattr(response, "content") else None,
            )

            return response
        finally:
            clear_request_context()


def setup_django_logging(service_name: str = "django"):
    """
    Set up Django logging with json-logify.
    Call this in your Django settings or apps.py
    """
    configure_logging(service_name=service_name)
