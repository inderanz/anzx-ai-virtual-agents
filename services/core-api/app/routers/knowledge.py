"""
Knowledge Base Management API Endpoints
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..utils.database import get_db
from ..middleware.auth import get_current_user, get_organization_id
from ..services.knowledge_service import knowledge_service
from ..models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


# Pydantic models for request/response
class KnowledgeSourceCreate(BaseModel):
    name: str = Field(..., description="Name of the knowledge source")
    type: str = Field(..., description="Type of source (file, url)")
    url: Optional[str] = Field(None, description="URL for web crawling")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class KnowledgeSourceUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Updated name")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    search_type: str = Field(default="hybrid", description="Search type (semantic, keyword, hybrid)")
    max_results: int = Field(default=10, description="Maximum results to return")
    source_filter: Optional[str] = Field(None, description="Filter by knowledge source ID")


@router.post("/sources", response_model=Dict[str, Any])
async def create_knowledge_source(
    source_data: KnowledgeSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Create a new knowledge source from URL"""
    try:
        if source_data.type == "url" and not source_data.url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL is required for URL-type sources"
            )
        
        # Convert to dict for processing
        source_dict = {
            "name": source_data.name,
            "type": source_data.type,
            "url": source_data.url,
            "metadata": source_data.metadata
        }
        
        result = await knowledge_service.create_knowledge_source(
            db=db,
            organization_id=organization_id,
            source_data=source_dict
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Knowledge source creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create knowledge source"
        )


@router.post("/sources/upload", response_model=Dict[str, Any])
async def upload_knowledge_source(
    name: str = Form(..., description="Name of the knowledge source"),
    file: UploadFile = File(..., description="File to upload"),
    metadata: Optional[str] = Form(None, description="JSON metadata"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Upload a file as a knowledge source"""
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse metadata if provided
        parsed_metadata = {}
        if metadata:
            try:
                parsed_metadata = eval(metadata)  # In production, use json.loads with proper validation
            except:
                parsed_metadata = {"raw_metadata": metadata}
        
        # Prepare source data
        source_dict = {
            "name": name,
            "type": "file",
            "filename": file.filename,
            "mime_type": file.content_type,
            "content": file_content,
            "metadata": parsed_metadata
        }
        
        result = await knowledge_service.create_knowledge_source(
            db=db,
            organization_id=organization_id,
            source_data=source_dict
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )


@router.get("/sources", response_model=List[Dict[str, Any]])
async def get_knowledge_sources(
    status_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Get all knowledge sources for the organization"""
    try:
        sources = await knowledge_service.get_knowledge_sources(
            db=db,
            organization_id=organization_id,
            status_filter=status_filter,
            type_filter=type_filter
        )
        
        return sources
        
    except Exception as e:
        logger.error(f"Failed to get knowledge sources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve knowledge sources"
        )


@router.get("/sources/{source_id}", response_model=Dict[str, Any])
async def get_knowledge_source(
    source_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Get detailed information about a specific knowledge source"""
    try:
        source = await knowledge_service.get_knowledge_source(
            db=db,
            source_id=source_id,
            organization_id=organization_id
        )
        
        return source
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get knowledge source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve knowledge source"
        )


@router.put("/sources/{source_id}", response_model=Dict[str, Any])
async def update_knowledge_source(
    source_id: str,
    update_data: KnowledgeSourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Update knowledge source metadata"""
    try:
        # Convert to dict, excluding None values
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        
        result = await knowledge_service.update_knowledge_source(
            db=db,
            source_id=source_id,
            organization_id=organization_id,
            update_data=update_dict
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update knowledge source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update knowledge source"
        )


@router.delete("/sources/{source_id}", response_model=Dict[str, Any])
async def delete_knowledge_source(
    source_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Delete a knowledge source and all its documents"""
    try:
        result = await knowledge_service.delete_knowledge_source(
            db=db,
            source_id=source_id,
            organization_id=organization_id
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete knowledge source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete knowledge source"
        )


@router.post("/sources/{source_id}/reprocess", response_model=Dict[str, Any])
async def reprocess_knowledge_source(
    source_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Reprocess a knowledge source (for URL sources)"""
    try:
        result = await knowledge_service.reprocess_knowledge_source(
            db=db,
            source_id=source_id,
            organization_id=organization_id
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reprocess knowledge source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reprocess knowledge source"
        )


@router.post("/search", response_model=Dict[str, Any])
async def search_knowledge_base(
    search_request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Search the organization's knowledge base"""
    try:
        result = await knowledge_service.search_knowledge_base(
            db=db,
            organization_id=organization_id,
            query=search_request.query,
            search_type=search_request.search_type,
            max_results=search_request.max_results,
            source_filter=search_request.source_filter
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Knowledge base search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


@router.get("/analytics", response_model=Dict[str, Any])
async def get_knowledge_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization_id: str = Depends(get_organization_id)
):
    """Get comprehensive knowledge base analytics"""
    try:
        analytics = await knowledge_service.get_knowledge_analytics(
            db=db,
            organization_id=organization_id
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"Failed to get knowledge analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )


@router.get("/health", response_model=Dict[str, Any])
async def knowledge_health_check(
    db: Session = Depends(get_db)
):
    """Check knowledge service health"""
    try:
        health = await knowledge_service.health_check(db=db)
        return health
        
    except Exception as e:
        logger.error(f"Knowledge health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }