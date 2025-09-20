"""
ANZX AI Platform - Core API
Main FastAPI application entry point
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import database components
from .utils.database import get_db, create_tables, engine
from .models.user import Organization, Assistant
from .services.assistant_factory import assistant_factory

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting ANZX AI Platform Core API")
    
    try:
        # Create database tables
        await create_tables()
        logger.info("Database tables created successfully")
        
        # Initialize services
        logger.info("Services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        # Don't exit in development, just log the error
        
    yield
    
    # Shutdown
    logger.info("Shutting down ANZX AI Platform Core API")


# Create FastAPI application
app = FastAPI(
    title="ANZX AI Platform API",
    description="AI-powered virtual agents platform for Australian businesses",
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

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": request.url.path
        }
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s"
    )
    
    return response

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "anzx-core-api",
        "version": "1.0.0"
    }

@app.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "anzx-core-api",
        "version": "1.0.0",
        "environment": "development",
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
    
    # Assistant factory check
    try:
        types = assistant_factory.get_available_types()
        health_status["checks"]["assistant_factory"] = {
            "status": "healthy",
            "message": f"Assistant factory loaded with {len(types)} types: {', '.join(types)}"
        }
    except Exception as e:
        health_status["checks"]["assistant_factory"] = {
            "status": "unhealthy",
            "message": f"Assistant factory error: {str(e)}"
        }
    
    return health_status

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ANZX AI Platform API",
        "version": "1.0.0",
        "status": "operational",
        "environment": "development",
        "docs": "/docs",
        "health": "/health"
    }

# Assistant endpoints
@app.get("/assistants")
async def list_assistants(db: Session = Depends(get_db)):
    """List available assistants"""
    try:
        # Get assistants from database
        assistants = db.query(Assistant).filter(Assistant.is_active == True).all()
        
        # If no assistants in DB, return the factory types
        if not assistants:
            factory_types = assistant_factory.get_available_types()
            return {
                "assistants": [
                    {
                        "id": f"{assistant_type}-assistant",
                        "name": f"{assistant_type.title()} Assistant",
                        "type": assistant_type,
                        "status": "available",
                        "description": f"{assistant_type.title()} specialist assistant",
                        "source": "factory"
                    }
                    for assistant_type in factory_types
                ]
            }
        
        # Return database assistants
        return {
            "assistants": [
                {
                    "id": str(assistant.id),
                    "name": assistant.name,
                    "type": assistant.type,
                    "status": assistant.deployment_status,
                    "description": assistant.description,
                    "source": "database"
                }
                for assistant in assistants
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list assistants: {e}")
        return {"assistants": [], "error": str(e)}

@app.post("/assistants/{assistant_id}/chat")
async def chat_with_assistant(assistant_id: str, message: dict, db: Session = Depends(get_db)):
    """Chat with an assistant"""
    try:
        user_message = message.get("message", "")
        
        # Try to find assistant in database (only if assistant_id is a valid UUID)
        assistant = None
        try:
            # Check if assistant_id is a valid UUID
            import uuid
            uuid.UUID(assistant_id)
            assistant = db.query(Assistant).filter(Assistant.id == assistant_id).first()
        except ValueError:
            # Not a valid UUID, skip database lookup
            pass
        
        if not assistant:
            # Check if it's a factory assistant type
            assistant_type = assistant_id.replace("-assistant", "")
            if assistant_type in assistant_factory.get_available_types():
                # Create a temporary assistant instance
                config = {
                    "organization_id": "dev-org",
                    "organization_name": "Development Organization"
                }
                
                temp_assistant = await assistant_factory.create_assistant(
                    db=db,
                    assistant_type=assistant_type,
                    assistant_id=assistant_id,
                    config=config
                )
                
                # Process the message
                response = await temp_assistant.process_message(
                    db=db,
                    message=user_message,
                    conversation_context={"conversation_id": "temp-conv"},
                    user_context={"user_id": "temp-user"}
                )
                
                return {
                    "assistant_id": assistant_id,
                    "response": response.get("response", "I'm processing your request..."),
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {
                        "assistant_type": assistant_type,
                        "message_length": len(user_message),
                        "source": "factory",
                        **response.get("metadata", {})
                    }
                }
        
        # Mock responses for database assistants
        response_text = f"Hello! I'm {assistant.name}. I understand you said: '{user_message}'. I'm here to help!"
        
        return {
            "assistant_id": assistant_id,
            "response": response_text,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "assistant_type": assistant.type,
                "message_length": len(user_message),
                "response_length": len(response_text),
                "source": "database"
            }
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {
            "assistant_id": assistant_id,
            "response": f"I'm sorry, I encountered an error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

# Organizations endpoint
@app.get("/organizations")
async def list_organizations(db: Session = Depends(get_db)):
    """List organizations"""
    try:
        organizations = db.query(Organization).all()
        return {
            "organizations": [
                {
                    "id": str(org.id),
                    "name": org.name,
                    "subscription_plan": org.subscription_plan,
                    "subscription_status": org.subscription_status,
                    "created_at": org.created_at.isoformat() if org.created_at else None
                }
                for org in organizations
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list organizations: {e}")
        return {"organizations": [], "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )