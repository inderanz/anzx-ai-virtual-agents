"""
ANZx.ai Platform - Core API Service
FastAPI application with authentication and core business logic
"""

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config.security import security_settings
from app.middleware.security import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    ComplianceLoggingMiddleware,
    PrivacyComplianceMiddleware
)
from app.routers import compliance, auth, organizations, billing, agents, knowledge, chat_widget, websocket, email, conversations, mcp

app = FastAPI(
    title="ANZx.ai Core API",
    description="Multi-agent AI platform core API service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security middleware (order matters)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=security_settings.RATE_LIMIT_REQUESTS_PER_MINUTE)
app.add_middleware(ComplianceLoggingMiddleware)
app.add_middleware(PrivacyComplianceMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(organizations.router)
app.include_router(billing.router)
app.include_router(agents.router)
app.include_router(knowledge.router)
app.include_router(chat_widget.router)
app.include_router(websocket.router)
app.include_router(email.router)
app.include_router(conversations.router)
app.include_router(mcp.router)
app.include_router(compliance.router)

@app.get("/")
async def root():
    return {
        "message": "ANZx.ai Core API",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    from app.models.database import check_db_health
    import os
    
    health_status = {
        "status": "healthy",
        "service": "core-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Database health check with detailed info
    db_health = check_db_health()
    health_status["checks"]["database"] = db_health
    if db_health["status"] != "healthy":
        health_status["status"] = "unhealthy"
    
    # Firebase health check
    try:
        import firebase_admin
        firebase_admin.get_app()
        health_status["checks"]["firebase"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["firebase"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"
    
    # Environment checks
    health_status["checks"]["environment"] = {
        "status": "healthy",
        "database_url_configured": bool(os.getenv("DATABASE_URL")),
        "jwt_secret_configured": bool(os.getenv("JWT_SECRET")),
        "firebase_configured": bool(os.getenv("FIREBASE_CONFIG")),
        "read_replica_configured": bool(os.getenv("READ_REPLICA_URL"))
    }
    
    return health_status

@app.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe endpoint"""
    return {"status": "ready", "service": "core-api"}

@app.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe endpoint"""
    return {"status": "alive", "service": "core-api"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)