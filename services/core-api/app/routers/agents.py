"""
AI Agents API endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.user import Assistant, Organization
from ..auth.dependencies import get_current_user, require_admin, require_organization_access
from ..services.agent_service import agent_service
from ..services.vertex_ai_service import vertex_ai_service
from ..compliance.audit import compliance_auditor, AuditEventType

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


# Request/Response models
class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    type: str = Field(..., regex="^(support|admin|content|insights)$")
    system_prompt: Optional[str] = Field(None, max_length=5000)
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(1024, ge=1, le=4096)
    top_p: Optional[float] = Field(0.9, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(40, ge=1, le=100)
    enabled_tools: Optional[List[str]] = Field(default_factory=list)
    knowledge_sources: Optional[List[str]] = Field(default_factory=list)
    escalation_enabled: Optional[bool] = True
    escalation_threshold: Optional[float] = Field(0.7, ge=0.0, le=1.0)


class AgentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    system_prompt: Optional[str] = Field(None, max_length=5000)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=4096)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(None, ge=1, le=100)
    enabled_tools: Optional[List[str]] = None
    knowledge_sources: Optional[List[str]] = None
    escalation_enabled: Optional[bool] = None
    escalation_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_active: Optional[bool] = None


class ConversationRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = None
    channel: str = Field("api", regex="^(api|widget|email|slack)$")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    type: str
    organization_id: str
    is_active: bool
    deployment_status: str
    version: str
    total_conversations: int
    total_messages: int
    average_response_time: float
    satisfaction_score: float
    created_at: datetime
    updated_at: datetime
    deployed_at: Optional[datetime]


class ConversationResponse(BaseModel):
    conversation_id: str
    message_id: str
    reply: str
    citations: List[Dict[str, Any]]
    search_results: List[Dict[str, Any]]
    usage: Dict[str, Any]
    conversation_state: str
    timestamp: datetime


class AgentAnalyticsResponse(BaseModel):
    agent_id: str
    period_days: int
    conversations: Dict[str, Any]
    performance: Dict[str, Any]
    vertex_ai_metrics: Dict[str, Any]
    generated_at: datetime


@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent_data: AgentCreateRequest,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new AI agent"""
    if not current_user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    organization_id = current_user["organization_id"]
    client_ip = _get_client_ip(request)
    
    try:
        # Create agent
        assistant = await agent_service.create_agent(
            db=db,
            organization_id=organization_id,
            agent_data=agent_data.dict()
        )
        
        # Log agent creation
        compliance_auditor.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="agent_created",
            outcome="success",
            user_id=current_user["user_id"],
            ip_address=client_ip,
            details={
                "agent_id": str(assistant.id),
                "agent_type": assistant.type,
                "agent_name": assistant.name,
                "organization_id": organization_id
            }
        )
        
        return AgentResponse(
            id=str(assistant.id),
            name=assistant.name,
            description=assistant.description,
            type=assistant.type,
            organization_id=str(assistant.organization_id),
            is_active=assistant.is_active,
            deployment_status=assistant.deployment_status,
            version=assistant.version,
            total_conversations=assistant.total_conversations,
            total_messages=assistant.total_messages,
            average_response_time=assistant.average_response_time,
            satisfaction_score=assistant.satisfaction_score,
            created_at=assistant.created_at,
            updated_at=assistant.updated_at,
            deployed_at=assistant.deployed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    agent_type: Optional[str] = None,
    active_only: bool = True,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List agents for the current organization"""
    if not current_user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    organization_id = current_user["organization_id"]
    
    try:
        assistants = await agent_service.list_agents(
            db=db,
            organization_id=organization_id,
            agent_type=agent_type,
            active_only=active_only
        )
        
        return [
            AgentResponse(
                id=str(assistant.id),
                name=assistant.name,
                description=assistant.description,
                type=assistant.type,
                organization_id=str(assistant.organization_id),
                is_active=assistant.is_active,
                deployment_status=assistant.deployment_status,
                version=assistant.version,
                total_conversations=assistant.total_conversations,
                total_messages=assistant.total_messages,
                average_response_time=assistant.average_response_time,
                satisfaction_score=assistant.satisfaction_score,
                created_at=assistant.created_at,
                updated_at=assistant.updated_at,
                deployed_at=assistant.deployed_at
            )
            for assistant in assistants
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get agent details"""
    if not current_user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    organization_id = current_user["organization_id"]
    
    try:
        assistant = await agent_service.get_agent(
            db=db,
            agent_id=agent_id,
            organization_id=organization_id
        )
        
        return AgentResponse(
            id=str(assistant.id),
            name=assistant.name,
            description=assistant.description,
            type=assistant.type,
            organization_id=str(assistant.organization_id),
            is_active=assistant.is_active,
            deployment_status=assistant.deployment_status,
            version=assistant.version,
            total_conversations=assistant.total_conversations,
            total_messages=assistant.total_messages,
            average_response_time=assistant.average_response_time,
            satisfaction_score=assistant.satisfaction_score,
            created_at=assistant.created_at,
            updated_at=assistant.updated_at,
            deployed_at=assistant.deployed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent: {str(e)}"
        )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    update_data: AgentUpdateRequest,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update agent configuration"""
    if not current_user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    organization_id = current_user["organization_id"]
    client_ip = _get_client_ip(request)
    
    try:
        # Update agent
        assistant = await agent_service.update_agent(
            db=db,
            agent_id=agent_id,
            organization_id=organization_id,
            update_data=update_data.dict(exclude_unset=True)
        )
        
        # Log agent update
        compliance_auditor.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="agent_updated",
            outcome="success",
            user_id=current_user["user_id"],
            ip_address=client_ip,
            details={
                "agent_id": agent_id,
                "updated_fields": list(update_data.dict(exclude_unset=True).keys()),
                "organization_id": organization_id
            }
        )
        
        return AgentResponse(
            id=str(assistant.id),
            name=assistant.name,
            description=assistant.description,
            type=assistant.type,
            organization_id=str(assistant.organization_id),
            is_active=assistant.is_active,
            deployment_status=assistant.deployment_status,
            version=assistant.version,
            total_conversations=assistant.total_conversations,
            total_messages=assistant.total_messages,
            average_response_time=assistant.average_response_time,
            satisfaction_score=assistant.satisfaction_score,
            created_at=assistant.created_at,
            updated_at=assistant.updated_at,
            deployed_at=assistant.deployed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent: {str(e)}"
        )


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    request: Request,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete an agent"""
    if not current_user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    organization_id = current_user["organization_id"]
    client_ip = _get_client_ip(request)
    
    try:
        success = await agent_service.delete_agent(
            db=db,
            agent_id=agent_id,
            organization_id=organization_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete agent"
            )
        
        # Log agent deletion
        compliance_auditor.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="agent_deleted",
            outcome="success",
            user_id=current_user["user_id"],
            ip_address=client_ip,
            details={
                "agent_id": agent_id,
                "organization_id": organization_id
            }
        )
        
        return {"message": "Agent deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}"
        )


