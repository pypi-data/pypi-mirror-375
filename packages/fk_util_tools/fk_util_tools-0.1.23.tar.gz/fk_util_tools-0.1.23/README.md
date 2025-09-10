# package-utils

Utilidades y herramientas compartidas para proyectos FK: configuración, logging, middlewares, integración con AWS y trazas OpenTelemetry para frameworks web en Python.

## Instalación

```bash
pip install fk-util-tools
```

## Características principales

- **Configuración centralizada**: Clase `Config` para gestionar settings globales.
- **Cache**: Integración con Redis.
- **Variables de entorno y AWS**: Acceso a parámetros y secretos en AWS Parameter Store y Secrets Manager.
- **Excepciones personalizadas**: Manejo de errores HTTP customizados.
- **Logging estructurado**: Logging para FastAPI y otros frameworks.
- **Middlewares**: SQL Printer, manejo de errores, internacionalización y lenguaje para Flask, Django y FastAPI.
- **Trazas OpenTelemetry**: Instrumentación para Flask, Django, FastAPI y AWS Lambda.
- **Tipado**: Soporte para type hints (PEP 561).

## Ejemplo de uso: Configuración

```python
from fk_utils import SETTINGS
print(SETTINGS.ENV)
```

## Ejemplo de uso: Logging estructurado en FastAPI

```python
from fastapi import FastAPI
from fk_utils.logging.fastapi.logging import setup_logging

app = FastAPI()
setup_logging(app)
```

## Ejemplo de uso: Middleware SQL Printer

### Flask
```python
from flask import Flask
from fk_utils.middlewares.flask.sql_middleware import SqlPrintingMiddleware
app = Flask(__name__)
app.config['DEBUG'] = True
SqlPrintingMiddleware(app)
```

### Django
```python
MIDDLEWARE = [
    'fk_utils.middlewares.django.sql_middleware.SqlPrintingMiddleware',
]
```

### FastAPI
```python
from fastapi import FastAPI
from fk_utils.middlewares.fastapi.sql_middleware import SqlPrintingMiddleware
app = FastAPI()
app.add_middleware(SqlPrintingMiddleware, debug=True)
```

## Ejemplo de uso: AWS Parameter Store y Secrets Manager

```python
from fk_utils.envs.aws.parameters import get_parameter
from fk_utils.envs.aws.secrets import get_secret
param = get_parameter('my-param')
secret = get_secret('my-secret')
```

## Ejemplo de uso: Instrumentación OpenTelemetry

### FastAPI + AWS Lambda
```python
from fk_utils.traces.opentelemetry.fastapi.aws_lambda.trace import instrument_app
instrument_app(app, instrument_lambda=True)
```

### Flask
```python
from fk_utils.traces.opentelemetry.flask.trace import instrument_app
instrument_app(app)
```

### Django
```python
from fk_utils.traces.opentelemetry.django.trace import instrument_app
instrument_app()
```

## Ejemplo de uso: Excepciones personalizadas

```python
from fk_utils.exceptions.custom_http_exception import CustomHTTPException
raise CustomHTTPException(status_code=400, detail="Bad request")
```

## Compatibilidad
- Python >=3.10
- Compatible con Flask, Django, FastAPI
- Integración con AWS y OpenTelemetry

## Licencia
MIT
