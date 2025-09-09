"""Tests for Django integration."""

import json
from io import StringIO
from unittest.mock import patch

import pytest

from logify.django import LogifyMiddleware, get_logging_config, setup_django_logging


class MockUser:
    """Mock Django user object."""

    def __init__(self, authenticated=False, user_id=1, username="testuser"):
        self.id = user_id
        self.username = username
        self.is_authenticated = authenticated


class TestDjangoLoggingConfig:
    """Test Django logging configuration."""

    def test_get_logging_config_basic(self):
        """Test basic logging configuration."""
        config = get_logging_config()

        assert config["version"] == 1
        assert config["disable_existing_loggers"] is False
        assert "formatters" in config
        assert "handlers" in config
        assert "loggers" in config
        assert "root" in config

        # Check formatters
        assert "json" in config["formatters"]

        # Check handlers
        assert "console" in config["handlers"]
        assert config["handlers"]["console"]["class"] == "logging.StreamHandler"

        # Check loggers
        assert "django" in config["loggers"]

    def test_get_logging_config_custom_service(self):
        """Test logging configuration with custom service name."""
        config = get_logging_config(service_name="myapp", level="DEBUG")

        assert "myapp" in config["loggers"]
        assert config["loggers"]["myapp"]["level"] == "DEBUG"
        assert config["root"]["level"] == "DEBUG"

    def test_setup_django_logging(self):
        """Test Django logging setup."""
        # Should not raise any exceptions
        setup_django_logging("test-django-service")
        setup_django_logging()


class MockDjangoRequest:
    """Mock Django request object."""

    def __init__(self, method="GET", path="/test", user_agent="TestAgent", remote_addr="127.0.0.1"):
        self.method = method
        self.path = path
        self.META = {
            "HTTP_USER_AGENT": user_agent,
            "REMOTE_ADDR": remote_addr,
        }
        # Add headers attribute that Django middleware expects
        self.headers = {"User-Agent": user_agent, "Host": "testserver", "Content-Type": "text/plain"}
        # Add other attributes middleware expects
        self.GET = {}
        self.body = b""
        self.content_type = "text/plain"
        # Add user mock
        self.user = MockUser()


class MockDjangoResponse:
    """Mock Django response object."""

    def __init__(self, status_code=200, content=b"test content"):
        self.status_code = status_code
        self.content = content


class TestLogifyMiddleware:
    """Test Django Logify middleware."""

    def setup_method(self):
        """Set up test fixtures."""
        from logify.core import clear_request_context

        clear_request_context()

    @patch("sys.stdout", new_callable=StringIO)
    def test_middleware_basic_request(self, mock_stdout):
        """Test middleware with basic request."""

        def mock_get_response(request):
            from logify import info

            info("Processing request")
            return MockDjangoResponse()

        middleware = LogifyMiddleware(mock_get_response)
        request = MockDjangoRequest()

        response = middleware(request)

        assert response.status_code == 200
        assert hasattr(request, "logify_request_id")

        # Check logs
        output = mock_stdout.getvalue().strip()
        if output:  # May be empty if no explicit logging in middleware
            assert "Processing request" in output

    def test_middleware_sets_request_context(self):
        """Test that middleware sets request context."""
        from logify.core import _request_context

        def mock_get_response(request):
            # Check that context is set during request processing (only request_id now)
            try:
                context = _request_context.get()
                assert "request_id" in context
                # Only request_id is set in context now - other fields are logged directly
            except LookupError:
                pytest.fail("Request context not set")

            return MockDjangoResponse(201)

        middleware = LogifyMiddleware(mock_get_response)
        request = MockDjangoRequest(method="POST", path="/api/test", user_agent="TestClient", remote_addr="192.168.1.1")

        response = middleware(request)
        assert response.status_code == 201

    def test_middleware_clears_context_after_request(self):
        """Test that middleware clears context after request."""
        from logify.core import _request_context

        def mock_get_response(request):
            return MockDjangoResponse()

        middleware = LogifyMiddleware(mock_get_response)
        request = MockDjangoRequest()

        middleware(request)

        # Context should be cleared after request
        try:
            context = _request_context.get()
            assert context == {}
        except LookupError:
            pass  # Expected if context is completely cleared

    def test_middleware_handles_exception(self):
        """Test middleware handles exceptions."""

        def mock_get_response(request):
            raise ValueError("Test exception")

        middleware = LogifyMiddleware(mock_get_response)
        request = MockDjangoRequest()

        with pytest.raises(ValueError):
            middleware(request)

        # Context should still be cleared even after exception
        from logify.core import _request_context

        try:
            context = _request_context.get()
            assert context == {}
        except LookupError:
            pass  # Expected if context is completely cleared

    def test_middleware_with_response_content_length(self):
        """Test middleware with response content length."""

        def mock_get_response(request):
            response = MockDjangoResponse(content=b"Hello, World!")
            return response

        middleware = LogifyMiddleware(mock_get_response)
        request = MockDjangoRequest()

        response = middleware(request)
        assert response.status_code == 200
        assert len(response.content) == 13

    def test_middleware_with_missing_headers(self):
        """Test middleware with missing headers."""

        def mock_get_response(request):
            return MockDjangoResponse()

        # Create request with minimal META
        request = MockDjangoRequest()
        request.META = {"REMOTE_ADDR": "127.0.0.1"}  # Missing USER_AGENT

        middleware = LogifyMiddleware(mock_get_response)

        # Should not raise exception
        response = middleware(request)
        assert response.status_code == 200


class TestDjangoIntegration:
    """Test Django integration scenarios."""

    @patch("sys.stdout", new_callable=StringIO)
    def test_full_request_cycle(self, mock_stdout):
        """Test full request cycle with logging."""
        from logify import error, info
        from logify.core import clear_request_context, configure_logging, set_request_context

        # Configure logging to ensure INFO level logs are captured
        configure_logging("test-service", "INFO")

        # Simulate Django middleware setting context
        set_request_context(request_id="django-req-123", method="POST", path="/api/users", user_agent="Django-Test")

        try:
            # Simulate view processing
            info("Starting user creation", action="create_user")

            # Simulate some business logic
            info("Validating user data", user_email="test@example.com")

            # Simulate error
            try:
                raise ValueError("Invalid email format")
            except ValueError as e:
                error("User validation failed", error=e, field="email")

            info("Request completed", status="error")

        finally:
            clear_request_context()

        # Check logs
        output = mock_stdout.getvalue().strip()
        lines = output.split("\n")

        assert len(lines) == 4

        # Check each log contains request context (only request_id is automatic now)
        for line in lines:
            if line.strip():  # Skip empty lines
                log_data = json.loads(line)
                assert log_data["payload"]["request_id"] == "django-req-123"
                # method and path are no longer automatically included from context

        # Check specific log content
        error_log = json.loads(lines[2])
        assert "User validation failed" in error_log["message"]
        assert error_log["error"] == "ValueError: Invalid email format"
        assert error_log["payload"]["field"] == "email"

    def test_django_settings_integration(self):
        """Test Django settings integration."""
        config = get_logging_config(service_name="django-app", level="WARNING", json_logs=True)

        # Verify it produces valid Django LOGGING configuration
        assert isinstance(config, dict)
        assert config["version"] == 1

        # Check that it can be used as Django LOGGING setting
        import logging.config

        # Should not raise exception
        logging.config.dictConfig(config)
