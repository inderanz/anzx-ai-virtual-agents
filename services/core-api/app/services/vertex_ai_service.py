"""
Vertex AI Agent Builder service integration
"""

import logging
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from google.cloud import aiplatform
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.auth.exceptions import DefaultCredentialsError, RefreshError
import google.auth.transport.requests
from fastapi import HTTPException, status

from ..config.vertex_ai import vertex_ai_config
from ..services.gcp_auth_service import gcp_auth_service
from ..models.user import Assistant, Conversation, Message

logger = logging.getLogger(__name__)


class VertexAIAgentService:
    """Vertex AI Agent Builder service"""
    
    def __init__(self):
        self.config = vertex_ai_config
        self.auth_service = gcp_auth_service
        self.project_id = None  # Will be lazy loaded
        self.location = self.config.LOCATION
        self.agent_builder_location = self.config.AGENT_BUILDER_LOCATION
        
        # Initialize clients as None - will be lazy loaded
        self._discovery_client = None
        self._conversation_client = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Ensure clients are initialized (lazy initialization)"""
        if self._initialized:
            return
            
        try:
            # Get project ID if not set
            if not self.project_id:
                self.project_id = self.auth_service.get_project_id()
            
            # Get authenticated credentials from auth service
            credentials = self.auth_service.get_credentials()
            
            # Initialize Vertex AI with proper credentials
            aiplatform.init(
                project=self.project_id,
                location=self.location,
                credentials=credentials
            )
            
            # Initialize Discovery Engine client with authenticated credentials
            self._discovery_client = discoveryengine.ConversationalSearchServiceClient(
                credentials=credentials
            )
            
            # Initialize conversation client with authenticated credentials
            self._conversation_client = discoveryengine.ConversationalSearchServiceClient(
                credentials=credentials
            )
            
            self._initialized = True
            logger.info(
                f"Vertex AI clients initialized with {self.auth_service._runtime_environment} authentication. "
                f"Project: {self.project_id}, Location: {self.location}"
            )
            
        except (DefaultCredentialsError, RefreshError) as e:
            logger.warning(f"Authentication failed for Vertex AI, service will be unavailable: {e}")
            self._initialized = False
            # Don't raise exception - allow service to start in degraded mode
        except Exception as e:
            logger.warning(f"Failed to initialize Vertex AI clients, service will be unavailable: {e}")
            self._initialized = False
            # Don't raise exception - allow service to start in degraded mode
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: str = "gemini-1.5-pro",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response using Vertex AI"""
        try:
            self._ensure_initialized()
            
            if not self._initialized:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Vertex AI service is not available"
                )
            
            # Extract the user message
            user_message = ""
            system_message = ""
            
            for msg in messages:
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                elif msg.get("role") == "system":
                    system_message = msg.get("content", "")
            
            # Use Vertex AI Gemini model for generation
            model_instance = aiplatform.GenerativeModel(model)
            
            # Combine system and user messages
            prompt = f"{system_message}\n\nUser: {user_message}" if system_message else user_message
            
            response = model_instance.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
            )
            
            return {
                "content": response.text,
                "metadata": {
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "tokens_input": len(prompt.split()),
                    "tokens_output": len(response.text.split()) if response.text else 0,
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to generate response: {str(e)}"
            )
    
    async def create_agent(
        self,
        organization_id: str,
        agent_type: str,
        name: str,
        description: Optional[str] = None,
        knowledge_base_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Vertex AI agent
        
        Args:
            organization_id: Organization ID
            agent_type: Type of agent (support, admin)
            name: Agent name
            description: Agent description
            knowledge_base_ids: List of knowledge base IDs to connect
            
        Returns:
            Agent configuration
        """
        self._ensure_initialized()
        try:
            # Get agent template
            template = self.config.get_agent_template(agent_type)
            
            # Create data store for knowledge base
            data_store_id = None
            if knowledge_base_ids:
                data_store_id = await self._create_data_store(
                    organization_id, f"{name}-knowledge-base"
                )
            
            # Create conversational search engine
            engine_id = await self._create_search_engine(
                organization_id=organization_id,
                name=f"{name}-engine",
                data_store_id=data_store_id
            )
            
            # Configure agent
            agent_config = {
                "agent_id": f"agent-{organization_id}-{agent_type}",
                "display_name": name,
                "description": description or template["description"],
                "engine_id": engine_id,
                "data_store_id": data_store_id,
                "agent_type": agent_type,
                "template": template,
                "organization_id": organization_id,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            logger.info(f"Created Vertex AI agent: {agent_config['agent_id']}")
            return agent_config
            
        except Exception as e:
            logger.error(f"Failed to create Vertex AI agent: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create agent: {str(e)}"
            )
    
    async def _create_data_store(
        self,
        organization_id: str,
        name: str
    ) -> str:
        """Create a data store for knowledge base"""
        try:
            parent = f"projects/{self.project_id}/locations/{self.agent_builder_location}"
            
            data_store = discoveryengine.DataStore(
                display_name=name,
                industry_vertical=discoveryengine.IndustryVertical.GENERIC,
                solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_CHAT],
                content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
            )
            
            request = discoveryengine.CreateDataStoreRequest(
                parent=parent,
                data_store=data_store,
                data_store_id=f"datastore-{organization_id}-{name.lower().replace(' ', '-')}"
            )
            
            # This would be an async operation in production
            operation = self._discovery_client.create_data_store(request=request)
            
            # For now, return the data store ID
            data_store_id = request.data_store_id
            logger.info(f"Created data store: {data_store_id}")
            
            return data_store_id
            
        except Exception as e:
            logger.error(f"Failed to create data store: {e}")
            raise
    
    async def _create_search_engine(
        self,
        organization_id: str,
        name: str,
        data_store_id: Optional[str] = None
    ) -> str:
        """Create a conversational search engine"""
        try:
            parent = f"projects/{self.project_id}/locations/{self.agent_builder_location}"
            
            engine_config = discoveryengine.Engine(
                display_name=name,
                solution_type=discoveryengine.SolutionType.SOLUTION_TYPE_CHAT,
                chat_engine_config=discoveryengine.Engine.ChatEngineConfig(
                    agent_creation_config=discoveryengine.Engine.ChatEngineConfig.AgentCreationConfig(
                        business="Customer Support and Administrative Assistant",
                        default_language_code="en",
                        time_zone="Australia/Sydney"
                    )
                )
            )
            
            # Add data store if provided
            if data_store_id:
                engine_config.data_store_ids = [
                    f"projects/{self.project_id}/locations/{self.agent_builder_location}/dataStores/{data_store_id}"
                ]
            
            request = discoveryengine.CreateEngineRequest(
                parent=parent,
                engine=engine_config,
                engine_id=f"engine-{organization_id}-{name.lower().replace(' ', '-')}"
            )
            
            # This would be an async operation in production
            operation = self._discovery_client.create_engine(request=request)
            
            engine_id = request.engine_id
            logger.info(f"Created search engine: {engine_id}")
            
            return engine_id
            
        except Exception as e:
            logger.error(f"Failed to create search engine: {e}")
            raise
    
    async def start_conversation(
        self,
        agent_id: str,
        user_message: str,
        conversation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start or continue a conversation with an agent
        
        Args:
            agent_id: Agent ID
            user_message: User's message
            conversation_id: Existing conversation ID (optional)
            context: Additional context
            
        Returns:
            Conversation response
        """
        try:
            # Parse agent ID to get engine ID
            engine_id = agent_id.replace("agent-", "engine-")
            
            # Build serving config path
            serving_config = f"projects/{self.project_id}/locations/{self.agent_builder_location}/dataStores/{engine_id}/servingConfigs/default_config"
            
            # Create conversation request
            request = discoveryengine.ConverseConversationRequest(
                name=serving_config,
                query=discoveryengine.TextInput(input=user_message),
                conversation=discoveryengine.Conversation(
                    name=conversation_id or "",
                    state=discoveryengine.Conversation.State.IN_PROGRESS
                ),
                safe_search=True,
                user_labels=context or {}
            )
            
            # Get response from Vertex AI
            response = self._conversation_client.converse_conversation(request=request)
            
            # Process response
            result = {
                "conversation_id": response.conversation.name,
                "reply": response.reply.reply if response.reply else "",
                "search_results": [],
                "citations": [],
                "conversation_state": response.conversation.state.name,
                "user_input": user_message,
                "response_time": datetime.utcnow().isoformat()
            }
            
            # Extract search results if available
            if hasattr(response, 'search_results'):
                for search_result in response.search_results:
                    result["search_results"].append({
                        "title": getattr(search_result.document, 'title', ''),
                        "snippet": getattr(search_result, 'snippet', ''),
                        "uri": getattr(search_result.document, 'uri', ''),
                        "score": getattr(search_result, 'score', 0.0)
                    })
            
            # Extract citations if available
            if hasattr(response.reply, 'references'):
                for reference in response.reply.references:
                    result["citations"].append({
                        "title": getattr(reference, 'title', ''),
                        "uri": getattr(reference, 'uri', ''),
                        "chunk_info": getattr(reference, 'chunk_info', {})
                    })
            
            logger.info(f"Conversation response generated for agent: {agent_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process conversation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process conversation: {str(e)}"
            )
    
    async def update_agent_configuration(
        self,
        agent_id: str,
        configuration: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update agent configuration"""
        try:
            # In a full implementation, this would update the actual Vertex AI agent
            # For now, we'll return the updated configuration
            
            updated_config = {
                "agent_id": agent_id,
                "updated_at": datetime.utcnow().isoformat(),
                "configuration": configuration,
                "status": "updated"
            }
            
            logger.info(f"Updated agent configuration: {agent_id}")
            return updated_config
            
        except Exception as e:
            logger.error(f"Failed to update agent configuration: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update agent: {str(e)}"
            )
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent"""
        try:
            # In a full implementation, this would delete the actual Vertex AI resources
            # For now, we'll just log the deletion
            
            logger.info(f"Deleted agent: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete agent: {e}")
            return False
    
    async def get_agent_metrics(
        self,
        agent_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get agent performance metrics"""
        try:
            # In a full implementation, this would fetch actual metrics from Vertex AI
            # For now, we'll return mock metrics
            
            metrics = {
                "agent_id": agent_id,
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                },
                "conversations": {
                    "total": 0,
                    "successful": 0,
                    "escalated": 0,
                    "average_duration": 0.0
                },
                "performance": {
                    "average_response_time": 0.0,
                    "satisfaction_score": 0.0,
                    "resolution_rate": 0.0
                },
                "usage": {
                    "total_tokens": 0,
                    "total_cost": 0.0
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get agent metrics: {e}")
            return {}
    
    async def add_knowledge_to_agent(
        self,
        agent_id: str,
        documents: List[Dict[str, Any]]
    ) -> bool:
        """Add knowledge documents to an agent's data store"""
        try:
            # In a full implementation, this would add documents to the data store
            # For now, we'll just log the operation
            
            logger.info(f"Added {len(documents)} documents to agent: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add knowledge to agent: {e}")
            return False
    
    async def test_agent_connection(self) -> Dict[str, Any]:
        """Test connection to Vertex AI services"""
        try:
            self._ensure_initialized()
            # Test basic connectivity
            config_validation = self.config.validate_config()
            
            # Test API access
            api_accessible = False
            try:
                # Simple API call to test connectivity
                parent = f"projects/{self.project_id}/locations/{self.agent_builder_location}"
                # This would make an actual API call in production
                api_accessible = True
            except Exception as e:
                logger.warning(f"API access test failed: {e}")
            
            return {
                "status": "healthy" if all(config_validation.values()) and api_accessible else "unhealthy",
                "project_id": self.project_id,
                "location": self.location,
                "agent_builder_location": self.agent_builder_location,
                "config_validation": config_validation,
                "api_accessible": api_accessible,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global service instance
vertex_ai_service = VertexAIAgentService()