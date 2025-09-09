# """Tests for Flask integration."""
#
# import json
# from io import StringIO
# from unittest.mock import patch
#
# import pytest
#
# from logify.flask import init_logify, setup_flask_logging
#
#
# class MockFlaskApp:
#     """Mock Flask app for testing."""
#
#     def __init__(self):
#         self.before_request_funcs = []
#         self.after_request_funcs = []
#         self.teardown_appcontext_funcs = []
#
#     def before_request(self, func):
#         """Mock before_request decorator."""
#         self.before_request_funcs.append(func)
#         return func
#
#     def after_request(self, func):
#         """Mock after_request decorator."""
#         self.after_request_funcs.append(func)
#         return func
#
#     def teardown_appcontext(self, func):
#         """Mock teardown_appcontext decorator."""
#         self.teardown_appcontext_funcs.append(func)
#         return func
#
#     def get_teardown_funcs(self):
#         """Get teardown functions for testing."""
#         return self.teardown_appcontext_funcs
#
#
# class MockFlaskRequest:
#     """Mock Flask request object."""
#
#     def __init__(self, method="GET", path="/", query_string=b"", remote_addr="127.0.0.1", user_agent="TestClient"):
#         self.method = method
#         self.path = path
#         self.query_string = query_string
#         self.remote_addr = remote_addr
#         self.headers = {"User-Agent": user_agent}
#
#
# class MockFlaskResponse:
#     """Mock Flask response object."""
#
#     def __init__(self, status_code=200, content_length=None):
#         self.status_code = status_code
#         self.content_length = content_length
#
#
# class MockFlaskG:
#     """Mock Flask g object."""
#
#     def __init__(self):
#         self._storage = {}
#
#     def __setattr__(self, name, value):
#         if name.startswith("_"):
#             super().__setattr__(name, value)
#         else:
#             self._storage[name] = value
#
#     def __getattr__(self, name):
#         if name in self._storage:
#             return self._storage[name]
#         raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
#
#
# class TestInitLogify:
#     """Test init_logify function."""
#
#     def setup_method(self):
#         """Set up test fixtures."""
#         from logify.core import clear_request_context
#
#         clear_request_context()
#
#     def test_init_logify_basic(self):
#         """Test basic init_logify functionality."""
#         app = MockFlaskApp()
#
#         # Should not raise exceptions
#         init_logify(app)
#
#         # Check that handlers were registered
#         assert len(app.before_request_funcs) == 1
#         assert len(app.after_request_funcs) == 1
#         assert len(app.teardown_appcontext_funcs) == 1
#
#     def test_init_logify_custom_service(self):
#         """Test init_logify with custom service name."""
#         app = MockFlaskApp()
#
#         init_logify(app, service_name="custom-flask-app", log_requests=False)
#
#         # Should still register handlers
#         assert len(app.before_request_funcs) == 1
#         assert len(app.after_request_funcs) == 1
#         assert len(app.teardown_appcontext_funcs) == 1
#
#
# class TestFlaskMiddleware:
#     """Test Flask middleware functionality."""
#
#     def setup_method(self):
#         """Set up test fixtures."""
#         from logify.core import clear_request_context
#
#         clear_request_context()
#
#     @patch("sys.stdout", new_callable=StringIO)
#     def test_before_request_handler(self, mock_stdout):
#         """Test before_request handler."""
#         # Use the real Flask objects in a test context
#         from flask import Flask, g
#
#         app = Flask(__name__)
#         init_logify(app, log_requests=True)
#
#         with app.test_request_context("/api/test", method="POST", headers={"User-Agent": "TestClient/1.0"}):
#             # Call before_request handler directly
#             before_request_handler = app.before_request_funcs[None][0]
#             before_request_handler()
#
#             # Check that request ID was set
#             assert hasattr(g, "logify_request_id")
#             assert hasattr(g, "logify_start_time")
#
#             # Check context was set
#             from logify.core import _request_context
#
#             try:
#                 context = _request_context.get()
#                 assert context["method"] == "POST"
#                 assert context["path"] == "/api/test"
#             except LookupError:
#                 pytest.fail("Request context not set")
#
#             # Check log output
#             output = mock_stdout.getvalue().strip()
#             if output:
#                 log_data = json.loads(output)
#                 assert "Request started" in log_data["message"]
#
#     @patch("sys.stdout", new_callable=StringIO)
#     def test_after_request_handler(self, mock_stdout):
#         """Test after_request handler."""
#         from flask import Flask, g
#
#         app = Flask(__name__)
#         init_logify(app, log_requests=True)
#
#         with app.test_request_context("/api/test", method="POST"):
#             # Set up g with request data
#             g.logify_request_id = "test-req-123"
#             g.logify_start_time = 1640995200.0  # Fixed time for testing
#
#             # Call after_request handler
#             after_request_handler = app.after_request_funcs[None][0]
#             response = MockFlaskResponse(status_code=201, content_length=100)
#
#             with patch("time.time", return_value=1640995200.5):  # 0.5 seconds later
#                 result = after_request_handler(response)
#
#             # Should return the same response
#             assert result is response
#
#             # Check log output
#             output = mock_stdout.getvalue().strip()
#             if output:
#                 log_data = json.loads(output)
#                 assert "Request completed" in log_data["message"]
#                 assert log_data["payload"]["status_code"] == 201
#                 assert log_data["payload"]["duration_seconds"] == 0.5
#
#     @patch("sys.stdout", new_callable=StringIO)
#     def test_teardown_appcontext_handler(self, mock_stdout):
#         """Test teardown_appcontext handler."""
#         from flask import Flask, g
#
#         app = Flask(__name__)
#         init_logify(app, log_requests=True)
#
#         with app.test_request_context("/test"):
#             g.logify_request_id = "test-123"
#
#             # Get all teardown handlers
#             teardown_funcs = app.teardown_appcontext_funcs
#             assert len(teardown_funcs) > 0
#
#             # Call the last registered handler with no exception
#             teardown_funcs[-1](None)
#
#             # Context should be cleared
#             from logify.core import _request_context
#
#             try:
#                 context = _request_context.get()
#                 assert context == {}
#             except LookupError:
#                 pass  # Expected if context is completely cleared
#
#     @patch("sys.stdout", new_callable=StringIO)
#     def test_teardown_appcontext_with_exception(self, mock_stdout):
#         """Test teardown_appcontext handler with exception."""
#         from flask import Flask, g
#
#         app = Flask(__name__)
#         init_logify(app, log_requests=True)
#
#         with app.test_request_context("/test"):
#             g.logify_request_id = "test-123"
#
#             # Get all teardown handlers
#             teardown_funcs = app.teardown_appcontext_funcs
#             assert len(teardown_funcs) > 0
#
#             # Call the last registered handler with exception
#             test_exception = ValueError("Test exception")
#             teardown_funcs[-1](test_exception)
#
#             # Check error log
#             output = mock_stdout.getvalue().strip()
#             if output:
#                 log_data = json.loads(output)
#                 assert "Request failed" in log_data["message"]
#                 assert log_data["error"] == "Test exception"
#
#
# class TestSetupFlaskLogging:
#     """Test Flask logging setup."""
#
#     def test_setup_flask_logging_default(self):
#         """Test Flask logging setup with defaults."""
#         # Should not raise any exceptions
#         setup_flask_logging()
#
#     def test_setup_flask_logging_custom_service(self):
#         """Test Flask logging setup with custom service."""
#         setup_flask_logging("custom-flask-service")
#
#
# class TestFlaskIntegration:
#     """Test Flask integration scenarios."""
#
#     @patch("sys.stdout", new_callable=StringIO)
#     def test_full_request_cycle(self, mock_stdout):
#         """Test full Flask request cycle with logging."""
#         from flask import Flask
#
#         from logify import error, info
#
#         app = Flask(__name__)
#         init_logify(app, service_name="flask-test-app", log_requests=True)
#
#         with app.test_request_context("/api/items/123", method="PUT", headers={"User-Agent": "FlaskClient/1.0"}):
#             # Simulate request cycle
#             with patch("time.time", side_effect=[1640995200.0, 1640995200.75]):  # Start and end times
#                 # 1. Before request
#                 before_request_handler = app.before_request_funcs[None][0]
#                 before_request_handler()
#
#                 # 2. Simulate route handler
#                 info("Updating item", item_id="123", user_id="user-456")
#
#                 # 3. Simulate some business logic
#                 info("Validating update data", validation_rules=["required", "format"])
#
#                 # 4. Simulate error
#                 try:
#                     raise PermissionError("User not authorized")
#                 except PermissionError as e:
#                     error("Authorization failed", error=e, required_permission="item.update")
#
#                 # 5. After request
#                 after_request_handler = app.after_request_funcs[None][0]
#                 response = MockFlaskResponse(status_code=403, content_length=50)
#                 after_request_handler(response)
#
#                 # 6. Teardown
#                 if None in app.teardown_appcontext_funcs:
#                     teardown_handler = app.teardown_appcontext_funcs[None][0]
#                     teardown_handler(None)
#
#             # Check logs
#             output = mock_stdout.getvalue().strip()
#             lines = [line for line in output.split("\n") if line.strip()]
#
#             # Should have: start, update, validation, error, completion logs
#             assert len(lines) >= 4
#
#             # Check request start log
#             start_log = json.loads(lines[0])
#             assert "Request started" in start_log["message"]
#             assert start_log["payload"]["method"] == "PUT"
#             assert start_log["payload"]["path"] == "/api/items/123"
#
#             # Check business logic logs contain request context
#             for i in range(1, len(lines) - 1):  # Skip start and end logs
#                 log_data = json.loads(lines[i])
#                 assert "request_id" in log_data["payload"]
#                 assert log_data["payload"]["method"] == "PUT"
#                 assert log_data["payload"]["path"] == "/api/items/123"
#
#             # Check error log
#             error_logs = [json.loads(line) for line in lines if "Authorization failed" in line]
#             assert len(error_logs) == 1
#             error_log = error_logs[0]
#             assert error_log["error"] == "User not authorized"
#             assert error_log["payload"]["required_permission"] == "item.update"
#
#             # Check completion log
#             completion_log = json.loads(lines[-1])
#             assert "Request completed" in completion_log["message"]
#             assert completion_log["payload"]["status_code"] == 403
#             assert completion_log["payload"]["duration_seconds"] == 0.75
#
#     def test_flask_without_request_logging(self):
#         """Test Flask integration without request logging."""
#         app = MockFlaskApp()
#         init_logify(app, log_requests=False)
#
#         # Handlers should still be registered
#         assert len(app.before_request_funcs) == 1
#         assert len(app.after_request_funcs) == 1
#         assert len(app.teardown_appcontext_funcs) == 1
#
#     def test_missing_request_attributes(self):
#         """Test handling of missing request attributes."""
#         from flask import Flask, g
#
#         app = Flask(__name__)
#         init_logify(app)
#
#         # Test with minimal request context (some attributes might be None)
#         with app.test_request_context("/", method="GET"):
#             # Should not raise exceptions
#             before_request_handler = app.before_request_funcs[None][0]
#             before_request_handler()
#
#             # Check that request ID was still set
#             assert hasattr(g, "logify_request_id")
