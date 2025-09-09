# """
# FastAPI integration for json-logify structured logging.
# """
#
# import time
#
# from fastapi import Request
# from starlette.middleware.base import BaseHTTPMiddleware
#
# from .core import clear_request_context, configure_logging, error, generate_request_id, info, set_request_context
#
#
# class LogifyMiddleware(BaseHTTPMiddleware):
#     """FastAPI middleware for structured logging with request context."""
#
#     def __init__(self, app, service_name: str = "fastapi", log_requests: bool = True):
#         super().__init__(app)
#         self.service_name = service_name
#         self.log_requests = log_requests
#         configure_logging(service_name=service_name)
#
#     async def dispatch(self, request: Request, call_next):
#         # Generate request ID and set context
#         request_id = generate_request_id()
#         start_time = time.time()
#
#         # Extract client info
#         client_host = getattr(request.client, "host", "unknown") if request.client else "unknown"
#
#         set_request_context(
#             request_id=request_id,
#             method=request.method,
#             path=request.url.path,
#             query_params=str(request.query_params) if request.query_params else None,
#             client_host=client_host,
#             user_agent=request.headers.get("user-agent", ""),
#         )
#
#         if self.log_requests:
#             info("Request started", method=request.method, path=request.url.path, request_id=request_id)
#
#         try:
#             response = await call_next(request)
#
#             duration = time.time() - start_time
#
#             # Add response info to context
#             set_request_context(status_code=response.status_code, duration_seconds=duration)
#
#             if self.log_requests:
#                 info(
#                     "Request completed",
#                     status_code=response.status_code,
#                     duration_seconds=duration,
#                     request_id=request_id,
#                 )
#
#             return response
#
#         except Exception as e:
#             duration = time.time() - start_time
#
#             if self.log_requests:
#                 error(
#                     "Request failed",
#                     error=e,
#                     duration_seconds=duration,
#                     request_id=request_id,
#                 )
#
#             raise
#
#         finally:
#             clear_request_context()
#
#
# def setup_fastapi_logging(service_name: str = "fastapi"):
#     """
#     Set up FastAPI logging with json-logify.
#     Call this when creating your FastAPI app.
#     """
#     configure_logging(service_name=service_name)
