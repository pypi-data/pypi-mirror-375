# """Tests for FastAPI integration."""
#
# import asyncio
# import json
# from io import StringIO
# from unittest.mock import MagicMock, patch
#
# import pytest
#
# from logify.fastapi import LogifyMiddleware, setup_fastapi_logging
#
#
# class MockFastAPIClient:
#     """Mock FastAPI client object."""
#
#     def __init__(self, host="127.0.0.1", port=8000):
#         self.host = host
#         self.port = port
#
#
# class MockFastAPIRequest:
#     """Mock FastAPI request object."""
#
#     def __init__(self, method="GET", path="/", query_params=None, headers=None, client=None):
#         self.method = method
#         self.url = MagicMock()
#         self.url.path = path
#         self.query_params = query_params or {}
#         self.headers = headers or {}
#         self.client = client or MockFastAPIClient()
#
#
# class MockFastAPIResponse:
#     """Mock FastAPI response object."""
#
#     def __init__(self, status_code=200, headers=None):
#         self.status_code = status_code
#         self.headers = headers or {}
#
#
# class TestLogifyMiddleware:
#     """Test FastAPI Logify middleware."""
#
#     def setup_method(self):
#         """Set up test fixtures."""
#         from logify.core import clear_request_context
#
#         clear_request_context()
#
#     @pytest.mark.asyncio
#     @patch("sys.stdout", new_callable=StringIO)
#     async def test_middleware_basic_request(self, mock_stdout):
#         """Test middleware with basic request."""
#
#         async def mock_call_next(request):
#             from logify import info
#
#             info("Processing FastAPI request")
#             return MockFastAPIResponse()
#
#         app = MagicMock()
#         middleware = LogifyMiddleware(app, service_name="test-fastapi", log_requests=True)
#         request = MockFastAPIRequest()
#
#         response = await middleware.dispatch(request, mock_call_next)
#
#         assert response.status_code == 200
#
#         # Check logs - should have start, processing, and completion logs
#         output = mock_stdout.getvalue().strip()
#         lines = output.split("\n")
#
#         # Filter out empty lines
#         lines = [line for line in lines if line.strip()]
#
#         assert len(lines) >= 2  # At least start and completion
#
#         # Check start log
#         start_log = json.loads(lines[0])
#         assert "Request started" in start_log["message"]
#         assert start_log["payload"]["method"] == "GET"
#         assert start_log["payload"]["path"] == "/"
#
#         # Check completion log (last line)
#         completion_log = json.loads(lines[-1])
#         assert "Request completed" in completion_log["message"]
#         assert "duration_seconds" in completion_log["payload"]
#         assert completion_log["payload"]["status_code"] == 200
#
#     @pytest.mark.asyncio
#     async def test_middleware_sets_request_context(self):
#         """Test that middleware sets request context."""
#         from logify.core import _request_context
#
#         async def mock_call_next(request):
#             # Check that context is set during request processing
#             try:
#                 context = _request_context.get()
#                 assert "request_id" in context
#                 assert context["method"] == "POST"
#                 assert context["path"] == "/api/users"
#                 assert context["client_host"] == "192.168.1.1"
#                 assert "user_agent" in context
#             except LookupError:
#                 pytest.fail("Request context not set")
#
#             return MockFastAPIResponse(201)
#
#         app = MagicMock()
#         middleware = LogifyMiddleware(app, service_name="test-api")
#
#         request = MockFastAPIRequest(
#             method="POST",
#             path="/api/users",
#             headers={"user-agent": "TestClient/1.0"},
#             client=MockFastAPIClient(host="192.168.1.1"),
#         )
#
#         response = await middleware.dispatch(request, mock_call_next)
#         assert response.status_code == 201
#
#     @pytest.mark.asyncio
#     async def test_middleware_clears_context_after_request(self):
#         """Test that middleware clears context after request."""
#         from logify.core import _request_context
#
#         async def mock_call_next(request):
#             return MockFastAPIResponse()
#
#         app = MagicMock()
#         middleware = LogifyMiddleware(app)
#         request = MockFastAPIRequest()
#
#         await middleware.dispatch(request, mock_call_next)
#
#         # Context should be cleared after request
#         try:
#             context = _request_context.get()
#             assert context == {}
#         except LookupError:
#             pass  # Expected if context is completely cleared
#
#     @pytest.mark.asyncio
#     @patch("sys.stdout", new_callable=StringIO)
#     async def test_middleware_handles_exception(self, mock_stdout):
#         """Test middleware handles exceptions."""
#
#         async def mock_call_next(request):
#             raise ValueError("Test async exception")
#
#         app = MagicMock()
#         middleware = LogifyMiddleware(app, log_requests=True)
#         request = MockFastAPIRequest()
#
#         with pytest.raises(ValueError):
#             await middleware.dispatch(request, mock_call_next)
#
#         # Check error log
#         output = mock_stdout.getvalue().strip()
#         lines = output.split("\n")
#         lines = [line for line in lines if line.strip()]
#
#         # Should have start and failure logs
#         assert len(lines) >= 2
#
#         failure_log = json.loads(lines[-1])
#         assert "Request failed" in failure_log["message"]
#         assert failure_log["error"] == "Test async exception"
#         assert failure_log["payload"]["error_type"] == "ValueError"
#         assert "duration_seconds" in failure_log["payload"]
#
#     @pytest.mark.asyncio
#     async def test_middleware_with_query_params(self):
#         """Test middleware with query parameters."""
#         from logify.core import _request_context
#
#         async def mock_call_next(request):
#             context = _request_context.get()
#             assert "query_params" in context
#             return MockFastAPIResponse()
#
#         app = MagicMock()
#         middleware = LogifyMiddleware(app)
#
#         # Mock query params
#         query_params = MagicMock()
#         query_params.__str__ = MagicMock(return_value="page=1&limit=10")
#
#         request = MockFastAPIRequest(query_params=query_params)
#
#         await middleware.dispatch(request, mock_call_next)
#
#     @pytest.mark.asyncio
#     async def test_middleware_without_logging(self):
#         """Test middleware with logging disabled."""
#
#         async def mock_call_next(request):
#             return MockFastAPIResponse()
#
#         app = MagicMock()
#         middleware = LogifyMiddleware(app, log_requests=False)
#         request = MockFastAPIRequest()
#
#         # Should work without raising exceptions
#         response = await middleware.dispatch(request, mock_call_next)
#         assert response.status_code == 200
#
#     @pytest.mark.asyncio
#     async def test_middleware_with_no_client(self):
#         """Test middleware when request has no client."""
#
#         async def mock_call_next(request):
#             return MockFastAPIResponse()
#
#         app = MagicMock()
#         middleware = LogifyMiddleware(app)
#
#         request = MockFastAPIRequest()
#         request.client = None
#
#         # Should handle gracefully
#         response = await middleware.dispatch(request, mock_call_next)
#         assert response.status_code == 200
#
#
# class TestSetupFastAPILogging:
#     """Test FastAPI logging setup."""
#
#     def test_setup_fastapi_logging_default(self):
#         """Test FastAPI logging setup with defaults."""
#         # Should not raise any exceptions
#         setup_fastapi_logging()
#
#     def test_setup_fastapi_logging_custom_service(self):
#         """Test FastAPI logging setup with custom service."""
#         setup_fastapi_logging("custom-fastapi-service")
#
#
# class TestFastAPIIntegration:
#     """Test FastAPI integration scenarios."""
#
#     @pytest.mark.asyncio
#     @patch("sys.stdout", new_callable=StringIO)
#     async def test_full_request_cycle(self, mock_stdout):
#         """Test full FastAPI request cycle with logging."""
#         from logify import error, info
#         from logify.core import clear_request_context, set_request_context
#
#         # Simulate FastAPI middleware setting context
#         set_request_context(
#             request_id="fastapi-req-456", method="GET", path="/api/items/123", client_host="192.168.1.100"
#         )
#
#         try:
#             # Simulate route handler processing
#             info("Fetching item", item_id="123")
#
#             # Simulate database query
#             info("Database query executed", table="items", query_time=0.025)
#
#             # Simulate error scenario
#             try:
#                 raise RuntimeError("Database connection failed")
#             except RuntimeError as e:
#                 error("Database error occurred", error=e, operation="fetch_item")
#
#             info("Request processed", status="error", response_time=0.150)
#
#         finally:
#             clear_request_context()
#
#         # Check logs
#         output = mock_stdout.getvalue().strip()
#         lines = output.split("\n")
#
#         assert len(lines) == 4
#
#         # Check each log contains request context
#         for line in lines:
#             log_data = json.loads(line)
#             assert log_data["payload"]["request_id"] == "fastapi-req-456"
#             assert log_data["payload"]["method"] == "GET"
#             assert log_data["payload"]["path"] == "/api/items/123"
#             assert log_data["payload"]["client_host"] == "192.168.1.100"
#
#         # Check specific log content
#         fetch_log = json.loads(lines[0])
#         assert "Fetching item" in fetch_log["message"]
#         assert fetch_log["payload"]["item_id"] == "123"
#
#         error_log = json.loads(lines[2])
#         assert "Database error occurred" in error_log["message"]
#         assert error_log["error"] == "Database connection failed"
#         assert error_log["payload"]["operation"] == "fetch_item"
#
#     @pytest.mark.asyncio
#     async def test_concurrent_requests(self):
#         """Test middleware with concurrent requests."""
#         from logify.core import _request_context
#
#         request_contexts = []
#
#         async def mock_call_next(request):
#             # Capture context during processing
#             try:
#                 context = _request_context.get()
#                 request_contexts.append(context.copy())
#             except LookupError:
#                 request_contexts.append({})
#
#             # Simulate some async work
#             await asyncio.sleep(0.01)
#             return MockFastAPIResponse()
#
#         app = MagicMock()
#         middleware = LogifyMiddleware(app)
#
#         # Create multiple requests
#         requests = [MockFastAPIRequest(path=f"/api/test/{i}") for i in range(3)]
#
#         # Process requests concurrently
#         tasks = [middleware.dispatch(req, mock_call_next) for req in requests]
#
#         responses = await asyncio.gather(*tasks)
#
#         # All requests should succeed
#         assert len(responses) == 3
#         assert all(r.status_code == 200 for r in responses)
#
#         # Each request should have its own context
#         assert len(request_contexts) == 3
#
#         # Request IDs should be unique
#         request_ids = [ctx.get("request_id") for ctx in request_contexts]
#         assert len(set(request_ids)) == 3  # All unique
