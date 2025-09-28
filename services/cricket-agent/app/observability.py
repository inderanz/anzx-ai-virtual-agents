"""
Cricket Agent Observability
Structured logging, metrics, and monitoring setup with OpenTelemetry integration
"""

import logging
import sys
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog
from google.cloud import logging as cloud_logging
try:
    from google.cloud import error_reporting
except ImportError:
    error_reporting = None
from opentelemetry import trace
from opentelemetry import metrics
try:
    from opentelemetry.exporter.cloud_monitoring import CloudMonitoringMetricsExporter
except ImportError:
    CloudMonitoringMetricsExporter = None
try:
    from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
except ImportError:
    CloudTraceSpanExporter = None
try:
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
except ImportError:
    TracerProvider = None
    BatchSpanProcessor = None
    MeterProvider = None
    PeriodicExportingMetricReader = None
try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
except ImportError:
    FastAPIInstrumentor = None

try:
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
except ImportError:
    HTTPXClientInstrumentor = None

try:
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
except ImportError:
    RequestsInstrumentor = None

def setup_logging():
    """Setup structured logging for the cricket agent"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        stream=sys.stdout
    )

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)

class CricketAgentMetrics:
    """Enhanced metrics collection for cricket agent with OpenTelemetry"""
    
    def __init__(self):
        # Basic counters
        self.request_count = 0
        self.error_count = 0
        self.total_latency_ms = 0
        self.playhq_api_calls = 0
        self.vector_store_queries = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Latency tracking for p95 calculation
        self.latency_samples: List[int] = []
        
        # Intent tracking
        self.intent_counts: Dict[str, int] = {}
        
        # Token usage tracking
        self.tokens_in = 0
        self.tokens_out = 0
        
        # Error tracking by type
        self.error_types: Dict[str, int] = {}
        
        # Setup OpenTelemetry
        self._setup_telemetry()
    
    def _setup_telemetry(self):
        """Setup OpenTelemetry tracing and metrics"""
        try:
            # Setup tracing
            trace.set_tracer_provider(TracerProvider())
            tracer = trace.get_tracer(__name__)
            
            # Setup metrics
            self.meter = metrics.get_meter(__name__)
            
            # Create custom metrics
            self.request_counter = self.meter.create_counter(
                name="cricket_agent_requests_total",
                description="Total number of requests"
            )
            
            self.error_counter = self.meter.create_counter(
                name="cricket_agent_errors_total",
                description="Total number of errors"
            )
            
            self.latency_histogram = self.meter.create_histogram(
                name="cricket_agent_request_duration_ms",
                description="Request duration in milliseconds"
            )
            
            self.playhq_counter = self.meter.create_counter(
                name="cricket_agent_playhq_calls_total",
                description="Total PlayHQ API calls"
            )
            
            self.vector_counter = self.meter.create_counter(
                name="cricket_agent_vector_queries_total",
                description="Total vector store queries"
            )
            
            self.token_counter = self.meter.create_counter(
                name="cricket_agent_tokens_total",
                description="Total tokens processed"
            )
            
        except Exception as e:
            # Fallback if OpenTelemetry setup fails
            logging.warning(f"OpenTelemetry setup failed: {e}")
    
    def record_request(self, latency_ms: int, success: bool = True, intent: str = None, tokens_in: int = 0, tokens_out: int = 0):
        """Record a request metric with enhanced tracking"""
        self.request_count += 1
        self.total_latency_ms += latency_ms
        self.latency_samples.append(latency_ms)
        
        # Keep only last 1000 samples for p95 calculation
        if len(self.latency_samples) > 1000:
            self.latency_samples = self.latency_samples[-1000:]
        
        # Track tokens
        self.tokens_in += tokens_in
        self.tokens_out += tokens_out
        
        # Track intent
        if intent:
            self.intent_counts[intent] = self.intent_counts.get(intent, 0) + 1
        
        if not success:
            self.error_count += 1
        
        # Record OpenTelemetry metrics
        try:
            self.request_counter.add(1, {"success": str(success), "intent": intent or "unknown"})
            self.latency_histogram.record(latency_ms, {"intent": intent or "unknown"})
            if tokens_in > 0 or tokens_out > 0:
                self.token_counter.add(tokens_in + tokens_out, {"type": "total"})
        except Exception:
            pass  # Ignore telemetry errors
    
    def record_playhq_call(self, endpoint: str = None, status_code: int = None):
        """Record a PlayHQ API call with enhanced tracking"""
        self.playhq_api_calls += 1
        
        try:
            self.playhq_counter.add(1, {
                "endpoint": endpoint or "unknown",
                "status_code": str(status_code) if status_code else "unknown"
            })
        except Exception:
            pass
    
    def record_vector_query(self, query_type: str = None):
        """Record a vector store query with enhanced tracking"""
        self.vector_store_queries += 1
        
        try:
            self.vector_counter.add(1, {"query_type": query_type or "unknown"})
        except Exception:
            pass
    
    def record_cache_hit(self):
        """Record a cache hit"""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record a cache miss"""
        self.cache_misses += 1
    
    def record_error(self, error_type: str, error_message: str = None):
        """Record an error with type tracking"""
        self.error_count += 1
        self.error_types[error_type] = self.error_types.get(error_type, 0) + 1
        
        try:
            self.error_counter.add(1, {
                "error_type": error_type,
                "error_message": error_message or "unknown"
            })
        except Exception:
            pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics including p95 latency"""
        avg_latency = self.total_latency_ms / max(self.request_count, 1)
        error_rate = self.error_count / max(self.request_count, 1)
        cache_hit_rate = self.cache_hits / max(self.cache_hits + self.cache_misses, 1)
        
        # Calculate p95 latency
        p95_latency = 0
        if self.latency_samples:
            sorted_samples = sorted(self.latency_samples)
            p95_index = int(len(sorted_samples) * 0.95)
            p95_latency = sorted_samples[p95_index] if p95_index < len(sorted_samples) else sorted_samples[-1]
        
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": error_rate,
            "avg_latency_ms": avg_latency,
            "p95_latency_ms": p95_latency,
            "playhq_api_calls": self.playhq_api_calls,
            "vector_store_queries": self.vector_store_queries,
            "cache_hit_rate": cache_hit_rate,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "intent_counts": self.intent_counts,
            "error_types": self.error_types
        }

# Global metrics instance
_metrics = CricketAgentMetrics()

def get_metrics() -> CricketAgentMetrics:
    """Get the global metrics instance"""
    return _metrics

def log_request_start(request_id: str, method: str, path: str, **kwargs):
    """Log the start of a request"""
    logger = get_logger("cricket_agent.request")
    logger.info(
        "Request started",
        request_id=request_id,
        method=method,
        path=path,
        **kwargs
    )

def log_request_end(request_id: str, status_code: int, latency_ms: int, **kwargs):
    """Log the end of a request"""
    logger = get_logger("cricket_agent.request")
    
    # Record metrics
    _metrics.record_request(latency_ms, status_code < 400)
    
    logger.info(
        "Request completed",
        request_id=request_id,
        status_code=status_code,
        latency_ms=latency_ms,
        **kwargs
    )

def log_cricket_query(request_id: str, query: str, intent: str, source: str, rag_ms: int = 0, api_ms: int = 0, tokens_in: int = 0, tokens_out: int = 0, **kwargs):
    """Log a cricket query with enhanced metrics"""
    logger = get_logger("cricket_agent.query")
    
    # Record metrics
    _metrics.record_request(
        latency_ms=rag_ms + api_ms,
        success=True,
        intent=intent,
        tokens_in=tokens_in,
        tokens_out=tokens_out
    )
    
    logger.info(
        "Cricket query received",
        request_id=request_id,
        query=query[:100],  # Truncate for privacy
        intent=intent,
        source=source,
        rag_ms=rag_ms,
        api_ms=api_ms,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        **kwargs
    )

def log_playhq_api_call(request_id: str, endpoint: str, status_code: int, latency_ms: int, **kwargs):
    """Log a PlayHQ API call"""
    logger = get_logger("cricket_agent.playhq")
    _metrics.record_playhq_call()
    
    logger.info(
        "PlayHQ API call",
        request_id=request_id,
        endpoint=endpoint,
        status_code=status_code,
        latency_ms=latency_ms,
        **kwargs
    )

def log_vector_query(request_id: str, query: str, results_count: int, latency_ms: int, **kwargs):
    """Log a vector store query"""
    logger = get_logger("cricket_agent.vector")
    _metrics.record_vector_query()
    
    logger.info(
        "Vector store query",
        request_id=request_id,
        query=query[:100],  # Truncate for privacy
        results_count=results_count,
        latency_ms=latency_ms,
        **kwargs
    )

def log_agent_response(request_id: str, response: str, intent: str, latency_ms: int, **kwargs):
    """Log an agent response"""
    logger = get_logger("cricket_agent.response")
    
    logger.info(
        "Agent response generated",
        request_id=request_id,
        response=response[:200],  # Truncate for privacy
        intent=intent,
        latency_ms=latency_ms,
        **kwargs
    )

def log_error(request_id: str, error: Exception, context: Dict[str, Any] = None):
    """Log an error"""
    logger = get_logger("cricket_agent.error")
    
    logger.error(
        "Error occurred",
        request_id=request_id,
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {}
    )

def log_data_refresh(scope: str, updated_count: int, duration_ms: int, **kwargs):
    """Log a data refresh operation"""
    logger = get_logger("cricket_agent.refresh")
    
    logger.info(
        "Data refresh completed",
        scope=scope,
        updated_count=updated_count,
        duration_ms=duration_ms,
        **kwargs
    )

def setup_observability():
    """Setup comprehensive observability including OpenTelemetry and error reporting"""
    try:
        # Setup structured logging
        setup_logging()
        
        # Setup Google Cloud Logging
        client = cloud_logging.Client()
        client.setup_logging()
        
        # Setup error reporting
        error_client = error_reporting.Client()
        
        # Setup OpenTelemetry
        _setup_telemetry()
        
        logger = get_logger("cricket_agent.observability")
        logger.info("Observability setup completed")
        
    except Exception as e:
        logging.error(f"Failed to setup observability: {e}")

def _setup_telemetry():
    """Setup OpenTelemetry tracing and metrics"""
    try:
        # Setup tracing (if available)
        if TracerProvider is not None:
            trace.set_tracer_provider(TracerProvider())
            tracer = trace.get_tracer(__name__)
            
            # Add Cloud Trace exporter (if available)
            if CloudTraceSpanExporter is not None and BatchSpanProcessor is not None:
                cloud_trace_exporter = CloudTraceSpanExporter()
                span_processor = BatchSpanProcessor(cloud_trace_exporter)
                trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Setup metrics (if available)
        if MeterProvider is not None:
            if CloudMonitoringMetricsExporter is not None and PeriodicExportingMetricReader is not None:
                cloud_monitoring_exporter = CloudMonitoringMetricsExporter()
                metric_reader = PeriodicExportingMetricReader(cloud_monitoring_exporter)
                meter_provider = MeterProvider(metric_readers=[metric_reader])
                metrics.set_meter_provider(meter_provider)
            else:
                # Fallback to basic metrics without cloud monitoring
                meter_provider = MeterProvider()
                metrics.set_meter_provider(meter_provider)
        
        # Instrument HTTP clients (if available)
        if HTTPXClientInstrumentor is not None:
            HTTPXClientInstrumentor().instrument()
        if RequestsInstrumentor is not None:
            RequestsInstrumentor().instrument()
        
    except Exception as e:
        logging.warning(f"OpenTelemetry setup failed: {e}")

def instrument_fastapi(app):
    """Instrument FastAPI app with OpenTelemetry"""
    try:
        if FastAPIInstrumentor is not None:
            FastAPIInstrumentor.instrument_app(app)
    except Exception as e:
        logging.warning(f"FastAPI instrumentation failed: {e}")

def report_error(error: Exception, context: Dict[str, Any] = None):
    """Report error to Google Cloud Error Reporting"""
    if error_reporting is None:
        logging.warning("Error reporting not available")
        return
        
    try:
        error_client = error_reporting.Client()
        error_client.report_exception(
            http_context=context.get('http_context') if context else None,
            user=context.get('user') if context else None
        )
    except Exception as e:
        logging.warning(f"Failed to report error: {e}")

def get_prometheus_metrics() -> str:
    """Get metrics in Prometheus format"""
    metrics = _metrics.get_metrics()
    
    prometheus_lines = []
    
    # Request metrics
    prometheus_lines.append(f"# HELP cricket_agent_requests_total Total number of requests")
    prometheus_lines.append(f"# TYPE cricket_agent_requests_total counter")
    prometheus_lines.append(f"cricket_agent_requests_total {metrics['request_count']}")
    
    # Error metrics
    prometheus_lines.append(f"# HELP cricket_agent_errors_total Total number of errors")
    prometheus_lines.append(f"# TYPE cricket_agent_errors_total counter")
    prometheus_lines.append(f"cricket_agent_errors_total {metrics['error_count']}")
    
    # Latency metrics
    prometheus_lines.append(f"# HELP cricket_agent_avg_latency_ms Average request latency in milliseconds")
    prometheus_lines.append(f"# TYPE cricket_agent_avg_latency_ms gauge")
    prometheus_lines.append(f"cricket_agent_avg_latency_ms {metrics['avg_latency_ms']:.2f}")
    
    prometheus_lines.append(f"# HELP cricket_agent_p95_latency_ms 95th percentile latency in milliseconds")
    prometheus_lines.append(f"# TYPE cricket_agent_p95_latency_ms gauge")
    prometheus_lines.append(f"cricket_agent_p95_latency_ms {metrics['p95_latency_ms']}")
    
    # API call metrics
    prometheus_lines.append(f"# HELP cricket_agent_playhq_calls_total Total PlayHQ API calls")
    prometheus_lines.append(f"# TYPE cricket_agent_playhq_calls_total counter")
    prometheus_lines.append(f"cricket_agent_playhq_calls_total {metrics['playhq_api_calls']}")
    
    prometheus_lines.append(f"# HELP cricket_agent_vector_queries_total Total vector store queries")
    prometheus_lines.append(f"# TYPE cricket_agent_vector_queries_total counter")
    prometheus_lines.append(f"cricket_agent_vector_queries_total {metrics['vector_store_queries']}")
    
    # Token metrics
    prometheus_lines.append(f"# HELP cricket_agent_tokens_in_total Total input tokens")
    prometheus_lines.append(f"# TYPE cricket_agent_tokens_in_total counter")
    prometheus_lines.append(f"cricket_agent_tokens_in_total {metrics['tokens_in']}")
    
    prometheus_lines.append(f"# HELP cricket_agent_tokens_out_total Total output tokens")
    prometheus_lines.append(f"# TYPE cricket_agent_tokens_out_total counter")
    prometheus_lines.append(f"cricket_agent_tokens_out_total {metrics['tokens_out']}")
    
    # Cache metrics
    prometheus_lines.append(f"# HELP cricket_agent_cache_hit_rate Cache hit rate")
    prometheus_lines.append(f"# TYPE cricket_agent_cache_hit_rate gauge")
    prometheus_lines.append(f"cricket_agent_cache_hit_rate {metrics['cache_hit_rate']:.4f}")
    
    return "\n".join(prometheus_lines)
