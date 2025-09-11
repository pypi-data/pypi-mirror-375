# src/__init__.py
from .rebrandly_otel import *
from .flask_support import setup_flask
from .fastapi_support import setup_fastapi

# Explicitly define what's available
__all__ = [
    'lambda_handler',
    'span',
    'aws_message_span',
    'traces',
    'tracer',
    'metrics',
    'logger',
    'force_flush',
    'aws_message_handler',
    'shutdown',
    'setup_flask',
    'setup_fastapi'
]