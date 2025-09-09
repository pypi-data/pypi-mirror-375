"""Tests for core logging functionality."""

import json
import time
from io import StringIO
from unittest.mock import patch

import pytest

from logify.core import (
    add_timestamp,
    bind,
    clear_request_context,
    configure_logging,
    critical,
    debug,
    error,
    exception,
    format_log_entry,
    generate_request_id,
    get_logger,
    info,
    orjson_serializer,
    set_request_context,
    track_performance,
    warning,
)


class TestBasicLogging:
    """Test basic logging functions."""

    def setup_method(self):
        """Set up test fixtures."""
        clear_request_context()
        configure_logging("test-service", "DEBUG")

    @patch("sys.stdout", new_callable=StringIO)
    def test_info_logging(self, mock_stdout):
        """Test info logging with basic message."""
        info("Test message", user_id="123", action="test")

        output = mock_stdout.getvalue().strip()
        log_data = json.loads(output)

        assert log_data["message"] == "Test message"
        assert log_data["level"] == "INFO"
        assert log_data["payload"]["user_id"] == "123"
        assert log_data["payload"]["action"] == "test"
        assert "timestamp" in log_data

    @patch("sys.stdout", new_callable=StringIO)
    def test_error_logging_with_exception(self, mock_stdout):
        """Test error logging with exception."""
        test_error = ValueError("Test error")
        error("Operation failed", error=test_error, operation="test")

        output = mock_stdout.getvalue().strip()
        log_data = json.loads(output)

        assert log_data["message"] == "Operation failed"
        assert log_data["level"] == "ERROR"
        assert log_data["error"] == "ValueError: Test error"
        # error_type removed from payload - now included in error field
        assert log_data["payload"]["operation"] == "test"

    @patch("sys.stdout", new_callable=StringIO)
    def test_error_logging_without_exception(self, mock_stdout):
        """Test error logging without exception."""
        error("Simple error", operation="test")

        output = mock_stdout.getvalue().strip()
        log_data = json.loads(output)

        assert log_data["message"] == "Simple error"
        assert log_data["level"] == "ERROR"
        assert "error" not in log_data  # No error field when no exception
        assert log_data["payload"]["operation"] == "test"

    @patch("sys.stdout", new_callable=StringIO)
    def test_all_log_levels(self, mock_stdout):
        """Test all log levels."""
        debug("Debug message")
        info("Info message")
        warning("Warning message")
        error("Error message")
        critical("Critical message")

        output = mock_stdout.getvalue().strip()
        lines = output.split("\n")

        assert len(lines) == 5
        levels = [json.loads(line)["level"] for line in lines]
        assert levels == ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class TestContextManagement:
    """Test context management functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        clear_request_context()
        configure_logging("test-service", "DEBUG")

    @patch("sys.stdout", new_callable=StringIO)
    def test_request_context(self, mock_stdout):
        """Test request context setting."""
        set_request_context(request_id="req-123", user_id="user-456")
        info("Test message")

        output = mock_stdout.getvalue().strip()
        log_data = json.loads(output)

        # Only request_id is automatically included from context now
        assert log_data["payload"]["request_id"] == "req-123"
        # user_id is not automatically included anymore - only request_id

        clear_request_context()
        info("After clear")

        output = mock_stdout.getvalue().strip()
        lines = output.split("\n")
        log_data2 = json.loads(lines[1])

        assert "request_id" not in log_data2["payload"]
        assert "user_id" not in log_data2["payload"]

    @patch("sys.stdout", new_callable=StringIO)
    def test_bound_logger(self, mock_stdout):
        """Test bound logger functionality."""
        logger = bind(service="auth", module="login")
        logger.info("User login attempt", user_id="123")

        output = mock_stdout.getvalue().strip()
        log_data = json.loads(output)

        assert log_data["payload"]["service"] == "auth"
        assert log_data["payload"]["module"] == "login"
        assert log_data["payload"]["user_id"] == "123"

    @patch("sys.stdout", new_callable=StringIO)
    def test_nested_bound_loggers(self, mock_stdout):
        """Test nested bound loggers."""
        logger1 = bind(service="auth")
        logger2 = logger1.bind(module="login", action="validate")
        logger2.info("Validation", user_id="123")

        output = mock_stdout.getvalue().strip()
        log_data = json.loads(output)

        assert log_data["payload"]["service"] == "auth"
        assert log_data["payload"]["module"] == "login"
        assert log_data["payload"]["action"] == "validate"
        assert log_data["payload"]["user_id"] == "123"


class TestUtilities:
    """Test utility functions."""

    def test_generate_request_id(self):
        """Test request ID generation."""
        request_id1 = generate_request_id()
        request_id2 = generate_request_id()

        assert isinstance(request_id1, str)
        assert isinstance(request_id2, str)
        assert request_id1 != request_id2
        assert len(request_id1) == 36  # UUID4 length

    @patch("sys.stdout", new_callable=StringIO)
    def test_performance_tracking(self, mock_stdout):
        """Test performance tracking decorator."""

        @track_performance
        def test_function(x, y):
            time.sleep(0.01)  # Small delay
            return x + y

        result = test_function(1, 2)

        assert result == 3

        output = mock_stdout.getvalue().strip()
        lines = output.split("\n")

        # Should have start and completion logs
        assert len(lines) == 2

        start_log = json.loads(lines[0])
        completion_log = json.loads(lines[1])

        assert "Function started" in start_log["message"]
        assert start_log["payload"]["function"] == "test_function"

        assert "Function completed" in completion_log["message"]
        assert completion_log["payload"]["function"] == "test_function"
        assert "duration_seconds" in completion_log["payload"]
        assert completion_log["payload"]["duration_seconds"] > 0

    @patch("sys.stdout", new_callable=StringIO)
    def test_performance_tracking_with_exception(self, mock_stdout):
        """Test performance tracking with exception."""

        @track_performance
        def failing_function():
            time.sleep(0.01)
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

        output = mock_stdout.getvalue().strip()
        lines = output.split("\n")

        # Should have start and failure logs
        assert len(lines) == 2

        failure_log = json.loads(lines[1])
        assert "Function failed" in failure_log["message"]
        assert failure_log["payload"]["function"] == "failing_function"
        assert "duration_seconds" in failure_log["payload"]
        assert failure_log["error"] == "ValueError: Test error"


class TestLogFormatters:
    """Test log formatting functions."""

    def test_add_timestamp(self):
        """Test timestamp addition."""
        event_dict = {"message": "test"}
        result = add_timestamp(None, None, event_dict)

        assert "timestamp" in result
        assert result["timestamp"].endswith("Z")
        assert "message" in result

    def test_format_log_entry_basic(self):
        """Test basic log entry formatting."""
        event_dict = {
            "event": "Test message",
            "level": "info",
            "user_id": "123",
            "timestamp": "2025-01-01T00:00:00.000Z",
        }

        result = format_log_entry(None, None, event_dict)

        assert result["message"] == "Test message"
        assert result["level"] == "INFO"
        assert result["timestamp"] == "2025-01-01T00:00:00.000Z"
        assert result["payload"]["user_id"] == "123"
        assert "error" not in result

    def test_format_log_entry_with_error(self):
        """Test log entry formatting with error."""
        test_error = ValueError("Test error")
        event_dict = {"event": "Error occurred", "level": "error", "error": test_error, "operation": "test"}

        result = format_log_entry(None, None, event_dict)

        assert result["message"] == "Error occurred"
        assert result["level"] == "ERROR"
        assert result["error"] == "ValueError: Test error"
        assert result["payload"]["operation"] == "test"
        assert "error" not in result["payload"]  # Moved to top level

    def test_orjson_serializer(self):
        """Test orjson serializer."""
        data = {"message": "test", "number": 123, "boolean": True}
        result = orjson_serializer(None, None, data)

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == data


class TestConfiguration:
    """Test configuration functionality."""

    def test_get_logger(self):
        """Test getting named logger."""
        logger = get_logger("test-logger")

        # Should return a bound logger
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "bind")

    def test_configure_logging(self):
        """Test logging configuration."""
        # Should not raise any exceptions
        configure_logging("test-service", "INFO")
        configure_logging("another-service", "DEBUG")

    @patch("sys.stdout", new_callable=StringIO)
    def test_exception_logging(self, mock_stdout):
        """Test exception logging with traceback."""
        configure_logging("test-service", "DEBUG")  # Ensure logging is configured
        try:
            raise ValueError("Test exception")
        except ValueError:
            exception("An exception occurred", context="test")

        output = mock_stdout.getvalue().strip()
        log_data = json.loads(output)

        assert log_data["message"] == "An exception occurred"
        assert log_data["level"] == "ERROR"
        assert "traceback" in log_data["payload"]
        # Check that traceback contains the exception info
        traceback_content = log_data["payload"]["traceback"]
        assert len(traceback_content) > 0
        assert "Traceback" in traceback_content
        assert log_data["payload"]["context"] == "test"


class TestLogSchema:
    """Test log schema compliance."""

    def setup_method(self):
        """Set up test fixtures."""
        clear_request_context()
        configure_logging("schema-test", "DEBUG")

    @patch("sys.stdout", new_callable=StringIO)
    def test_schema_compliance_basic(self, mock_stdout):
        """Test basic schema compliance."""
        info("Test message", custom_field="value")

        output = mock_stdout.getvalue().strip()
        log_data = json.loads(output)

        # Required fields
        assert "timestamp" in log_data
        assert "message" in log_data
        assert "level" in log_data
        assert "payload" in log_data

        # Optional fields should not be present
        assert "error" not in log_data

        # Payload structure
        assert isinstance(log_data["payload"], dict)
        assert log_data["payload"]["custom_field"] == "value"

    @patch("sys.stdout", new_callable=StringIO)
    def test_schema_compliance_with_error(self, mock_stdout):
        """Test schema compliance with error."""
        test_error = RuntimeError("Runtime error")
        error("Error occurred", error=test_error, details="test details")

        output = mock_stdout.getvalue().strip()
        log_data = json.loads(output)

        # Required fields
        assert "timestamp" in log_data
        assert "message" in log_data
        assert "level" in log_data
        assert "payload" in log_data

        # Optional error field should be present
        assert "error" in log_data
        assert log_data["error"] == "RuntimeError: Runtime error"

        # Error should not be duplicated in payload
        assert "error" not in log_data["payload"]
        assert log_data["payload"]["details"] == "test details"
