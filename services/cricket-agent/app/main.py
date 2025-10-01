"""
Caroline Springs CC Cricket Agent
Main FastAPI application entry point
"""

import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from .config import get_settings
from .observability import setup_logging, get_logger, get_prometheus_metrics, setup_observability, instrument_fastapi
from .webhook_handler import process_webhook
from .webhook_models import WebhookResponse

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Request/Response Models
class AskRequest(BaseModel):
    text: str = Field(..., description="User query text")
    source: Optional[str] = Field(None, description="Source channel (web, whatsapp)")
    team_hint: Optional[str] = Field(None, description="Optional team hint for context")

class AskResponse(BaseModel):
    answer: str = Field(..., description="Agent response")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")

class RefreshRequest(BaseModel):
    scope: str = Field("all", description="Refresh scope: all, team, match, ladder")
    id: Optional[str] = Field(None, description="Specific ID for targeted refresh")

class RefreshResponse(BaseModel):
    status: str = Field(..., description="Refresh status")
    message: str = Field(..., description="Status message")
    updated_count: int = Field(0, description="Number of records updated")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Caroline Springs CC Cricket Agent")
    
    # Setup observability
    setup_observability()
    instrument_fastapi(app)
    
    try:
        # Initialize services
        settings = get_settings()
        logger.info(f"Configuration loaded: {settings.app_env}")
        
        # Initialize PlayHQ client
        # TODO: Initialize PlayHQ client with credentials
        
        # Initialize vector store
        # TODO: Initialize Vertex RAG or knowledge service
        
        logger.info("Cricket Agent initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize cricket agent: {e}")
        # Don't exit in development, just log the error
        
    yield
    
    # Shutdown
    logger.info("Shutting down Cricket Agent")

