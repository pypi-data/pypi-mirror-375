# fk-util-tools

Utility tools and shared functions for FK projects: centralized configuration, logging, middlewares, AWS integration, and OpenTelemetry tracing for Python web frameworks.

## Installation

```bash
pip install fk-util-tools
```

## Main Features

- **Centralized Configuration**: `Config` class for global settings management.
- **Cache**: Redis integration.
- **Environment Variables & AWS**: Access to AWS Parameter Store and Secrets Manager.
- **Custom Exceptions**: HTTP error handling with custom codes.
- **Structured Logging**: Logging for FastAPI and other frameworks.
- **Middlewares**: SQL Printer, error handling, internationalization, and language support for Flask, Django, and FastAPI.
- **OpenTelemetry Tracing**: Instrumentation for Flask, Django, FastAPI, and AWS Lambda.
- **Type Hints**: PEP 561 support.

## Usage Examples

### Configuration

```python
from fk_utils import SETTINGS
print(SETTINGS.ENV)
```

### Structured Logging in FastAPI

```python
from fastapi import FastAPI
from fk_utils.logging.fastapi.logging import setup_logging

app = FastAPI()
setup_logging(app)
```

### SQL Printer Middleware

#### Flask

```python
from flask import Flask
from fk_utils.middlewares.flask.sql_middleware import SqlPrintingMiddleware

app = Flask(__name__)
app.config['DEBUG'] = True
SqlPrintingMiddleware(app)
```

#### Django

```python
from fk_utils.middlewares.django.sql_middleware import SqlPrintingMiddleware

SqlPrintingMiddleware()
```

#### FastAPI

```python
from fk_utils.middlewares.fastapi.sql_middleware import SqlPrintingMiddleware

app = FastAPI()
SqlPrintingMiddleware(app)
```

### OpenTelemetry Instrumentation

```python
from fk_utils.traces.opentelemetry.fastapi.trace import instrument_app

app = FastAPI()
instrument_app(app)
```

### AWS Lambda Instrumentation

```python
from fk_utils.traces.opentelemetry.fastapi.aws_lambda.trace import instrument_app

app = FastAPI()
is_lambda = instrument_app(app, instrument_lambda=True)
print("Lambda instrumented:", is_lambda)
```

## License

MIT
