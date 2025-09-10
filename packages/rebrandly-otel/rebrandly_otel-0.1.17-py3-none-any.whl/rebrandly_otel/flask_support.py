# flask_integration.py
"""Flask integration for Rebrandly OTEL SDK."""
from typing import TYPE_CHECKING
from opentelemetry.trace import Status, StatusCode, SpanKind

if TYPE_CHECKING:
    from .rebrandly_otel import RebrandlyOTEL

def setup_flask(otel: 'RebrandlyOTEL', app):
    """
    Setup Flask application with OTEL instrumentation.
    
    Example:
        from flask import Flask
        from rebrandly_otel import otel
        from rebrandly_otel.flask_integration import setup_flask
        
        app = Flask(__name__)
        setup_flask(otel, app)
    """
    app.before_request(lambda: app_before_request(otel))
    app.after_request(lambda response: app_after_request(otel, response))
    app.register_error_handler(Exception, lambda e: flask_error_handler(otel, e))
    return app

def app_before_request(otel: 'RebrandlyOTEL'):
    """
    Setup tracing for incoming Flask request.
    To be used with Flask's before_request hook.
    """
    from flask import request

    # Extract trace context from headers
    headers = dict(request.headers)
    token = otel.attach_context(headers)
    request.trace_token = token

    # Start span for request using start_as_current_span to make it the active span
    span = otel.tracer.tracer.start_as_current_span(
        f"{request.method} {request.path}",
        attributes={
            "http.method": request.method,
            "http.url": request.url,
            "http.path": request.path,
            "http.scheme": request.scheme,
            "http.host": request.host,
            "http.user_agent": request.user_agent.string if request.user_agent else '',
            "http.remote_addr": request.remote_addr,
            "http.target": request.path,
            "span.kind": "server"
        },
        kind=SpanKind.SERVER
    )
    # Store both the span context manager and the span itself
    request.span_context = span
    request.span = span.__enter__()  # This activates the span and returns the span object

    # Log request start
    otel.logger.logger.info(f"Request started: {request.method} {request.path}",
                            extra={"http.method": request.method, "http.path": request.path})

def app_after_request(otel: 'RebrandlyOTEL', response):
    """
    Cleanup tracing after Flask request completes.
    To be used with Flask's after_request hook.
    """
    from flask import request

    # Check if we have a span and it's still recording
    if hasattr(request, 'span') and request.span.is_recording():
        request.span.set_attribute("http.status_code", response.status_code)

        # Set span status based on HTTP status code
        if response.status_code >= 400:
            request.span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
            # Record error metric
            otel.meter.GlobalMetrics.error_invocations.add(1, {
                "endpoint": request.path,
                "method": request.method,
                "status_code": response.status_code
            })
        else:
            request.span.set_status(Status(StatusCode.OK))
            # Record success metric
            otel.meter.GlobalMetrics.successful_invocations.add(1, {
                "endpoint": request.path,
                "method": request.method
            })

        # Properly close the span context manager
        if hasattr(request, 'span_context'):
            request.span_context.__exit__(None, None, None)
        else:
            # Fallback if we don't have the context manager
            request.span.end()

    # Detach context
    if hasattr(request, 'trace_token'):
        otel.detach_context(request.trace_token)

    # Log request completion
    otel.logger.logger.info(f"Request completed: {response.status_code}",
                            extra={"http.status_code": response.status_code})

    # Record general invocation metric
    otel.meter.GlobalMetrics.invocations.add(1, {
        "endpoint": request.path,
        "method": request.method
    })

    return response

def flask_error_handler(otel: 'RebrandlyOTEL', exception):
    """
    Handle Flask exceptions and record them in the current span.
    To be used with Flask's errorhandler decorator.
    """
    from flask import request, jsonify
    from werkzeug.exceptions import HTTPException

    # Determine the status code
    if isinstance(exception, HTTPException):
        status_code = exception.code
    elif hasattr(exception, 'status_code'):
        status_code = exception.status_code
    elif hasattr(exception, 'code'):
        status_code = exception.code if isinstance(exception.code, int) else 500
    else:
        status_code = 500

    # Record exception in span if available and still recording
    if hasattr(request, 'span') and request.span.is_recording():
        request.span.set_attribute("http.status_code", status_code)
        request.span.set_attribute("error.type", type(exception).__name__)

        request.span.record_exception(exception)
        request.span.set_status(Status(StatusCode.ERROR, str(exception)))
        request.span.add_event("exception", {
            "exception.type": type(exception).__name__,
            "exception.message": str(exception),
            "http.status_code": status_code
        })

        # Only close the span if it's still recording (not already ended)
        if hasattr(request, 'span_context'):
            request.span_context.__exit__(type(exception), exception, None)
        else:
            request.span.end()

    # Log the error with status code
    otel.logger.logger.error(f"Unhandled exception: {exception} (status: {status_code})",
                             exc_info=True,
                             extra={
                                 "exception.type": type(exception).__name__,
                                 "http.status_code": status_code
                             })

    # Record error metric with status code
    otel.meter.GlobalMetrics.error_invocations.add(1, {
        "endpoint": request.path if hasattr(request, 'path') else 'unknown',
        "method": request.method if hasattr(request, 'method') else 'unknown',
        "error": type(exception).__name__,
        "status_code": status_code
    })

    # Return error response with the determined status code
    return jsonify({
        "error": str(exception),
        "type": type(exception).__name__
    }), status_code