"""
ANZX AI Platform - Distributed Tracing
OpenTelemetry distributed tracing with Google Cloud Trace integration
"""

import os
import functools
from typing import Dict, Any, Optional, Callable
from contextvars import ContextVar

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.propagators.cloud_trace import CloudTraceFormatPropagator
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes

# Context variable for current span
current_span_var: ContextVar[Optional[trace.Span]] = ContextVar('current_span', default=None)

def setup_tracing(
    service_name: str = "anzx-core-api",
    service_version: str = "1.0.0",
    environment: str = None,
    enable_cloud_trace: bool = None,
    enable_jaeger: bool = False,
    jaeger_endpoint: str = "http://localhost:14268/api/traces"
) -> trace.Tracer:
    """
    Set up OpenTelemetry distributed tracing
    
    Args:
        service_name: Name of the service
        service_version: Version of the service
        environment: Environment (development, staging, production)
        enable_cloud_trace: Enable Google Cloud Trace export
        enable_jaeger: Enable Jaeger export for local development
        jaeger_endpoint: Jaeger collector endpoint
        
    Returns:
        Configured tracer instance
    """
    
    # Determine environment and cloud trace settings
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")
    
    if enable_cloud_trace is None:
        enable_cloud_trace = environment == "production"
    
    # Create resource
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: service_name,
        ResourceAttributes.SERVICE_VERSION: service_version,
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: environment,
        ResourceAttributes.CLOUD_PROVIDER: "gcp",
        ResourceAttributes.CLOUD_PLATFORM: "gcp_cloud_run",
        ResourceAttributes.CLOUD_REGION: os.getenv("GOOGLE_CLOUD_REGION", "australia-southeast1"),
    })
    
    # Set up tracer provider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    
    # Add exporters
    if enable_cloud_trace:
        # Google Cloud Trace exporter
        cloud_trace_exporter = CloudTraceSpanExporter(
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT")
        )
        tracer_provider.add_span_processor(
            BatchSpanProcessor(cloud_trace_exporter)
        )
        
        # Set Cloud Trace propagator
        trace.set_tracer_provider(tracer_provider)
        from opentelemetry.propagate import set_global_textmap
        set_global_textmap(CloudTraceFormatPropagator())
    
    if enable_jaeger:
        # Jaeger exporter for local development
        jaeger_exporter = JaegerExporter(
            endpoint=jaeger_endpoint,
        )
        tracer_provider.add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
    
    # Auto-instrument libraries
    FastAPIInstrumentor.instrument()
    SQLAlchemyInstrumentor.instrument()
    HTTPXClientInstrumentor.instrument()
    RedisInstrumentor.instrument()
    
    # Get tracer
    tracer = trace.get_tracer(service_name, service_version)
    
    return tracer

def get_tracer(name: str = None) -> trace.Tracer:
    """
    Get a tracer instance
    
    Args:
        name: Tracer name (defaults to service name)
        
    Returns:
        Tracer instance
    """
    return trace.get_tracer(name or "anzx-core-api")

def trace_request(
    operation_name: str = None,
    attributes: Dict[str, Any] = None
):
    """
    Decorator to trace function calls
    
    Args:
        operation_name: Name of the operation (defaults to function name)
        attributes: Additional span attributes
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()
            span_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(span_name) as span:
                # Set current span in context
                current_span_var.set(span)
                
                # Add default attributes
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(
                        trace.Status(
                            trace.StatusCode.ERROR,
                            description=str(e)
                        )
                    )
                    span.record_exception(e)
                    raise
                finally:
                    current_span_var.set(None)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = get_tracer()
            span_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(span_name) as span:
                # Set current span in context
                current_span_var.set(span)
                
                # Add default attributes
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(
                        trace.Status(
                            trace.StatusCode.ERROR,
                            description=str(e)
                        )
                    )
                    span.record_exception(e)
                    raise
                finally:
                    current_span_var.set(None)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def add_span_attribute(key: str, value: Any) -> None:
    """
    Add attribute to current span
    
    Args:
        key: Attribute key
        value: Attribute value
    """
    span = current_span_var.get()
    if span:
        span.set_attribute(key, value)

def add_span_event(name: str, attributes: Dict[str, Any] = None) -> None:
    """
    Add event to current span
    
    Args:
        name: Event name
        attributes: Event attributes
    """
    span = current_span_var.get()
    if span:
        span.add_event(name, attributes or {})

def record_exception(exception: Exception) -> None:
    """
    Record exception in current span
    
    Args:
        exception: Exception to record
    """
    span = current_span_var.get()
    if span:
        span.record_exception(exception)

class TracingMiddleware:
    """FastAPI middleware for enhanced tracing"""
    
    def __init__(self, app):
        self.app = app
        self.tracer = get_tracer()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        from fastapi import Request
        request = Request(scope, receive)
        
        # Create span for request
        with self.tracer.start_as_current_span(
            f"{request.method} {request.url.path}"
        ) as span:
            # Add request attributes
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("http.scheme", request.url.scheme)
            span.set_attribute("http.host", request.url.hostname)
            span.set_attribute("http.target", request.url.path)
            span.set_attribute("user_agent.original", request.headers.get("user-agent", ""))
            
            if request.client:
                span.set_attribute("client.address", request.client.host)
                span.set_attribute("client.port", request.client.port)
            
            # Process request
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                    span.set_attribute("http.status_code", status_code)
                    
                    # Set span status based on HTTP status
                    if status_code >= 400:
                        span.set_status(
                            trace.Status(
                                trace.StatusCode.ERROR,
                                description=f"HTTP {status_code}"
                            )
                        )
                    else:
                        span.set_status(trace.Status(trace.StatusCode.OK))
                
                await send(message)
            
            try:
                await self.app(scope, receive, send_wrapper)
            except Exception as e:
                span.record_exception(e)
                span.set_status(
                    trace.Status(
                        trace.StatusCode.ERROR,
                        description=str(e)
                    )
                )
                raise

# Specialized tracing decorators
def trace_ai_operation(operation_name: str = None):
    """Decorator for AI/ML operations"""
    return trace_request(
        operation_name=operation_name,
        attributes={"component": "ai", "operation.type": "ai_inference"}
    )

def trace_db_operation(operation_name: str = None):
    """Decorator for database operations"""
    return trace_request(
        operation_name=operation_name,
        attributes={"component": "database", "operation.type": "db_query"}
    )

def trace_integration_operation(service: str, operation_name: str = None):
    """Decorator for third-party integration operations"""
    return trace_request(
        operation_name=operation_name,
        attributes={
            "component": "integration",
            "integration.service": service,
            "operation.type": "external_api"
        }
    )