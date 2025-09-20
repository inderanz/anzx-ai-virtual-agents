"""
Mock Vertex AI Service for Development
Provides mock responses without requiring Google Cloud dependencies
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class MockVertexAIService:
    """Mock Vertex AI service for development"""
    
    def __init__(self):
        self.is_initialized = False
        self.project_id = "extreme-gecko-466211-t1"
        self.location = "australia-southeast1"
    
    async def initialize(self):
        """Initialize the mock service"""
        try:
            logger.info("Initializing Mock Vertex AI service")
            self.is_initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Mock Vertex AI service: {e}")
            return False
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: str = "gemini-1.5-pro",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a mock response"""
        try:
            # Simulate processing time
            await asyncio.sleep(0.1)
            
            # Get the last user message
            user_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            
            # Generate mock response based on message content
            mock_responses = {
                "hello": "Hello! How can I assist you today?",
                "help": "I'm here to help! What do you need assistance with?",
                "support": "I'm your support assistant. I can help you with technical issues, account questions, and general inquiries.",
                "sales": "I'm your sales assistant. I can help you learn about our products and services, and guide you through the sales process.",
                "admin": "I'm your admin assistant. I can help you with scheduling, calendar management, and administrative tasks.",
                "content": "I'm your content assistant. I can help you create engaging content that aligns with your brand voice.",
                "insights": "I'm your insights assistant. I can help you analyze data and generate actionable business insights."
            }
            
            # Find appropriate response
            response_text = "Thank you for your message. I'm a mock AI assistant and I'm here to help!"
            for keyword, response in mock_responses.items():
                if keyword.lower() in user_message.lower():
                    response_text = response
                    break
            
            # Add context-aware response
            if len(user_message) > 100:
                response_text += " I can see you've provided detailed information, and I'll do my best to address all your points."
            
            return {
                "content": response_text,
                "metadata": {
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "tokens_input": len(user_message.split()),
                    "tokens_output": len(response_text.split()),
                    "latency_ms": 100,
                    "mock": True
                }
            }
            
        except Exception as e:
            logger.error(f"Mock response generation failed: {e}")
            return {
                "content": "I apologize, but I'm having trouble processing your request right now. Please try again.",
                "metadata": {
                    "error": str(e),
                    "mock": True
                }
            }
    
    async def create_agent(
        self,
        name: str,
        description: str,
        instructions: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a mock agent"""
        try:
            agent_id = f"mock-agent-{hash(name) % 10000}"
            
            return {
                "agent_id": agent_id,
                "name": name,
                "description": description,
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "mock": True
            }
            
        except Exception as e:
            logger.error(f"Mock agent creation failed: {e}")
            return {"error": str(e), "mock": True}
    
    async def chat_with_agent(
        self,
        agent_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Chat with a mock agent"""
        try:
            # Simulate processing time
            await asyncio.sleep(0.2)
            
            response = await self.generate_response([
                {"role": "user", "content": message}
            ])
            
            return {
                "agent_id": agent_id,
                "conversation_id": conversation_id or f"mock-conv-{hash(message) % 10000}",
                "response": response["content"],
                "metadata": {
                    **response["metadata"],
                    "agent_id": agent_id
                }
            }
            
        except Exception as e:
            logger.error(f"Mock agent chat failed: {e}")
            return {"error": str(e), "mock": True}
    
    def get_available_models(self) -> List[str]:
        """Get list of available mock models"""
        return [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro"
        ]
    
    def is_healthy(self) -> bool:
        """Check if the mock service is healthy"""
        return self.is_initialized


# Global mock service instance
vertex_ai_service = MockVertexAIService()