"""
Tests for AI Assistant Implementations
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session

from app.services.assistant_factory import assistant_factory, BaseAssistant
from app.assistants.admin_assistant import AdminAssistant
from app.assistants.content_assistant import ContentAssistant
from app.assistants.insights_assistant import InsightsAssistant
from app.config.assistant_config import get_assistant_template, validate_assistant_config


class TestAssistantFactory:
    """Test the assistant factory functionality"""
    
    def test_get_available_types(self):
        """Test getting available assistant types"""
        types = assistant_factory.get_available_types()
        expected_types = ["support", "sales", "technical", "admin", "content", "insights"]
        
        for expected_type in expected_types:
            assert expected_type in types
    
    @pytest.mark.asyncio
    async def test_create_assistant(self):
        """Test creating different assistant types"""
        db_mock = Mock(spec=Session)
        
        # Test creating support assistant
        config = {
            "organization_id": "test_org",
            "organization_name": "Test Organization"
        }
        
        with patch('app.services.assistant_factory.mcp_tool_registry') as mock_registry:
            mock_registry.get_available_tools = AsyncMock(return_value=[])
            
            assistant = await assistant_factory.create_assistant(
                db=db_mock,
                assistant_type="support",
                assistant_id="test_support",
                config=config
            )
            
            assert assistant is not None
            assert assistant.type == "support"
            assert assistant.assistant_id == "test_support"
    
    @pytest.mark.asyncio
    async def test_get_assistant_capabilities(self):
        """Test getting assistant capabilities"""
        capabilities = await assistant_factory.get_assistant_capabilities("support")
        
        assert "type" in capabilities
        assert "capabilities" in capabilities
        assert "escalation_triggers" in capabilities
        assert capabilities["type"] == "support"
    
    def test_invalid_assistant_type(self):
        """Test creating assistant with invalid type"""
        db_mock = Mock(spec=Session)
        
        with pytest.raises(ValueError):
            assistant_factory.create_assistant(
                db=db_mock,
                assistant_type="invalid_type",
                assistant_id="test",
                config={}
            )


class TestAdminAssistant:
    """Test the Admin Assistant implementation"""
    
    @pytest.fixture
    def admin_assistant(self):
        """Create admin assistant instance for testing"""
        config = {
            "organization_id": "test_org",
            "organization_name": "Test Organization"
        }
        return AdminAssistant("test_admin", config)
    
    @pytest.mark.asyncio
    async def test_initialize(self, admin_assistant):
        """Test admin assistant initialization"""
        db_mock = Mock(spec=Session)
        
        with patch('app.assistants.admin_assistant.agent_space_connector_manager') as mock_manager:
            mock_manager.initialize_agent = AsyncMock()
            
            with patch.object(admin_assistant, 'get_available_tools', return_value=[]):
                result = await admin_assistant.initialize(db_mock)
                
                assert result["type"] == "admin"
                assert "capabilities" in result
                assert "agent_space_enabled" in result
    
    @pytest.mark.asyncio
    async def test_analyze_admin_message(self, admin_assistant):
        """Test admin message analysis"""
        # Test scheduling message
        message = "Schedule a meeting with John for tomorrow at 2pm"
        analysis = await admin_assistant._analyze_admin_message(message)
        
        assert analysis["category"] == "scheduling"
        assert analysis["requires_calendar"] is True
        assert "scheduling_details" in analysis
    
    def test_extract_scheduling_details(self, admin_assistant):
        """Test extracting scheduling details from message"""
        message = "Schedule a 1 hour meeting with john@example.com tomorrow at 2pm"
        details = admin_assistant._extract_scheduling_details(message)
        
        assert "participants" in details
        assert "john@example.com" in details["participants"]
        assert details["action_required"] is True


class TestContentAssistant:
    """Test the Content Assistant implementation"""
    
    @pytest.fixture
    def content_assistant(self):
        """Create content assistant instance for testing"""
        config = {
            "organization_id": "test_org",
            "organization_name": "Test Organization"
        }
        return ContentAssistant("test_content", config)
    
    @pytest.mark.asyncio
    async def test_initialize(self, content_assistant):
        """Test content assistant initialization"""
        db_mock = Mock(spec=Session)
        
        with patch('app.assistants.content_assistant.hybrid_agent_orchestrator') as mock_orchestrator:
            mock_orchestrator.register_workflow = AsyncMock()
            
            with patch.object(content_assistant, 'get_available_tools', return_value=[]):
                result = await content_assistant.initialize(db_mock)
                
                assert result["type"] == "content"
                assert "capabilities" in result
                assert result["custom_workflows"] is True
    
    @pytest.mark.asyncio
    async def test_analyze_content_message(self, content_assistant):
        """Test content message analysis"""
        # Test content generation message
        message = "Create a blog post about AI for small businesses"
        analysis = await content_assistant._analyze_content_message(message)
        
        assert analysis["category"] == "generation"
        assert "content_details" in analysis
        assert analysis["requires_content_action"] is True
    
    def test_extract_content_details(self, content_assistant):
        """Test extracting content details from message"""
        message = "Write a professional blog post about AI for small business owners, 800 words"
        details = content_assistant._extract_content_details(message)
        
        assert details["content_type"] == "blog post"
        assert details["tone"] == "professional"
        assert details["length"] == "800"


class TestInsightsAssistant:
    """Test the Insights Assistant implementation"""
    
    @pytest.fixture
    def insights_assistant(self):
        """Create insights assistant instance for testing"""
        config = {
            "organization_id": "test_org",
            "organization_name": "Test Organization"
        }
        return InsightsAssistant("test_insights", config)
    
    @pytest.mark.asyncio
    async def test_initialize(self, insights_assistant):
        """Test insights assistant initialization"""
        db_mock = Mock(spec=Session)
        
        with patch('app.assistants.insights_assistant.hybrid_agent_orchestrator') as mock_orchestrator:
            mock_orchestrator.register_workflow = AsyncMock()
            
            with patch.object(insights_assistant, 'get_available_tools', return_value=[]):
                result = await insights_assistant.initialize(db_mock)
                
                assert result["type"] == "insights"
                assert "capabilities" in result
                assert result["analytics_integration"] is True
    
    @pytest.mark.asyncio
    async def test_analyze_insights_message(self, insights_assistant):
        """Test insights message analysis"""
        # Test analytics message
        message = "Analyze sales trends for the last 3 months"
        analysis = await insights_assistant._analyze_insights_message(message)
        
        assert analysis["category"] == "trends"
        assert "sales" in analysis["data_sources"]
        assert analysis["requires_analytics_action"] is True
    
    def test_extract_query_details(self, insights_assistant):
        """Test extracting query details from message"""
        message = "Show me total revenue vs last month for customers in the US"
        details = insights_assistant._extract_query_details(message)
        
        assert "revenue" in details["metrics"]
        assert details["comparison"] is True
        assert details["aggregation"] == "sum"


class TestAssistantConfiguration:
    """Test assistant configuration functionality"""
    
    def test_get_assistant_template(self):
        """Test getting assistant templates"""
        support_template = get_assistant_template("support")
        assert support_template["name"] == "Support Assistant"
        assert "capabilities" in support_template
        assert "system_prompt_template" in support_template
        
        # Test invalid template
        invalid_template = get_assistant_template("invalid")
        assert invalid_template == {}
    
    def test_validate_assistant_config(self):
        """Test assistant configuration validation"""
        # Valid config
        valid_config = {
            "name": "Test Assistant",
            "type": "support",
            "capabilities": ["communication", "technical"]
        }
        assert validate_assistant_config(valid_config) is True
        
        # Invalid config - missing required fields
        invalid_config = {
            "name": "Test Assistant"
        }
        assert validate_assistant_config(invalid_config) is False
        
        # Invalid config - invalid type
        invalid_type_config = {
            "name": "Test Assistant",
            "type": "invalid_type",
            "capabilities": ["communication"]
        }
        assert validate_assistant_config(invalid_type_config) is False


class TestBaseAssistantFunctionality:
    """Test base assistant functionality"""
    
    @pytest.fixture
    def mock_assistant(self):
        """Create a mock assistant for testing"""
        class MockAssistant(BaseAssistant):
            async def initialize(self, db):
                return {"type": "mock"}
            
            async def process_message(self, db, message, context, user_context=None):
                return {"response": "mock response"}
            
            async def should_escalate(self, db, context):
                return {"should_escalate": False}
        
        return MockAssistant("test_mock", {})
    
    @pytest.mark.asyncio
    async def test_get_available_tools(self, mock_assistant):
        """Test getting available tools"""
        db_mock = Mock(spec=Session)
        
        with patch('app.services.assistant_factory.mcp_tool_registry') as mock_registry:
            mock_tools = [
                {"tool_id": "test_tool", "category": "general"},
                {"tool_id": "restricted_tool", "category": "restricted"}
            ]
            mock_registry.get_available_tools = AsyncMock(return_value=mock_tools)
            
            mock_assistant.capabilities = ["general"]
            tools = await mock_assistant.get_available_tools(db_mock)
            
            # Should only return tools that match capabilities
            assert len(tools) == 1
            assert tools[0]["tool_id"] == "test_tool"
    
    def test_build_system_prompt(self, mock_assistant):
        """Test building system prompt with context"""
        base_prompt = "You are a test assistant."
        context = {
            "organization_name": "Test Org",
            "available_tools": [{"name": "test_tool"}]
        }
        
        prompt = mock_assistant._build_system_prompt(base_prompt, context)
        
        assert "You are a test assistant." in prompt
        assert "Test Org" in prompt
        assert "test_tool" in prompt


@pytest.mark.integration
class TestAssistantIntegration:
    """Integration tests for assistant functionality"""
    
    @pytest.mark.asyncio
    async def test_full_assistant_workflow(self):
        """Test complete assistant workflow from creation to message processing"""
        db_mock = Mock(spec=Session)
        
        # Mock all external dependencies
        with patch('app.services.assistant_factory.mcp_tool_registry') as mock_registry, \
             patch('app.services.vertex_ai_service.vertex_ai_service') as mock_vertex:
            
            mock_registry.get_available_tools = AsyncMock(return_value=[])
            mock_vertex.generate_response = AsyncMock(return_value={
                "content": "Test response",
                "metadata": {}
            })
            
            # Create assistant
            config = {
                "organization_id": "test_org",
                "organization_name": "Test Organization"
            }
            
            assistant = await assistant_factory.create_assistant(
                db=db_mock,
                assistant_type="support",
                assistant_id="test_support",
                config=config
            )
            
            # Process message
            message = "I need help with my account"
            context = {"conversation_id": "test_conv"}
            
            response = await assistant.process_message(
                db=db_mock,
                message=message,
                conversation_context=context
            )
            
            assert "response" in response
            assert "analysis" in response
            assert response["metadata"]["assistant_type"] == "support"