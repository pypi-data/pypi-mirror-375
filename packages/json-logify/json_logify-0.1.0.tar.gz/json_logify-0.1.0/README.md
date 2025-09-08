# json-logify

Universal structured logging with exact JSON schema for Python frameworks.

[![PyPI version](https://badge.fury.io/py/json-logify.svg)](https://badge.fury.io/py/json-logify)
[![Python Support](https://img.shields.io/pypi/pyversions/json-logify.svg)](https://pypi.org/project/json-logify/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- <� **Exact JSON Schema**: Consistent log format across all frameworks
- � **High Performance**: Built with structlog and orjson for maximum speed
- < **Universal**: Works with Django, FastAPI, Flask, and standalone Python
- =' **Easy Setup**: One-line configuration for most use cases
- =� **Rich Context**: Request IDs, user tracking, and custom payload support
- = **Modern Python**: Full type hints and async support

## Quick Start

### Installation

```bash
# Basic installation
pip install json-logify

# For specific frameworks
pip install json-logify[django]
pip install json-logify[fastapi]
pip install json-logify[flask]

# Everything
pip install json-logify[all]
```

### Basic Usage

```python
from logify import info, error

# Simple logging
info("User logged in", user_id="12345", action="login")

# Error logging with exception
try:
    raise ValueError("Something went wrong")
except Exception as e:
    error("Operation failed", error=e, operation="data_processing")
```

Output:
```json
{
  "timestamp": "2025-01-15T10:30:00.123Z",
  "message": "User logged in",
  "level": "INFO",
  "payload": {
    "user_id": "12345",
    "action": "login"
  }
}
```

### Django Integration

```python
# settings.py
from logify.django import get_logging_config

LOGGING = get_logging_config(
    service_name="myapp",
    json_logs=True
)

# Add middleware (optional for request tracking)
MIDDLEWARE = [
    'logify.django.LogifyMiddleware',
    # ... other middleware
]
```

### FastAPI Integration

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

### Flask Integration

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