@router.post("/{agent_id}/chat", response_model=ConversationResponse)
async def chat_with_agent(
    agent_id: str,
    conversation_data: ConversationRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start or continue a conversation with an agent"""
    if not current_user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    organization_id = current_user["organization_id"]
    client_ip = _get_client_ip(request)
    
    try:
        # Start conversation
        response = await agent_service.start_conversation(
            db=db,
            assistant_id=agent_id,
            organization_id=organization_id,
            user_message=conversation_data.message,
            user_id=current_user["user_id"],
            conversation_id=conversation_data.conversation_id,
            channel=conversation_data.channel
        )
        
        # Log conversation
        compliance_auditor.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="agent_conversation",
            outcome="success",
            user_id=current_user["user_id"],
            ip_address=client_ip,
            details={
                "agent_id": agent_id,
                "conversation_id": response["conversation_id"],
                "channel": conversation_data.channel,
                "tokens_used": response["usage"]["tokens_input"] + response["usage"]["tokens_output"],
                "cost": response["usage"]["cost"]
            }
        )
        
        return ConversationResponse(
            conversation_id=response["conversation_id"],
            message_id=response["message_id"],
            reply=response["reply"],
            citations=response["citations"],
            search_results=response["search_results"],
            usage=response["usage"],
            conversation_state=response["conversation_state"],
            timestamp=datetime.fromisoformat(response["timestamp"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process conversation: {str(e)}"
        )


@router.get("/{agent_id}/conversations/{conversation_id}/history")
async def get_conversation_history(
    agent_id: str,
    conversation_id: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation message history"""
    if not current_user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    organization_id = current_user["organization_id"]
    
    try:
        history = await agent_service.get_conversation_history(
            db=db,
            conversation_id=conversation_id,
            organization_id=organization_id,
            limit=limit
        )
        
        return {"conversation_id": conversation_id, "messages": history}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {str(e)}"
        )


@router.get("/{agent_id}/analytics", response_model=AgentAnalyticsResponse)
async def get_agent_analytics(
    agent_id: str,
    days: int = 30,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get agent performance analytics"""
    if not current_user.get("organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    organization_id = current_user["organization_id"]
    
    try:
        analytics = await agent_service.get_agent_analytics(
            db=db,
            agent_id=agent_id,
            organization_id=organization_id,
            days=days
        )
        
        return AgentAnalyticsResponse(
            agent_id=analytics["agent_id"],
            period_days=analytics["period_days"],
            conversations=analytics["conversations"],
            performance=analytics["performance"],
            vertex_ai_metrics=analytics["vertex_ai_metrics"],
            generated_at=datetime.fromisoformat(analytics["generated_at"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent analytics: {str(e)}"
        )


@router.get("/health/vertex-ai")
async def vertex_ai_health_check(
    current_user: dict = Depends(require_admin)
):
    """Check Vertex AI service health"""
    try:
        health_status = await vertex_ai_service.test_agent_connection()
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/templates")
async def get_agent_templates():
    """Get available agent templates"""
    from ..config.vertex_ai import vertex_ai_config
    
    templates = {}
    for agent_type, template in vertex_ai_config.AGENT_TEMPLATES.items():
        templates[agent_type] = {
            "display_name": template["display_name"],
            "description": template["description"],
            "supported_languages": template.get("supported_language_codes", ["en"]),
            "default_intents": len(template.get("intents", [])),
            "webhook_enabled": template.get("webhooks", {}).get("enabled", False)
        }
    
    return {"templates": templates}


def _get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"