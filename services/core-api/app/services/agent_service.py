"""
Agent management service - orchestrates between database models and Vertex AI
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.user import Assistant, Organization, Conversation, Message
from ..services.vertex_ai_service import vertex_ai_service
from ..services.hybrid_agent_orchestrator import hybrid_agent_orchestrator
from ..middleware.usage_tracking import usage_tracker
from ..config.vertex_ai import vertex_ai_config

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing AI agents and their interactions"""
    
    def __init__(self):
        self.vertex_ai = vertex_ai_service
        self.orchestrator = hybrid_agent_orchestrator
        self.config = vertex_ai_config
    
    async def create_agent(
        self,
        db: Session,
        organization_id: str,
        agent_data: Dict[str, Any]
    ) -> Assistant:
        """
        Create a new AI agent
        
        Args:
            db: Database session
            organization_id: Organization ID
            agent_data: Agent configuration data
            
        Returns:
            Created Assistant model
        """
        try:
            # Validate organization exists
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization not found"
                )
            
            # Check subscription limits
            existing_agents = db.query(Assistant).filter(
                Assistant.organization_id == organization_id,
                Assistant.is_active == True
            ).count()
            
            plan_limits = usage_service.billing_config.get_plan_limits(org.subscription_plan)
            max_assistants = plan_limits.get("assistants", 1)
            
            if max_assistants > 0 and existing_agents >= max_assistants:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Assistant limit reached for {org.subscription_plan} plan"
                )
            
            # Create Vertex AI agent
            vertex_agent = await self.vertex_ai.create_agent(
                organization_id=organization_id,
                agent_type=agent_data["type"],
                name=agent_data["name"],
                description=agent_data.get("description"),
                knowledge_base_ids=agent_data.get("knowledge_sources", [])
            )
            
            # Create database record
            assistant = Assistant(
                name=agent_data["name"],
                description=agent_data.get("description"),
                type=agent_data["type"],
                organization_id=organization_id,
                system_prompt=self._generate_system_prompt(agent_data["type"], agent_data.get("custom_prompt")),
                model_config={
                    "vertex_ai_agent_id": vertex_agent["agent_id"],
                    "engine_id": vertex_agent["engine_id"],
                    "data_store_id": vertex_agent.get("data_store_id"),
                    "model": self.config.DEFAULT_MODEL,
                    "temperature": agent_data.get("temperature", 0.7),
                    "max_tokens": agent_data.get("max_tokens", 1024),
                    "top_p": agent_data.get("top_p", 0.9),
                    "top_k": agent_data.get("top_k", 40)
                },
                tools_config={
                    "enabled_tools": agent_data.get("enabled_tools", []),
                    "webhook_url": f"/api/v1/agents/{agent_data['type']}/webhook",
                    "escalation_enabled": agent_data.get("escalation_enabled", True),
                    "escalation_threshold": agent_data.get("escalation_threshold", 0.7)
                },
                knowledge_sources=agent_data.get("knowledge_sources", []),
                is_active=True,
                deployment_status="deployed"
            )
            
            db.add(assistant)
            db.commit()
            db.refresh(assistant)
            
            logger.info(f"Created agent: {assistant.id} for organization: {organization_id}")
            return assistant
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create agent: {str(e)}"
            )
    
    async def get_agent(
        self,
        db: Session,
        agent_id: str,
        organization_id: str
    ) -> Assistant:
        """Get agent by ID"""
        assistant = db.query(Assistant).filter(
            Assistant.id == agent_id,
            Assistant.organization_id == organization_id
        ).first()
        
        if not assistant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        return assistant
    
    async def list_agents(
        self,
        db: Session,
        organization_id: str,
        agent_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[Assistant]:
        """List agents for an organization"""
        query = db.query(Assistant).filter(Assistant.organization_id == organization_id)
        
        if agent_type:
            query = query.filter(Assistant.type == agent_type)
        
        if active_only:
            query = query.filter(Assistant.is_active == True)
        
        return query.all()
    
    async def update_agent(
        self,
        db: Session,
        agent_id: str,
        organization_id: str,
        update_data: Dict[str, Any]
    ) -> Assistant:
        """Update agent configuration"""
        try:
            assistant = await self.get_agent(db, agent_id, organization_id)
            
            # Update Vertex AI agent if needed
            if any(key in update_data for key in ["name", "description", "system_prompt"]):
                vertex_config = {
                    "display_name": update_data.get("name", assistant.name),
                    "description": update_data.get("description", assistant.description),
                    "system_prompt": update_data.get("system_prompt", assistant.system_prompt)
                }
                
                await self.vertex_ai.update_agent_configuration(
                    assistant.model_config["vertex_ai_agent_id"],
                    vertex_config
                )
            
            # Update database record
            for key, value in update_data.items():
                if hasattr(assistant, key):
                    setattr(assistant, key, value)
            
            assistant.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(assistant)
            
            logger.info(f"Updated agent: {agent_id}")
            return assistant
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update agent: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update agent: {str(e)}"
            )
    
    async def delete_agent(
        self,
        db: Session,
        agent_id: str,
        organization_id: str
    ) -> bool:
        """Delete an agent"""
        try:
            assistant = await self.get_agent(db, agent_id, organization_id)
            
            # Delete from Vertex AI
            vertex_agent_id = assistant.model_config.get("vertex_ai_agent_id")
            if vertex_agent_id:
                await self.vertex_ai.delete_agent(vertex_agent_id)
            
            # Soft delete in database
            assistant.is_active = False
            assistant.deployment_status = "archived"
            assistant.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Deleted agent: {agent_id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete agent: {e}")
            db.rollback()
            return False
    
    async def start_conversation(
        self,
        db: Session,
        assistant_id: str,
        organization_id: str,
        user_message: str,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        channel: str = "api"
    ) -> Dict[str, Any]:
        """
        Start or continue a conversation with an agent
        
        Args:
            db: Database session
            assistant_id: Assistant ID
            organization_id: Organization ID
            user_message: User's message
            user_id: User ID (optional for anonymous)
            conversation_id: Existing conversation ID (optional)
            channel: Communication channel
            
        Returns:
            Conversation response with agent reply
        """
        try:
            # Get assistant
            assistant = await self.get_agent(db, assistant_id, organization_id)
            
            # Check usage limits
            limit_check = await usage_tracker.check_usage_limits(
                db, organization_id, required_tokens=len(user_message.split()) * 2
            )
            
            if not limit_check["can_proceed"]:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Usage limit exceeded. Please upgrade your plan."
                )
            
            # Get or create conversation
            conversation = None
            if conversation_id:
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id,
                    Conversation.organization_id == organization_id
                ).first()
            
            if not conversation:
                conversation = Conversation(
                    organization_id=organization_id,
                    user_id=user_id,
                    assistant_id=assistant_id,
                    channel=channel,
                    status="active"
                )
                db.add(conversation)
                db.flush()
            
            # Create user message record
            user_msg = Message(
                conversation_id=conversation.id,
                content=user_message,
                role="user",
                metadata={"channel": channel}
            )
            db.add(user_msg)
            
            # Get conversation context
            context = await self._build_conversation_context(db, conversation.id)
            
            # Call Vertex AI agent
            vertex_agent_id = assistant.model_config["vertex_ai_agent_id"]
            vertex_response = await self.vertex_ai.start_conversation(
                agent_id=vertex_agent_id,
                user_message=user_message,
                conversation_id=str(conversation.id),
                context=context
            )
            
            # Calculate usage metrics
            tokens_input = len(user_message.split())
            tokens_output = len(vertex_response["reply"].split())
            cost = usage_tracker.calculate_token_cost(
                tokens_input, tokens_output, self.config.DEFAULT_MODEL
            )
            
            # Create assistant message record
            assistant_msg = Message(
                conversation_id=conversation.id,
                content=vertex_response["reply"],
                role="assistant",
                model=self.config.DEFAULT_MODEL,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                cost=cost,
                citations=vertex_response.get("citations", []),
                metadata={
                    "vertex_conversation_id": vertex_response["conversation_id"],
                    "search_results": vertex_response.get("search_results", []),
                    "confidence_score": vertex_response.get("confidence_score", 0.8)
                }
            )
            db.add(assistant_msg)
            
            # Update conversation metrics
            conversation.message_count += 2  # User + assistant messages
            conversation.total_tokens += tokens_input + tokens_output
            conversation.total_cost += cost
            conversation.updated_at = datetime.utcnow()
            
            # Update assistant metrics
            assistant.total_messages += 1
            assistant.total_conversations = db.query(Conversation).filter(
                Conversation.assistant_id == assistant_id
            ).count()
            
            db.commit()
            
            # Track usage
            await usage_tracker.track_ai_interaction(
                db=db,
                organization_id=organization_id,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                cost=cost,
                model=self.config.DEFAULT_MODEL
            )
            
            # Prepare response
            response = {
                "conversation_id": str(conversation.id),
                "message_id": str(assistant_msg.id),
                "reply": vertex_response["reply"],
                "citations": vertex_response.get("citations", []),
                "search_results": vertex_response.get("search_results", []),
                "usage": {
                    "tokens_input": tokens_input,
                    "tokens_output": tokens_output,
                    "cost": cost
                },
                "conversation_state": vertex_response.get("conversation_state", "IN_PROGRESS"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Conversation processed for assistant: {assistant_id}")
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to process conversation: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process conversation: {str(e)}"
            )
    
    async def get_conversation_history(
        self,
        db: Session,
        conversation_id: str,
        organization_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get conversation message history"""
        try:
            # Verify conversation belongs to organization
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.organization_id == organization_id
            ).first()
            
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            
            # Get messages
            messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.desc()).limit(limit).all()
            
            # Format response
            history = []
            for msg in reversed(messages):  # Reverse to get chronological order
                history.append({
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat(),
                    "tokens_input": msg.tokens_input,
                    "tokens_output": msg.tokens_output,
                    "cost": float(msg.cost) if msg.cost else 0.0,
                    "citations": msg.citations or [],
                    "metadata": msg.metadata or {}
                })
            
            return history
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get conversation history: {str(e)}"
            )
    
    async def get_agent_analytics(
        self,
        db: Session,
        agent_id: str,
        organization_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get agent performance analytics"""
        try:
            assistant = await self.get_agent(db, agent_id, organization_id)
            
            # Get Vertex AI metrics
            vertex_metrics = await self.vertex_ai.get_agent_metrics(
                assistant.model_config["vertex_ai_agent_id"]
            )
            
            # Get database metrics
            from sqlalchemy import func
            from datetime import timedelta
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Conversation metrics
            conversation_stats = db.query(
                func.count(Conversation.id).label("total_conversations"),
                func.sum(Conversation.message_count).label("total_messages"),
                func.sum(Conversation.total_tokens).label("total_tokens"),
                func.sum(Conversation.total_cost).label("total_cost"),
                func.avg(Conversation.satisfaction_rating).label("avg_satisfaction")
            ).filter(
                Conversation.assistant_id == agent_id,
                Conversation.created_at >= start_date
            ).first()
            
            # Response time metrics
            response_times = db.query(
                func.avg(Message.latency_ms).label("avg_response_time")
            ).filter(
                Message.conversation_id.in_(
                    db.query(Conversation.id).filter(
                        Conversation.assistant_id == agent_id,
                        Conversation.created_at >= start_date
                    )
                ),
                Message.role == "assistant"
            ).first()
            
            analytics = {
                "agent_id": agent_id,
                "period_days": days,
                "conversations": {
                    "total": conversation_stats.total_conversations or 0,
                    "messages": conversation_stats.total_messages or 0,
                    "avg_satisfaction": float(conversation_stats.avg_satisfaction or 0)
                },
                "performance": {
                    "avg_response_time_ms": float(response_times.avg_response_time or 0),
                    "total_tokens": conversation_stats.total_tokens or 0,
                    "total_cost": float(conversation_stats.total_cost or 0)
                },
                "vertex_ai_metrics": vertex_metrics,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get agent analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get agent analytics: {str(e)}"
            )
    
    def _generate_system_prompt(self, agent_type: str, custom_prompt: Optional[str] = None) -> str:
        """Generate system prompt for agent type"""
        if custom_prompt:
            return custom_prompt
        
        prompts = {
            "support": """You are a helpful customer support assistant for ANZx.ai. 
            Your role is to assist customers with their questions, troubleshoot issues, 
            and provide accurate information about our AI platform services. 
            Always be polite, professional, and helpful. If you cannot answer a question, 
            offer to escalate to a human agent.""",
            
            "admin": """You are an administrative assistant that helps with scheduling, 
            email management, and office tasks. You can schedule meetings, send emails, 
            manage calendars, and help with various administrative duties. 
            Always confirm important actions before executing them."""
        }
        
        return prompts.get(agent_type, prompts["support"])
    
    async def _build_conversation_context(self, db: Session, conversation_id: str) -> Dict[str, Any]:
        """Build conversation context for Vertex AI"""
        try:
            # Get recent messages for context
            recent_messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.desc()).limit(10).all()
            
            context = {
                "conversation_id": str(conversation_id),
                "message_count": len(recent_messages),
                "recent_messages": [
                    {
                        "role": msg.role,
                        "content": msg.content[:200],  # Truncate for context
                        "timestamp": msg.created_at.isoformat()
                    }
                    for msg in reversed(recent_messages)
                ]
            }
            
            return context
            
        except Exception as e:
            logger.warning(f"Failed to build conversation context: {e}")
            return {}


# Global service instance
agent_service = AgentService()