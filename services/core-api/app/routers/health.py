"""
Health Check Router
Provides health check endpoints for monitoring and load balancing
"""

import time
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..utils.database import get_db
from ..config.settings import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "anzx-core-api",
        "version": "1.0.0"
    }


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Detailed health check with dependency status"""
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "anzx-core-api",
        "version": "1.0.0",
        "environment": settings.environment,
        "checks": {}
    }
    
    # Database check
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Redis check (if configured)
    try:
        import redis
        r = redis.from_url(settings.redis_url)
        r.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }
    
    # Vertex AI check
    try:
        from ..services.vertex_ai_service import vertex_ai_service
        if vertex_ai_service.is_initialized:
            health_status["checks"]["vertex_ai"] = {
                "status": "healthy",
                "message": "Vertex AI service initialized"
            }
        else:
            health_status["checks"]["vertex_ai"] = {
                "status": "warning",
                "message": "Vertex AI service not initialized"
            }
    except Exception as e:
        health_status["checks"]["vertex_ai"] = {
            "status": "unhealthy",
            "message": f"Vertex AI service error: {str(e)}"
        }
    
    # Response time
    response_time = round((time.time() - start_time) * 1000, 2)
    health_status["response_time_ms"] = response_time
    
    # Return appropriate status code
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check for Kubernetes"""
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        
        # Check if services are initialized
        from ..services.assistant_factory import assistant_factory
        if not assistant_factory.get_available_types():
            raise Exception("Assistant factory not initialized")
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }