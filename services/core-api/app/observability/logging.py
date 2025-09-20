"""
ANZX AI Platform - Structured Logging Configuration
OpenTelemetry-compatible structured logging with Google Cloud Logging integration
"""

import os
import sys
import json
import logging
import structlog
from typing import Dict, Any, Optional
from datetime import datetime
from contextvars import ContextVar

# Context variables for request tracing
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
organization_id_var: ContextVar[Optional[str]] = ContextVar('organization_id', default=None)

class GoogleCloudLoggingProcessor:
    """Processor to format logs for Google Cloud Logging"""
    
    def __call__(self, logger, method_name, event_dict):
        # Add Google Cloud Logging fields
        event_dict["severity"] = event_dict.get("level", "INFO").upper()
        event_dict["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        # Add trace context if available
        request_id = request_id_var.get()
        if request_id:
            event_dict["trace"] = f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT', 'anzx-ai')}/traces/{request_id}"
            event_dict["spanId"] = request_id[:16]  # Use first 16 chars as span ID
        
        # Add user context
        user_id = user_id_var.get()
        if user_id:
            event_dict["userId"] = user_id
            
        org_id = organization_id_var.get()
        if org_id:
            event_dict["organizationId"] = org_id
        
        # Add service information
        event_dict["service"] = {
            "name": "anzx-core-api",
            "version": os.getenv("SERVICE_VERSION", "1.0.0"),
            "environment": os.getenv("ENVIRONMENT", "development")
        }
        
        return event_dict

class RequestContextProcessor:
    """Add request context to all log entries"""
    
    def __call__(self, logger, method_name, event_dict):
        # Add request context
        event_dict["requestId"] = request_id_var.get()
        event_dict["userId"] = user_id_var.get()
        event_dict["organizationId"] = organization_id_var.get()
        
        return event_dict

def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    enable_cloud_logging: bool = None
) -> None:
    """
    Set up structured logging with OpenTelemetry integration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Output format ('json' or 'console')
        enable_cloud_logging: Enable Google Cloud Logging format
    """
    
    # Determine if we should use cloud logging
    if enable_cloud_logging is None:
        enable_cloud_logging = os.getenv("ENVIRONMENT", "development") == "production"
    
    # Configure processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        RequestContextProcessor(),
    ]
    
    if enable_cloud_logging:
        processors.append(GoogleCloudLoggingProcessor())
    else:
        processors.extend([
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="ISO"),
        ])
    
    # Add final processor based on format
    if format_type == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )
    
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a structured logger instance
    
    Args:
        name: Logger name (defaults to calling module)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)

def set_request_context(
    request_id: str = None,
    user_id: str = None,
    organization_id: str = None
) -> None:
    """
    Set request context for logging
    
    Args:
        request_id: Unique request identifier
        user_id: User identifier
        organization_id: Organization identifier
    """
    if request_id:
        request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if organization_id:
        organization_id_var.set(organization_id)

def clear_request_context() -> None:
    """Clear request context"""
    request_id_var.set(None)
    user_id_var.set(None)
    organization_id_var.set(None)

class LoggingMiddleware:
    """FastAPI middleware for request logging"""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger("request")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        import uuid
        import time
        from fastapi import Request
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        set_request_context(request_id=request_id)
        
        # Create request object
        request = Request(scope, receive)
        
        # Log request start
        start_time = time.time()
        self.logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            user_agent=request.headers.get("user-agent"),
            client_ip=request.client.host if request.client else None,
        )
        
        # Process request
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Log response
                process_time = time.time() - start_time
                self.logger.info(
                    "Request completed",
                    status_code=message["status"],
                    process_time_ms=round(process_time * 1000, 2),
                    method=request.method,
                    path=request.url.path,
                )
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            self.logger.error(
                "Request failed",
                error=str(e),
                error_type=type(e).__name__,
                process_time_ms=round(process_time * 1000, 2),
                method=request.method,
                path=request.url.path,
            )
            raise
        finally:
            clear_request_context()

# Pre-configured loggers for different components
def get_api_logger() -> structlog.BoundLogger:
    """Get logger for API operations"""
    return get_logger("api")

def get_db_logger() -> structlog.BoundLogger:
    """Get logger for database operations"""
    return get_logger("database")

def get_ai_logger() -> structlog.BoundLogger:
    """Get logger for AI/ML operations"""
    return get_logger("ai")

def get_integration_logger() -> structlog.BoundLogger:
    """Get logger for third-party integrations"""
    return get_logger("integration")

def get_security_logger() -> structlog.BoundLogger:
    """Get logger for security events"""
    return get_logger("security")