# Create FastAPI application
app = FastAPI(
    title="Caroline Springs CC Cricket Agent",
    description="Real-time cricket agent for Caroline Springs Cricket Club",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with request ID"""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"Request {request_id}: {request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s"
    )
    
    return response

# Health check endpoints
@app.get("/healthz")
async def health_check():
    """Basic health check endpoint with readiness information"""
    settings = get_settings()
    
    return {
        "ok": True,
        "env": settings.app_env,
        "rag": settings.vector_backend,
        "mode": settings.playhq_mode,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "cricket-agent",
        "version": "1.0.0"
    }

@app.get("/healthz/detailed")
async def detailed_health_check():
    """Detailed health check with service dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "cricket-agent",
        "version": "1.0.0",
        "checks": {}
    }
    
    # PlayHQ API check
    try:
        # TODO: Check PlayHQ API connectivity
        health_status["checks"]["playhq_api"] = {
            "status": "healthy",
            "message": "PlayHQ API connection successful"
        }
    except Exception as e:
        health_status["checks"]["playhq_api"] = {
            "status": "unhealthy",
            "message": f"PlayHQ API connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Vector store check
    try:
        # TODO: Check vector store connectivity
        health_status["checks"]["vector_store"] = {
            "status": "healthy",
            "message": "Vector store connection successful"
        }
    except Exception as e:
        health_status["checks"]["vector_store"] = {
            "status": "unhealthy",
            "message": f"Vector store connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    return health_status

@app.get("/metrics")
async def get_metrics():
    """Prometheus-style metrics endpoint"""
    try:
        metrics_data = get_prometheus_metrics()
        return Response(
            content=metrics_data,
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

# Webhook endpoints (private mode only)
@app.post("/webhooks/playhq", response_model=WebhookResponse)
async def playhq_webhook(request: Request):
    """
    PlayHQ webhook endpoint for real-time updates
    Only available in private mode
    """
    settings = get_settings()
    
    if settings.playhq_mode != "private":
        raise HTTPException(status_code=403, detail="Webhook mode not enabled")
    
    return await process_webhook(request)

# Main cricket agent endpoints
@app.post("/v1/ask", response_model=AskResponse)
async def ask_cricket_agent(request: AskRequest):
    """
    Main endpoint for cricket agent queries
    Handles questions about fixtures, players, ladder, etc.
    """
    request_id = getattr(request, 'request_id', str(uuid.uuid4()))
    start_time = time.time()
    
    logger.info(f"Processing cricket query: {request.text[:100]}...", extra={
        "request_id": request_id,
        "source": request.source,
        "team_hint": request.team_hint
    })
    
    try:
        # Import router
        from agent.router import get_router
        
        # Route the query
        router = get_router()
        result = await router.route_query(
            text=request.text,
            source=request.source or "web",
            team_hint=request.team_hint
        )
        
        # Extract response
        answer = result.get("answer", "I don't have that information.")
        meta = result.get("meta", {})
        
        # Add request_id to meta
        meta["request_id"] = request_id
        
        response = AskResponse(
            answer=answer,
            meta=meta
        )
        
        logger.info(f"Query processed successfully", extra={
            "request_id": request_id,
            "latency_ms": meta.get("latency_ms", 0),
            "intent": meta.get("intent", "unknown")
        })
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to process cricket query: {e}", extra={
            "request_id": request_id
        })
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")

@app.post("/internal/refresh", response_model=RefreshResponse)
async def refresh_data(
    request: RefreshRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Internal endpoint to refresh cricket data
    Requires bearer token authentication
    """
    # Validate bearer token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    
    # Get settings to validate token
    settings = get_settings()
    if not settings.internal_token:
        raise HTTPException(status_code=500, detail="Internal token not configured")
    
    # Extract token from header
    token = authorization.replace("Bearer ", "")
    if token != settings.internal_token:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    
    logger.info(f"Data refresh requested: scope={request.scope}, id={request.id}")
    
    try:
        # Import sync functions
        from jobs.sync import run_full_refresh, run_team_refresh, run_match_refresh, run_ladder_refresh
        
        # Route to appropriate sync function
        if request.scope == "all":
            result = await run_full_refresh()
        elif request.scope == "team":
            if not request.id:
                raise HTTPException(status_code=400, detail="Team ID required for team scope")
            result = await run_team_refresh(request.id)
        elif request.scope == "match":
            if not request.id:
                raise HTTPException(status_code=400, detail="Match ID required for match scope")
            result = await run_match_refresh(request.id)
        elif request.scope == "ladder":
            if not request.id:
                raise HTTPException(status_code=400, detail="Grade ID required for ladder scope")
            result = await run_ladder_refresh(request.id)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid scope: {request.scope}")
        
        # Extract stats from result
        stats = result.get("stats", {})
        updated_count = sum([
            stats.get("fixtures_updated", 0),
            stats.get("ladders_updated", 0),
            stats.get("teams_updated", 0),
            stats.get("scorecards_updated", 0),
            stats.get("rosters_updated", 0),
            stats.get("vector_upserts", 0)
        ])
        
        response = RefreshResponse(
            status=result.get("status", "success"),
            message=f"Data refreshed for scope: {request.scope}",
            updated_count=updated_count
        )
        
        logger.info(f"Data refresh completed: {request.scope}", extra={
            "scope": request.scope,
            "id": request.id,
            "updated_count": updated_count,
            "stats": stats
        })
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data refresh failed: {e}")
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")

@app.post("/sync")
async def sync_data(request: Dict[str, Any] = None):
    """
    Public endpoint to trigger data synchronization
    Can be called without authentication for automated pipelines
    """
    logger.info("Data sync requested via /sync endpoint")
    
    try:
        # Import sync functions
        from jobs.sync import CricketDataSync
        
        # Initialize sync
        sync = CricketDataSync()
        
        # Run full sync
        result = await sync.sync_all()
        
        logger.info(f"Data sync completed", extra={
            "status": result.get("status", "success"),
            "stats": result.get("stats", {})
        })
        
        return {
            "status": result.get("status", "success"),
            "message": "Data synchronization completed",
            "stats": result.get("stats", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Data sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@app.post("/admin/populate-synthetic")
async def populate_synthetic_data():
    """
    Admin endpoint to populate synthetic cricket data
    Used by automated pipelines for data population
    """
    logger.info("Synthetic data population requested")
    
    try:
        # Import synthetic data generator
        from scripts.synthetic_data_generator import SyntheticCricketDataGenerator
        
        # Generate and store synthetic data
        generator = SyntheticCricketDataGenerator()
        result = await generator.generate_and_store_synthetic_data()
        
        logger.info(f"Synthetic data population completed", extra={
            "status": result.get("status", "success"),
            "stats": result.get("stats", {})
        })
        
        return {
            "status": result.get("status", "success"),
            "message": "Synthetic data population completed",
            "stats": result.get("stats", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Synthetic data population failed: {e}")
        raise HTTPException(status_code=500, detail=f"Synthetic data population failed: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Caroline Springs CC Cricket Agent",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/healthz"
    }

@app.get("/debug/vector-store")
async def debug_vector_store():
    """Debug endpoint to check vector store contents"""
    try:
        from agent.tools.vector_client import get_vector_client
        
        vector_client = get_vector_client()
        
        # Get stored documents count
        stored_docs = getattr(vector_client, '_stored_documents', {})
        
        # Try to reload from local storage
        try:
            vector_client._load_from_local_storage()
            stored_docs = getattr(vector_client, '_stored_documents', {})
        except Exception as e:
            logger.warning(f"Failed to reload from local storage: {e}")
        
        # Try to reload from GCS
        try:
            vector_client._load_from_gcs()
            stored_docs = getattr(vector_client, '_stored_documents', {})
        except Exception as e:
            logger.warning(f"Failed to reload from GCS: {e}")
        
        return {
            "status": "success",
            "vector_store_type": type(vector_client).__name__,
            "project_id": vector_client.project_id,
            "stored_documents_count": len(stored_docs),
            "document_ids": list(stored_docs.keys())[:10],  # First 10 IDs
            "sample_document": stored_docs.get(list(stored_docs.keys())[0], {}) if stored_docs else None,
            "gcs_bucket": f"{vector_client.project_id}-cricket-vectors",
            "vector_client_instance_id": id(vector_client),
            "current_instance_id": id(vector_client)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/debug/reload-vector-store")
async def reload_vector_store():
    """Force reload vector store from GCS"""
    try:
        from agent.tools.vector_client import get_vector_client
        
        vector_client = get_vector_client()
        vector_client._load_from_gcs()
        
        stored_docs = getattr(vector_client, '_stored_documents', {})
        
        return {
            "status": "success",
            "message": f"Reloaded {len(stored_docs)} documents from GCS",
            "stored_documents_count": len(stored_docs)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/debug/test-vector-store")
async def test_vector_store():
    """Test vector store by directly upserting a document"""
    try:
        from agent.tools.vector_client import get_vector_client
        
        vector_client = get_vector_client()
        
        # Test document
        test_doc = {
            "id": "test-doc-1",
            "text": "This is a test document for Harshvarshan",
            "metadata": {
                "type": "test",
                "player": "Harshvarshan"
            }
        }
        
        # Upsert the test document
        vector_client.upsert([test_doc])
        
        # Check if it was stored
        stored_docs = getattr(vector_client, '_stored_documents', {})
        
        return {
            "status": "success",
            "message": f"Test document upserted",
            "stored_documents_count": len(stored_docs),
            "test_doc_stored": "test-doc-1" in stored_docs
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/admin/initialize-matching-engine")
async def initialize_matching_engine():
    """Initialize Vertex AI Matching Engine"""
    try:
        from agent.tools.vector_client import get_vector_client
        
        vector_client = get_vector_client()
        
        # Initialize Matching Engine
        success = vector_client.initialize_matching_engine()
        
        if success:
            return {
                "status": "success",
                "message": "Matching Engine initialized successfully",
                "matching_engine_status": vector_client.get_matching_engine_status()
            }
        else:
            return {
                "status": "error",
                "message": "Failed to initialize Matching Engine"
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/debug/matching-engine-status")
async def get_matching_engine_status():
    """Get Matching Engine status"""
    try:
        from agent.tools.vector_client import get_vector_client
        
        vector_client = get_vector_client()
        status = vector_client.get_matching_engine_status()
        
        return {
            "status": "success",
            "matching_engine_status": status
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/debug/clear-corrupted-storage")
async def clear_corrupted_storage():
    """Clear corrupted storage and reinitialize"""
    try:
        from agent.tools.vector_client import get_vector_client
        
        vector_client = get_vector_client()
        vector_client.clear_corrupted_storage()
        
        return {
            "status": "success",
            "message": "Corrupted storage cleared and reinitialized"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/debug/redis-storage-status")
async def get_redis_storage_status():
    """Get Redis storage status"""
    try:
        from agent.tools.vector_client import get_vector_client
        
        vector_client = get_vector_client()
        
        if hasattr(vector_client, 'redis_storage') and vector_client.redis_storage:
            status = vector_client.redis_storage.health_check()
            metadata = vector_client.redis_storage.get_metadata()
            
            return {
                "status": "success",
                "redis_storage": status,
                "metadata": metadata
            }
        else:
            return {
                "status": "success",
                "redis_storage": {"status": "not_available"},
                "metadata": {"storage_type": "fallback"}
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/debug/clear-redis-storage")
async def clear_redis_storage():
    """Clear Redis storage"""
    try:
        from agent.tools.vector_client import get_vector_client
        
        vector_client = get_vector_client()
        
        if hasattr(vector_client, 'redis_storage') and vector_client.redis_storage:
            success = vector_client.redis_storage.clear_all()
            
            if success:
                return {
                    "status": "success",
                    "message": "Redis storage cleared successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to clear Redis storage"
                }
        else:
            return {
                "status": "error",
                "message": "Redis storage not available"
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/debug/firestore-storage-status")
async def get_firestore_storage_status():
    """Get Firestore storage status"""
    try:
        from agent.tools.vector_client import get_vector_client
        
        vector_client = get_vector_client()
        
        if hasattr(vector_client, 'firestore_storage') and vector_client.firestore_storage:
            status = vector_client.firestore_storage.health_check()
            metadata = vector_client.firestore_storage.get_metadata()
            
            return {
                "status": "success",
                "firestore_storage": status,
                "metadata": metadata
            }
        else:
            return {
                "status": "success",
                "firestore_storage": {"status": "not_available"},
                "metadata": {"storage_type": "fallback"}
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/debug/clear-firestore-storage")
async def clear_firestore_storage():
    """Clear Firestore storage"""
    try:
        from agent.tools.vector_client import get_vector_client
        
        vector_client = get_vector_client()
        
        if hasattr(vector_client, 'firestore_storage') and vector_client.firestore_storage:
            success = vector_client.firestore_storage.clear_all()
            
            if success:
                return {
                    "status": "success",
                    "message": "Firestore storage cleared successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to clear Firestore storage"
                }
        else:
            return {
                "status": "error",
                "message": "Firestore storage not available"
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/debug/cloud-storage-persistence-status")
async def get_cloud_storage_persistence_status():
    """Get Cloud Storage persistence status"""
    try:
        from agent.tools.vector_client import get_vector_client
        
        vector_client = get_vector_client()
        
        if hasattr(vector_client, 'cloud_storage_persistence') and vector_client.cloud_storage_persistence:
            status = vector_client.cloud_storage_persistence.health_check()
            metadata = vector_client.cloud_storage_persistence.get_metadata()
            
            return {
                "status": "success",
                "cloud_storage_persistence": status,
                "metadata": metadata
            }
        else:
            return {
                "status": "success",
                "cloud_storage_persistence": {"status": "not_available"},
                "metadata": {"storage_type": "fallback"}
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/debug/clear-cloud-storage-persistence")
async def clear_cloud_storage_persistence():
    """Clear Cloud Storage persistence"""
    try:
        from agent.tools.vector_client import get_vector_client
        
        vector_client = get_vector_client()
        
        if hasattr(vector_client, 'cloud_storage_persistence') and vector_client.cloud_storage_persistence:
            success = vector_client.cloud_storage_persistence.clear_all()
            
            if success:
                return {
                    "status": "success",
                    "message": "Cloud Storage persistence cleared successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to clear Cloud Storage persistence"
                }
        else:
            return {
                "status": "error",
                "message": "Cloud Storage persistence not available"
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
