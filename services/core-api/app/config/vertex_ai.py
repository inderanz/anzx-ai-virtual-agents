"""
Vertex AI Agent Builder configuration with Workload Identity Federation
"""

import os
from typing import Dict, Any, List


class VertexAIConfig:
    """Vertex AI Agent Builder configuration settings"""
    
    # Google Cloud Project settings
    PROJECT_ID: str = os.getenv("GOOGLE_CLOUD_PROJECT", "anzx-ai-platform")
    LOCATION: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    
    # Workload Identity Federation settings
    # For GKE: Uses Kubernetes Service Account mapped to Google Service Account
    # For Cloud Run: Uses default service account with proper IAM roles
    KUBERNETES_SERVICE_ACCOUNT: str = os.getenv("KUBERNETES_SERVICE_ACCOUNT", "anzx-vertex-ai-sa")
    GOOGLE_SERVICE_ACCOUNT: str = os.getenv("GOOGLE_SERVICE_ACCOUNT", f"vertex-ai-service@{os.getenv('GOOGLE_CLOUD_PROJECT', 'anzx-ai-platform')}.iam.gserviceaccount.com")
    
    # Runtime environment detection
    RUNTIME_ENVIRONMENT: str = os.getenv("RUNTIME_ENVIRONMENT", "cloudrun")  # gke, cloudrun, local
    
    # Authentication scopes for Vertex AI
    REQUIRED_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/aiplatform",
        "https://www.googleapis.com/auth/discoveryengine"
    ]
    
    # Agent Builder settings
    AGENT_BUILDER_LOCATION: str = os.getenv("AGENT_BUILDER_LOCATION", "global")
    DATA_STORE_LOCATION: str = os.getenv("DATA_STORE_LOCATION", "global")
    
    # Model configurations
    DEFAULT_MODEL: str = os.getenv("VERTEX_AI_DEFAULT_MODEL", "gemini-1.0-pro")
    EMBEDDING_MODEL: str = os.getenv("VERTEX_AI_EMBEDDING_MODEL", "text-embedding-004")
    
    # Agent templates configuration
    AGENT_TEMPLATES: Dict[str, Dict[str, Any]] = {
        "support": {
            "display_name": "Customer Support Agent",
            "description": "AI assistant for customer support and help desk operations",
            "default_language_code": "en",
            "time_zone": "Australia/Sydney",
            "avatar_uri": "",
            "enable_stackdriver_logging": True,
            "enable_spell_check": True,
            "classification_threshold": 0.3,
            "api_version": "v2beta1",
            "supported_language_codes": ["en", "en-AU"],
            "intents": [
                {
                    "display_name": "Default Welcome Intent",
                    "priority": 500000,
                    "is_fallback": False,
                    "training_phrases": [
                        "Hi", "Hello", "Good morning", "Good afternoon", "Good evening",
                        "Hey", "I need help", "Can you help me", "Support"
                    ],
                    "messages": [
                        {
                            "text": "Hello! I'm your AI support assistant. How can I help you today?"
                        }
                    ]
                },
                {
                    "display_name": "Default Fallback Intent",
                    "priority": 500000,
                    "is_fallback": True,
                    "messages": [
                        {
                            "text": "I'm sorry, I didn't understand that. Could you please rephrase your question or let me connect you with a human agent?"
                        }
                    ]
                }
            ],
            "entities": [
                {
                    "display_name": "product",
                    "kind": "KIND_MAP",
                    "entries": [
                        {"value": "billing", "synonyms": ["payment", "invoice", "subscription", "plan"]},
                        {"value": "technical", "synonyms": ["bug", "error", "issue", "problem"]},
                        {"value": "account", "synonyms": ["profile", "settings", "login", "password"]}
                    ]
                }
            ],
            "webhooks": {
                "enabled": True,
                "url": "/api/v1/agents/webhooks/support",
                "headers": {
                    "Authorization": "Bearer {webhook_token}"
                }
            }
        },
        "admin": {
            "display_name": "Administrative Assistant",
            "description": "AI assistant for administrative tasks, scheduling, and office management",
            "default_language_code": "en",
            "time_zone": "Australia/Sydney",
            "avatar_uri": "",
            "enable_stackdriver_logging": True,
            "enable_spell_check": True,
            "classification_threshold": 0.3,
            "api_version": "v2beta1",
            "supported_language_codes": ["en", "en-AU"],
            "intents": [
                {
                    "display_name": "Schedule Meeting",
                    "priority": 500000,
                    "training_phrases": [
                        "Schedule a meeting", "Book a meeting", "Set up a call",
                        "Arrange a meeting", "Plan a meeting", "Calendar booking"
                    ],
                    "parameters": [
                        {
                            "display_name": "date-time",
                            "entity_type": "@sys.date-time",
                            "mandatory": True,
                            "prompts": ["When would you like to schedule the meeting?"]
                        },
                        {
                            "display_name": "duration",
                            "entity_type": "@sys.duration",
                            "mandatory": False
                        }
                    ]
                },
                {
                    "display_name": "Send Email",
                    "priority": 500000,
                    "training_phrases": [
                        "Send an email", "Compose email", "Write email",
                        "Email someone", "Send message"
                    ],
                    "parameters": [
                        {
                            "display_name": "email",
                            "entity_type": "@sys.email",
                            "mandatory": True,
                            "prompts": ["Who would you like to send the email to?"]
                        },
                        {
                            "display_name": "subject",
                            "entity_type": "@sys.any",
                            "mandatory": True,
                            "prompts": ["What's the subject of the email?"]
                        }
                    ]
                }
            ],
            "webhooks": {
                "enabled": True,
                "url": "/api/v1/agents/webhooks/admin",
                "headers": {
                    "Authorization": "Bearer {webhook_token}"
                }
            }
        }
    }
    
    # Conversation settings
    CONVERSATION_SETTINGS: Dict[str, Any] = {
        "max_conversation_history": 50,
        "session_timeout_minutes": 30,
        "enable_conversation_summarization": True,
        "enable_sentiment_analysis": True,
        "enable_auto_escalation": True,
        "escalation_threshold": 0.7,
        "max_retry_attempts": 3
    }
    
    # Knowledge base settings
    KNOWLEDGE_BASE_SETTINGS: Dict[str, Any] = {
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "similarity_threshold": 0.7,
        "max_results": 10,
        "enable_reranking": True,
        "citation_style": "numbered"
    }
    
    # Performance settings
    PERFORMANCE_SETTINGS: Dict[str, Any] = {
        "request_timeout": 30,
        "max_concurrent_requests": 100,
        "retry_attempts": 3,
        "retry_delay": 1.0,
        "enable_caching": True,
        "cache_ttl": 300
    }
    
    @classmethod
    def get_agent_template(cls, agent_type: str) -> Dict[str, Any]:
        """Get agent template configuration"""
        return cls.AGENT_TEMPLATES.get(agent_type, cls.AGENT_TEMPLATES["support"])
    
    @classmethod
    def get_project_path(cls) -> str:
        """Get Google Cloud project path"""
        return f"projects/{cls.PROJECT_ID}"
    
    @classmethod
    def get_location_path(cls) -> str:
        """Get location path for Vertex AI"""
        return f"projects/{cls.PROJECT_ID}/locations/{cls.LOCATION}"
    
    @classmethod
    def get_agent_builder_location_path(cls) -> str:
        """Get location path for Agent Builder"""
        return f"projects/{cls.PROJECT_ID}/locations/{cls.AGENT_BUILDER_LOCATION}"
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Validate configuration settings"""
        return {
            "project_id_set": bool(cls.PROJECT_ID),
            "location_set": bool(cls.LOCATION),
            "runtime_environment_set": bool(cls.RUNTIME_ENVIRONMENT),
            "service_account_configured": bool(cls.GOOGLE_SERVICE_ACCOUNT),
            "agent_templates_configured": len(cls.AGENT_TEMPLATES) > 0,
            "conversation_settings_configured": len(cls.CONVERSATION_SETTINGS) > 0
        }
    
    @classmethod
    def get_authentication_info(cls) -> Dict[str, str]:
        """Get authentication configuration info"""
        return {
            "runtime_environment": cls.RUNTIME_ENVIRONMENT,
            "google_service_account": cls.GOOGLE_SERVICE_ACCOUNT,
            "kubernetes_service_account": cls.KUBERNETES_SERVICE_ACCOUNT if cls.RUNTIME_ENVIRONMENT == "gke" else "N/A",
            "project_id": cls.PROJECT_ID,
            "required_scopes": ", ".join(cls.REQUIRED_SCOPES)
        }


# Global config instance
vertex_ai_config = VertexAIConfig()