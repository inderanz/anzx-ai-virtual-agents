"""
Agent Space Manager
Based on Google Cloud Platform agent-starter-pack architecture
Manages Vertex AI Agent Builder agents with built-in tools and connectors

Architecture alignment with agent-starter-pack:
- Uses Vertex AI Agent Builder as primary orchestration
- Leverages built-in connectors (Gmail, Calendar, Drive)
- Implements proper tool calling and function declarations
- Supports both Agent Builder and custom LangGraph workflows
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from google.cloud import discoveryengine_v1beta as discoveryengine
    from google.cloud import aiplatform
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    import vertexai
    from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration
except ImportError as e:
    logging.warning(f"Google Cloud libraries not installed: {e}")
    # Mock classes for development
    class discoveryengine:
        pass
    class aiplatform:
        pass
    class GenerativeModel:
        pass
    class Tool:
        pass
    class FunctionDeclaration:
        pass

from ..config.google_connectors import agent_space_connector_config
from ..config.vertex_ai import vertex_ai_config
from .tool_registry import tool_registry

logger = logging.getLogger(__name__)


class AgentSpaceManager:
    """
    Manages Vertex AI Agent Builder agents with built-in tools
    
    Based on the Google Cloud Platform agent-starter-pack approach:
    - Agents are created through Vertex AI Agent Builder
    - Built-in tools (Gmail, Calendar, Drive) are configured via Agent Builder
    - No custom connector code needed - agents use native integrations
    """
    
    def __init__(self):
        self.config = agent_space_connector_config
        self.vertex_config = vertex_ai_config
        self.project_id = self.vertex_config.PROJECT_ID
        self.location = self.vertex_config.LOCATION
        
        # Initialize Vertex AI following agent-starter-pack pattern
        vertexai.init(project=self.project_id, location=self.location)
        
        # Agent Builder clients (following agent-starter-pack architecture)
        self._agent_builder_client = None
        self._discovery_client = None
        self._conversation_client = None
        
        # Tool registry for function calling (following agent-starter-pack)
        self.tool_registry = tool_registry
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Agent Builder and Discovery Engine clients"""
        try:
            self._discovery_client = discoveryengine.ConversationalSearchServiceClient()
            logger.info("Agent Builder clients initialized")
        except Exception as e:
            logger.error(f"Failed to initialize clients: {e}")
    
    async def create_agent_with_tools(
        self,
        organization_id: str,
        agent_config: Dict[str, Any],
        enabled_tools: List[str]
    ) -> Dict[str, Any]:
        """
        Create Agent Builder agent with built-in tools
        
        Based on agent-starter-pack approach:
        - Create agent through Vertex AI Agent Builder
        - Configure built-in tools (Gmail, Calendar, Drive) 
        - Tools are enabled via Agent Builder configuration
        
        Args:
            organization_id: Organization ID
            agent_config: Agent configuration
            enabled_tools: List of tools to enable
            
        Returns:
            Created agent information
        """
        try:
            # Define available built-in tools
            available_tools = {
                "gmail": {
                    "name": "gmail",
                    "description": "Send and read emails using Gmail",
                    "function_declarations": [
                        FunctionDeclaration(
                            name="send_email",
                            description="Send an email via Gmail",
                            parameters={
                                "type": "object",
                                "properties": {
                                    "to": {"type": "string", "description": "Recipient email"},
                                    "subject": {"type": "string", "description": "Email subject"},
                                    "body": {"type": "string", "description": "Email body"}
                                },
                                "required": ["to", "subject", "body"]
                            }
                        ),
                        FunctionDeclaration(
                            name="read_emails",
                            description="Read recent emails from Gmail",
                            parameters={
                                "type": "object", 
                                "properties": {
                                    "query": {"type": "string", "description": "Search query"},
                                    "max_results": {"type": "integer", "description": "Max emails to return"}
                                }
                            }
                        )
                    ]
                },
                "calendar": {
                    "name": "calendar",
                    "description": "Manage Google Calendar events",
                    "function_declarations": [
                        FunctionDeclaration(
                            name="create_event",
                            description="Create a calendar event",
                            parameters={
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Event title"},
                                    "start_time": {"type": "string", "description": "Start time (ISO format)"},
                                    "end_time": {"type": "string", "description": "End time (ISO format)"},
                                    "attendees": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["title", "start_time", "end_time"]
                            }
                        ),
                        FunctionDeclaration(
                            name="find_free_time",
                            description="Find free time slots for scheduling",
                            parameters={
                                "type": "object",
                                "properties": {
                                    "attendees": {"type": "array", "items": {"type": "string"}},
                                    "duration_minutes": {"type": "integer"},
                                    "start_date": {"type": "string"},
                                    "end_date": {"type": "string"}
                                },
                                "required": ["attendees", "duration_minutes"]
                            }
                        )
                    ]
                },
                "drive": {
                    "name": "drive", 
                    "description": "Access and manage Google Drive files",
                    "function_declarations": [
                        FunctionDeclaration(
                            name="list_files",
                            description="List files in Google Drive",
                            parameters={
                                "type": "object",
                                "properties": {
                                    "folder_id": {"type": "string", "description": "Folder ID to search in"},
                                    "file_type": {"type": "string", "description": "File type filter"}
                                }
                            }
                        ),
                        FunctionDeclaration(
                            name="share_file",
                            description="Share a file with someone",
                            parameters={
                                "type": "object",
                                "properties": {
                                    "file_id": {"type": "string", "description": "File ID to share"},
                                    "email": {"type": "string", "description": "Email to share with"},
                                    "role": {"type": "string", "description": "Permission role"}
                                },
                                "required": ["file_id", "email"]
                            }
                        )
                    ]
                }
            }
            
            # Build tools list for the agent
            agent_tools = []
            for tool_name in enabled_tools:
                if tool_name in available_tools:
                    tool_config = available_tools[tool_name]
                    tool = Tool(
                        function_declarations=tool_config["function_declarations"]
                    )
                    agent_tools.append(tool)
            
            # Create the agent with Vertex AI Agent Builder
            # In the actual implementation, this would use the Agent Builder API
            agent_id = f"agent_{organization_id}_{agent_config['type']}"
            
            # Mock agent creation - in production this would call Agent Builder API
            created_agent = {
                "agent_id": agent_id,
                "display_name": agent_config["name"],
                "description": agent_config.get("description", ""),
                "type": agent_config["type"],
                "enabled_tools": enabled_tools,
                "tool_count": len(agent_tools),
                "status": "active",
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Created Agent Builder agent {agent_id} with {len(agent_tools)} tools")
            
            return created_agent
            
        except Exception as e:
            logger.error(f"Failed to create agent with tools: {e}")
            raise
    
    async def get_available_connectors(self) -> List[Dict[str, Any]]:
        """Get list of available Agent Space connectors"""
        try:
            connectors = []
            
            for connector_type, config in self.config.AGENT_SPACE_CONNECTORS.items():
                connectors.append({
                    "connector_id": config["connector_id"],
                    "connector_type": connector_type,
                    "display_name": config["display_name"],
                    "description": config["description"],
                    "enabled": config["enabled"],
                    "oauth_required": config["oauth_required"],
                    "capabilities": config["configuration"]["capabilities"],
                    "required_scopes": config["configuration"]["scopes"]
                })
            
            return connectors
            
        except Exception as e:
            logger.error(f"Failed to get available connectors: {e}")
            raise
    
    async def get_connector_oauth_url(
        self,
        connector_type: str,
        organization_id: str,
        redirect_uri: Optional[str] = None
    ) -> str:
        """
        Get OAuth authorization URL for connector
        
        Args:
            connector_type: Type of connector
            organization_id: Organization ID
            redirect_uri: OAuth redirect URI
            
        Returns:
            OAuth authorization URL
        """
        try:
            if connector_type not in self.config.AGENT_SPACE_CONNECTORS:
                raise ValueError(f"Unknown connector type: {connector_type}")
            
            connector_config = self.config.AGENT_SPACE_CONNECTORS[connector_type]
            
            if not connector_config["oauth_required"]:
                raise ValueError(f"Connector {connector_type} does not require OAuth")
            
            # Build OAuth URL
            scopes = connector_config["configuration"]["scopes"]
            scope_string = " ".join(scopes)
            
            # In production, this would use the actual OAuth flow
            # For Agent Space, OAuth is typically handled through the Agent Builder UI
            oauth_url = (
                f"https://accounts.google.com/o/oauth2/v2/auth?"
                f"client_id={self.config.CLIENT_ID}&"
                f"redirect_uri={redirect_uri or self.config.REDIRECT_URI}&"
                f"scope={scope_string}&"
                f"response_type=code&"
                f"state={organization_id}:{connector_type}&"
                f"access_type=offline&"
                f"prompt=consent"
            )
            
            return oauth_url
            
        except Exception as e:
            logger.error(f"Failed to get OAuth URL: {e}")
            raise
    
    async def handle_oauth_callback(
        self,
        organization_id: str,
        connector_type: str,
        authorization_code: str
    ) -> Dict[str, Any]:
        """
        Handle OAuth callback and store credentials
        
        Args:
            organization_id: Organization ID
            connector_type: Connector type
            authorization_code: OAuth authorization code
            
        Returns:
            OAuth result
        """
        try:
            if connector_type not in self.config.AGENT_SPACE_CONNECTORS:
                raise ValueError(f"Unknown connector type: {connector_type}")
            
            # In production, this would exchange the code for tokens
            # For Agent Space, this is typically handled automatically
            
            # Store OAuth credentials (mock implementation)
            credential_key = f"{organization_id}:{connector_type}"
            self._oauth_credentials[credential_key] = {
                "connector_type": connector_type,
                "organization_id": organization_id,
                "authorized": True,
                "authorized_at": datetime.utcnow().isoformat(),
                "scopes": self.config.AGENT_SPACE_CONNECTORS[connector_type]["configuration"]["scopes"]
            }
            
            logger.info(f"OAuth configured for {connector_type} in organization {organization_id}")
            
            return {
                "success": True,
                "connector_type": connector_type,
                "organization_id": organization_id,
                "authorized": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to handle OAuth callback: {e}")
            return {
                "success": False,
                "error": str(e),
                "connector_type": connector_type,
                "organization_id": organization_id
            }
    
    async def check_connector_status(
        self,
        organization_id: str,
        connector_type: str
    ) -> Dict[str, Any]:
        """Check status of a connector for an organization"""
        try:
            if connector_type not in self.config.AGENT_SPACE_CONNECTORS:
                raise ValueError(f"Unknown connector type: {connector_type}")
            
            connector_config = self.config.AGENT_SPACE_CONNECTORS[connector_type]
            credential_key = f"{organization_id}:{connector_type}"
            
            # Check OAuth status
            oauth_configured = False
            if connector_config["oauth_required"]:
                oauth_configured = credential_key in self._oauth_credentials
            else:
                oauth_configured = True  # No OAuth required
            
            return {
                "connector_type": connector_type,
                "organization_id": organization_id,
                "enabled": connector_config["enabled"],
                "oauth_required": connector_config["oauth_required"],
                "oauth_configured": oauth_configured,
                "capabilities": connector_config["configuration"]["capabilities"],
                "status": "ready" if oauth_configured else "oauth_required",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to check connector status: {e}")
            raise
    
    async def get_organization_connectors(
        self,
        organization_id: str
    ) -> List[Dict[str, Any]]:
        """Get all configured connectors for an organization"""
        try:
            connectors = []
            
            for connector_type in self.config.AGENT_SPACE_CONNECTORS.keys():
                status = await self.check_connector_status(organization_id, connector_type)
                connectors.append(status)
            
            return connectors
            
        except Exception as e:
            logger.error(f"Failed to get organization connectors: {e}")
            raise
    
    async def _configure_oauth(
        self,
        organization_id: str,
        connector_type: str,
        credentials: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Configure OAuth for a connector"""
        try:
            if not credentials:
                return {"success": False, "error": "No credentials provided"}
            
            # In production, this would validate and store the OAuth credentials
            # For Agent Space, OAuth is typically managed through the platform
            
            credential_key = f"{organization_id}:{connector_type}"
            self._oauth_credentials[credential_key] = {
                "connector_type": connector_type,
                "organization_id": organization_id,
                "credentials": credentials,
                "configured_at": datetime.utcnow().isoformat()
            }
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Failed to configure OAuth: {e}")
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Agent Space connector manager health"""
        try:
            available_connectors = await self.get_available_connectors()
            
            return {
                "status": "healthy",
                "available_connectors": len(available_connectors),
                "oauth_credentials_stored": len(self._oauth_credentials),
                "project_id": self.project_id,
                "location": self.location,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global instance
agent_space_connector_manager = AgentSpaceConnectorManager()