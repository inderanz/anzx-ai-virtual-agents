"""
Tool Registry for Agent Builder Function Calling
Based on Google Cloud Platform agent-starter-pack architecture
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum

try:
    from vertexai.generative_models import FunctionDeclaration, Tool
    from google.cloud import discoveryengine_v1beta as discoveryengine
except ImportError as e:
    logging.warning(f"Vertex AI dependencies not installed: {e}")
    # Mock classes for development
    class FunctionDeclaration:
        def __init__(self, **kwargs): pass
    class Tool:
        def __init__(self, **kwargs): pass

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Tool categories for organization"""
    COMMUNICATION = "communication"
    CALENDAR = "calendar"
    DOCUMENT = "document"
    ANALYTICS = "analytics"
    BILLING = "billing"
    CUSTOM = "custom"


class ToolRegistry:
    """
    Central registry for Agent Builder function declarations
    Following agent-starter-pack pattern for tool management
    """
    
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._function_handlers: Dict[str, Callable] = {}
        self._tool_categories: Dict[str, ToolCategory] = {}
        
        # Initialize built-in tools following agent-starter-pack approach
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Register built-in tools following agent-starter-pack architecture"""
        
        # Gmail/Email tools
        self.register_tool(
            name="send_email",
            category=ToolCategory.COMMUNICATION,
            description="Send an email via Gmail",
            parameters={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string", 
                        "description": "Email subject line"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content"
                    },
                    "cc": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "CC recipients (optional)"
                    }
                },
                "required": ["to", "subject", "body"]
            },
            handler=self._handle_send_email
        )
        
        self.register_tool(
            name="search_emails",
            category=ToolCategory.COMMUNICATION,
            description="Search emails in Gmail",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Gmail search query (e.g., 'from:user@example.com')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            },
            handler=self._handle_search_emails
        )
        
        # Calendar tools
        self.register_tool(
            name="create_calendar_event",
            category=ToolCategory.CALENDAR,
            description="Create a new calendar event",
            parameters={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Event title"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time in ISO format (e.g., '2024-01-15T10:00:00')"
                    },
                    "end_time": {
                        "type": "string", 
                        "description": "End time in ISO format"
                    },
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of attendee email addresses"
                    },
                    "description": {
                        "type": "string",
                        "description": "Event description (optional)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Event location (optional)"
                    }
                },
                "required": ["title", "start_time", "end_time"]
            },
            handler=self._handle_create_calendar_event
        )
        
        self.register_tool(
            name="find_available_time",
            category=ToolCategory.CALENDAR,
            description="Find available time slots for scheduling",
            parameters={
                "type": "object",
                "properties": {
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of attendee email addresses"
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Meeting duration in minutes"
                    },
                    "preferred_start_date": {
                        "type": "string",
                        "description": "Preferred start date for search (ISO format)"
                    },
                    "preferred_end_date": {
                        "type": "string",
                        "description": "End date for search range (ISO format)"
                    },
                    "working_hours_only": {
                        "type": "boolean",
                        "description": "Only consider working hours (9 AM - 5 PM)",
                        "default": True
                    }
                },
                "required": ["attendees", "duration_minutes"]
            },
            handler=self._handle_find_available_time
        )
        
        # Document/Drive tools
        self.register_tool(
            name="search_documents",
            category=ToolCategory.DOCUMENT,
            description="Search documents in Google Drive",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for documents"
                    },
                    "file_type": {
                        "type": "string",
                        "description": "File type filter (docs, sheets, slides, pdf)",
                        "enum": ["docs", "sheets", "slides", "pdf", "all"]
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["query"]
            },
            handler=self._handle_search_documents
        )
        
        self.register_tool(
            name="create_document",
            category=ToolCategory.DOCUMENT,
            description="Create a new Google Docs document",
            parameters={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Document title"
                    },
                    "content": {
                        "type": "string",
                        "description": "Initial document content (optional)"
                    },
                    "folder_id": {
                        "type": "string",
                        "description": "Google Drive folder ID to create document in (optional)"
                    }
                },
                "required": ["title"]
            },
            handler=self._handle_create_document
        )
        
        # Knowledge base search tool
        self.register_tool(
            name="search_knowledge_base",
            category=ToolCategory.CUSTOM,
            description="Search the organization's knowledge base",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for knowledge base"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 5
                    },
                    "source_filter": {
                        "type": "string",
                        "description": "Filter by knowledge source (optional)"
                    }
                },
                "required": ["query"]
            },
            handler=self._handle_search_knowledge_base
        )
        
        logger.info(f"Registered {len(self._tools)} built-in tools")
    
    def register_tool(
        self,
        name: str,
        category: ToolCategory,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable
    ):
        """Register a new tool with the registry"""
        try:
            self._tools[name] = {
                "name": name,
                "category": category,
                "description": description,
                "parameters": parameters,
                "registered_at": datetime.utcnow().isoformat()
            }
            
            self._function_handlers[name] = handler
            self._tool_categories[name] = category
            
            logger.info(f"Registered tool: {name} in category {category.value}")
            
        except Exception as e:
            logger.error(f"Failed to register tool {name}: {e}")
            raise
    
    def get_function_declarations(self, tool_names: List[str]) -> List[FunctionDeclaration]:
        """Get function declarations for specified tools"""
        try:
            declarations = []
            
            for tool_name in tool_names:
                if tool_name not in self._tools:
                    logger.warning(f"Tool {tool_name} not found in registry")
                    continue
                
                tool_config = self._tools[tool_name]
                
                declaration = FunctionDeclaration(
                    name=tool_config["name"],
                    description=tool_config["description"],
                    parameters=tool_config["parameters"]
                )
                
                declarations.append(declaration)
            
            logger.info(f"Generated {len(declarations)} function declarations")
            return declarations
            
        except Exception as e:
            logger.error(f"Failed to get function declarations: {e}")
            raise
    
    def get_tools_for_agent_type(self, agent_type: str) -> List[str]:
        """Get recommended tools for specific agent type"""
        tool_mappings = {
            "support": [
                "search_knowledge_base",
                "send_email",
                "search_emails",
                "search_documents"
            ],
            "admin": [
                "create_calendar_event",
                "find_available_time", 
                "send_email",
                "create_document",
                "search_documents"
            ],
            "content": [
                "create_document",
                "search_documents",
                "search_knowledge_base"
            ],
            "insights": [
                "search_documents",
                "search_knowledge_base"
            ]
        }
        
        return tool_mappings.get(agent_type, [])
    
    def get_tools_by_category(self, category: ToolCategory) -> List[str]:
        """Get all tools in a specific category"""
        return [
            name for name, cat in self._tool_categories.items()
            if cat == category
        ]
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool function"""
        try:
            if tool_name not in self._function_handlers:
                raise ValueError(f"Tool {tool_name} not found")
            
            handler = self._function_handlers[tool_name]
            result = await handler(parameters, context)
            
            logger.info(f"Executed tool {tool_name} successfully")
            return {
                "tool_name": tool_name,
                "success": True,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}")
            return {
                "tool_name": tool_name,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # Tool handler implementations (mock for now)
    async def _handle_send_email(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send email tool execution"""
        # In production, this would integrate with Gmail API
        return {
            "message_id": "mock_message_id",
            "status": "sent",
            "to": parameters["to"],
            "subject": parameters["subject"]
        }
    
    async def _handle_search_emails(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email search tool execution"""
        # In production, this would search Gmail
        return {
            "emails": [
                {
                    "id": "mock_email_1",
                    "subject": "Mock Email Subject",
                    "from": "sender@example.com",
                    "snippet": "This is a mock email result..."
                }
            ],
            "total_count": 1
        }
    
    async def _handle_create_calendar_event(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calendar event creation"""
        # In production, this would create Google Calendar event
        return {
            "event_id": "mock_event_id",
            "title": parameters["title"],
            "start_time": parameters["start_time"],
            "end_time": parameters["end_time"],
            "status": "created"
        }
    
    async def _handle_find_available_time(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle finding available time slots"""
        # In production, this would query Google Calendar free/busy
        return {
            "available_slots": [
                {
                    "start_time": "2024-01-15T10:00:00",
                    "end_time": "2024-01-15T11:00:00",
                    "duration_minutes": parameters["duration_minutes"]
                },
                {
                    "start_time": "2024-01-15T14:00:00", 
                    "end_time": "2024-01-15T15:00:00",
                    "duration_minutes": parameters["duration_minutes"]
                }
            ]
        }
    
    async def _handle_search_documents(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle document search in Google Drive"""
        # In production, this would search Google Drive
        return {
            "documents": [
                {
                    "id": "mock_doc_id",
                    "title": "Mock Document",
                    "type": "docs",
                    "url": "https://docs.google.com/document/d/mock_doc_id"
                }
            ],
            "total_count": 1
        }
    
    async def _handle_create_document(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle document creation in Google Docs"""
        # In production, this would create Google Docs document
        return {
            "document_id": "mock_new_doc_id",
            "title": parameters["title"],
            "url": "https://docs.google.com/document/d/mock_new_doc_id",
            "status": "created"
        }
    
    async def _handle_search_knowledge_base(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle knowledge base search"""
        # In production, this would search the organization's knowledge base
        return {
            "results": [
                {
                    "title": "FAQ: How to reset password",
                    "content": "To reset your password, click the 'Forgot Password' link...",
                    "source": "company_faq",
                    "confidence": 0.95
                }
            ],
            "total_count": 1
        }
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        category_counts = {}
        for category in ToolCategory:
            category_counts[category.value] = len(self.get_tools_by_category(category))
        
        return {
            "total_tools": len(self._tools),
            "categories": category_counts,
            "available_tools": list(self._tools.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instance
tool_registry = ToolRegistry()