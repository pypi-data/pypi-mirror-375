# json-logify

Universal structured logging with exact JSON schema for Python frameworks.

[![PyPI version](https://badge.fury.io/py/json-logify.svg)](https://badge.fury.io/py/json-logify)
[![Python Support](https://img.shields.io/pypi/pyversions/json-logify.svg)](https://pypi.org/project/json-logify/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Exact JSON Schema**: Consistent log format across all frameworks
- **High Performance**: Built with structlog and orjson for maximum speed
- **Universal**: Works with Django, FastAPI, Flask and standalone Python
- **Security First**: Automatic masking of sensitive data (passwords, tokens, etc.)
- **Easy Setup**: One-line configuration for most use cases
- **Rich Context**: Request IDs, user tracking, and custom payload support
- **Smart Filtering**: Configurable path ignoring and request/response body logging
- **Modern Python**: Full type hints and async support

## Quick Start

### Installation

```bash
# Basic installation
pip install json-logify

# For specific frameworks
pip install json-logify[django]
# pip install json-logify[fastapi]  # Coming soon
# pip install json-logify[flask]    # Coming soon

# Everything
pip install json-logify[all]
```

### Basic Usage

```python
from logify import info, error, debug, warning

# Basic logging with message
info("User logged in")

# With structured context
info("Payment processed", amount=100.0, currency="USD", user_id="user123")

# Different log levels
debug("Debug information", query_time=0.023)
warning("Slow database query detected", query_time=1.52, query_id="a1b2c3")
error("Payment failed", error_code="CARD_DECLINED", user_id="user123")

# Exception handling
try:
    # Some code that might fail
    result = some_function()
except Exception as e:
    error("Operation failed", exception=str(e), operation="some_function")
```

### Django Integration

#### 1. Install with Django extras:

```bash
pip install json-logify[django]
```

#### 2. Configure in settings.py:

```python
from logify.django import get_logging_config

# Add middleware to MIDDLEWARE list
MIDDLEWARE = [
    # ... other middleware
    'logify.django.LogifyMiddleware',  # ← Add this
]

# Configure logging with json-logify
LOGGING = get_logging_config(
    service_name="my-django-app",
    level="INFO",
    max_string_length=200,              # String truncation limit
    sensitive_fields=[                  # Fields to mask with "***"
        "password", "passwd", "secret", "token", "api_key",
        "access_token", "refresh_token", "session_key",
        "credit_card", "cvv", "ssn", "authorization",
        "cookie", "x-api-key", "custom_sensitive_field"
    ],
    ignore_paths=[                      # Paths to skip logging
        "/health/", "/static/", "/favicon.ico",
        "/admin/jsi18n/", "/metrics/"
    ]
)

# Optional: Reduce Django built-in logger noise
LOGGING['loggers'].update({
    'django.utils.autoreload': {'level': 'WARNING'},
    'django.db.backends': {'level': 'WARNING'},
    'django.server': {'level': 'WARNING'},
    'django.request': {'level': 'WARNING'},
})
```

#### 3. Use in your views:

```python
from logify import info, error, debug, warning
from django.http import JsonResponse

def process_payment(request):
    # Log with automatic request context
    info("Payment processing started",
         user_id=request.user.id,
         amount=request.POST.get('amount'))

    try:
        # Sensitive data gets automatically masked
        info("User data received",
             username=request.user.username,    # ← Visible
             password=request.POST.get('password'),  # ← Masked: "***"
             credit_card=request.POST.get('card'),   # ← Masked: "***"
             email=request.user.email)               # ← Visible

        # Your business logic
        payment = process_payment_logic(request.POST)

        # Log success
        info("Payment completed",
             payment_id=payment.id,
             status="success",
             amount=payment.amount)

        return JsonResponse({"status": "success", "payment_id": payment.id})

    except ValidationError as e:
        error("Payment validation failed", error=e, user_id=request.user.id)
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
    except Exception as e:
        error("Payment processing failed", error=e)
        return JsonResponse({"status": "error"}, status=500)
```

#### 4. What you get automatically:

**Request logging:**
```json
{
  "timestamp": "2025-09-09T08:09:35.933Z",
  "message": "Request started",
  "level": "INFO",
  "payload": {
    "request_id": "b62e59b6-bae7-4a96-821d",
    "service": "my-django-app",
    "method": "POST",
    "path": "/api/payment/",
    "user_info": "User ID: 123: john_doe",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "***",           // ← Automatically masked
      "User-Agent": "curl/8.7.1"
    },
    "request_body": {
      "username": "john_doe",
      "password": "***",                // ← Automatically masked
      "credit_card": "***"              // ← Automatically masked
    }
  }
}
```

**Your application logs:**
```json
{
  "timestamp": "2025-09-09T08:09:35.934Z",
  "message": "Payment completed",
  "level": "INFO",
  "payload": {
    "request_id": "b62e59b6-bae7-4a96-821d",  // ← Auto-linked to request
    "payment_id": "pay_123456",
    "status": "success",
    "amount": 99.99
  }
}
```

**🔒 Security Features:**
- **Automatic masking**: Passwords, tokens, API keys, credit cards → `"***"`
- **Header filtering**: Authorization, Cookie, X-API-Key → `"***"`
- **Recursive masking**: Works in nested objects and arrays
- **Request/Response body**: Limited size + content-type filtering
- **Path ignoring**: Skip health checks, static files, etc.
- Request and response bodies (with sensitive fields masked)

<!--
### FastAPI Integration (Coming Soon)

```python
from fastapi import FastAPI
from logify.fastapi import LogifyMiddleware

app = FastAPI()
app.add_middleware(LogifyMiddleware, service_name="myapi")

@app.get("/")
async def root():
    from logify import info
    info("API endpoint called", endpoint="/")
    return {"message": "Hello World"}
```

### Flask Integration (Coming Soon)

```python
from flask import Flask
from logify.flask import init_logify

app = Flask(__name__)
init_logify(app, service_name="myapp")

@app.route("/")
def hello():
    from logify import info
    info("Flask endpoint called", endpoint="/")
    return "Hello, World!"
```
-->

## Advanced Usage

### Context Management

```python
from logify import bind, set_request_context, clear_request_context

# Bind context to a logger
logger = bind(service="auth", module="login")
logger.info("Processing login", user_id="123")

# Set request-level context (useful in middleware)
set_request_context(request_id="req-456", user_id="123")
info("User action", action="view_profile")  # Includes request context
clear_request_context()
```

### Performance Tracking

```python
from logify import track_performance

@track_performance
def expensive_operation():
    # Your code here
    return "result"

# Automatically logs function start, completion, and duration
```

### Custom Configuration

```python
from logify import configure_logging

# Configure with custom settings
configure_logging(
    service_name="myapp",
    level="DEBUG"
)
```

## Log Schema

All logs follow this exact JSON schema:

```json
{
  "timestamp": "2025-01-15T10:30:00.123Z",
  "message": "Log message here",
  "level": "INFO",
  "error": "Error description (optional)",
  "payload": {
    "service": "myapp",
    "request_id": "req-123",
    "custom_field": "custom_value"
  }
}
```

The `error` field is optional and will only appear when logging errors or exceptions.

## Requirements

- Python 3.8+
- structlog >= 23.0.0
- orjson >= 3.8.0

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
