"""
Base Assistant Class
Abstract base class for all AI assistant implementations
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from ..models.user import Assistant, Conversation, Organization

logger = logging.getLogger(__name__)


class BaseAssistant(ABC):
    """
    Abstract base class for AI assistants
    
    Provides common functionality and interface for all assistant types
    """
    
    def __init__(self):
        self.assistant_type = "base"
        self.capabilities = []
        self.required_tools = []
        self.default_config = {}
    
    @abstractmethod
    async def initialize_assistant(
        self,
        db: Session,
        assistant: Assistant,
        organization: Organization
    ) -> Dict[str, Any]:
        """
        Initialize the assistant with organization-specific configuration
        
        Args:
            db: Database session
            assistant: Assistant model instance
            organization: Organization model instance
            
        Returns:
            Initialization result
        """
        pass
    
    @abstractmethod
    async def process_message(
        self,
        db: Session,
        assistant: Assistant,
        conversation: Conversation,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate response
        
        Args:
            db: Database session
            assistant: Assistant model instance
            conversation: Conversation model instance
            user_message: User's message
            context: Additional context
            
        Returns:
            Response data including message and metadata
        """
        pass
    
    async def validate_configuration(
        self,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate assistant configuration
        
        Args:
            config: Configuration to validate
            
        Returns:
            Validation result
        """
        try:
            # Basic validation - can be overridden by subclasses
            required_fields = getattr(self, 'required_config_fields', [])
            
            for field in required_fields:
                if field not in config:
                    return {
                        "valid": False,
                        "error": f"Missing required configuration field: {field}"
                    }
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    async def get_capabilities(self) -> List[str]:
        """Get assistant capabilities"""
        return self.capabilities.copy()
    
    async def get_required_tools(self) -> List[str]:
        """Get required tools for this assistant"""
        return self.required_tools.copy()
    
    async def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for this assistant"""
        return self.default_config.copy()
    
    def _log_interaction(
        self,
        assistant_id: str,
        conversation_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log assistant interaction"""
        log_data = {
            "assistant_id": assistant_id,
            "conversation_id": conversation_id,
            "action": action,
            "assistant_type": self.assistant_type
        }
        
        if details:
            log_data.update(details)
        
        logger.info(f"Assistant interaction: {log_data}")
    
    def _format_response(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format assistant response"""
        return {
            "response": content,
            "metadata": {
                "assistant_type": self.assistant_type,
                **(metadata or {})
            }
        }