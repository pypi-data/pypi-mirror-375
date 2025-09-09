# """
# Flask integration for json-logify structured logging.
# """
#
# import time
#
# from flask import Flask, g, request
#
# from .core import clear_request_context, configure_logging, error, generate_request_id, info, set_request_context
#
#
# def init_logify(app: Flask, service_name: str = "flask", log_requests: bool = True):
#     """
#     Initialize json-logify for Flask application.
#
#     Usage:
#         from flask import Flask
#         from logify.flask import init_logify
#
#         app = Flask(__name__)
#         init_logify(app, service_name="myapp")
#     """
#     configure_logging(service_name=service_name)
#
#     @app.before_request
#     def before_request():
#         # Generate request ID and set context
#         request_id = generate_request_id()
#         g.logify_request_id = request_id
#         g.logify_start_time = time.time()
#
#         set_request_context(
#             request_id=request_id,
#             method=request.method,
#             path=request.path,
#             query_string=request.query_string.decode() if request.query_string else None,
#             remote_addr=request.remote_addr,
#             user_agent=request.headers.get("User-Agent", ""),
#         )
#
#         if log_requests:
#             info("Request started", method=request.method, path=request.path, request_id=request_id)
#
#     @app.after_request
#     def after_request(response):
#         try:
#             # Calculate duration
#             duration = time.time() - g.logify_start_time
#
#             # Add response info to context
#             set_request_context(
#                 status_code=response.status_code, duration_seconds=duration, content_length=response.content_length
#             )
#
#             if log_requests:
#                 info(
#                     "Request completed",
#                     status_code=response.status_code,
#                     duration_seconds=duration,
#                     request_id=g.logify_request_id,
#                 )
#         except Exception:
#             # If we can't access g, just return the response
#             pass
#
#         return response
#
#     def teardown_request(exception):
#         # Clear request context
#         clear_request_context()
#
#         if exception and log_requests:
#             error(
#                 "Request failed",
#                 error=exception,
#                 request_id=getattr(g, "logify_request_id", "unknown"),
#             )
#
#     # Register teardown function
#     app.teardown_appcontext(teardown_request)
#
#
# def setup_flask_logging(service_name: str = "flask"):
#     """
#     Set up Flask logging with json-logify.
#     Call this when creating your Flask app.
#     """
#     configure_logging(service_name=service_name)
