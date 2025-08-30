"""
Hybrid Agent Orchestration System
Combines Google Agent Space agents with custom LangGraph workflows
Based on the design requirements for Content and Insights agents
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

try:
    from langgraph import StateGraph, END
    from langgraph.graph import Graph
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
    from langchain_core.runnables import RunnableConfig
except ImportError as e:
    logging.warning(f"LangGraph dependencies not installed: {e}")
    # Mock classes for development
    class StateGraph:
        def __init__(self): pass
        def add_node(self, *args): pass
        def add_edge(self, *args): pass
        def set_entry_point(self, *args): pass
        def compile(self): return self
        def invoke(self, *args): return {}
    class Graph: pass
    class BaseMessage: pass
    class HumanMessage: pass
    class AIMessage: pass
    class RunnableConfig: pass
    END = "END"

from .agent_space_connector_manager import AgentSpaceManager
from .vertex_ai_service import vertex_ai_service
from ..config.vertex_ai import vertex_ai_config

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Agent types and their orchestration approach"""
    SUPPORT = "support"          # Agent Space
    ADMIN = "admin"              # Agent Space  
    CONTENT = "content"          # Custom LangGraph
    INSIGHTS = "insights"        # Custom LangGraph


class AgentState:
    """State management for agent workflows"""
    
    def __init__(self):
        self.messages: List[BaseMessage] = []
        self.context: Dict[str, Any] = {}
        self.current_step: str = ""
        self.workflow_data: Dict[str, Any] = {}
        self.agent_type: str = ""
        self.organization_id: str = ""
        self.user_id: Optional[str] = None


class HybridAgentOrchestrator:
    """
    Orchestrates between Agent Space agents and custom LangGraph workflows
    
    Architecture:
    - Support & Admin agents: Use Google Agent Space with built-in tools
    - Content & Insights agents: Use custom LangGraph workflows
    - Routing logic determines which system handles each request
    - Shared context management across all agent types
    """
    
    def __init__(self):
        self.agent_space_manager = AgentSpaceManager()
        self.vertex_ai = vertex_ai_service
        self.config = vertex_ai_config
        
        # Agent routing configuration
        self.agent_routing = {
            AgentType.SUPPORT: "agent_space",
            AgentType.ADMIN: "agent_space", 
            AgentType.CONTENT: "langgraph",
            AgentType.INSIGHTS: "langgraph"
        }
        
        # Initialize custom workflows
        self._content_workflow = None
        self._insights_workflow = None
        self._initialize_custom_workflows()
    
    def _initialize_custom_workflows(self):
        """Initialize custom LangGraph workflows"""
        try:
            self._content_workflow = self._build_content_workflow()
            self._insights_workflow = self._build_insights_workflow()
            logger.info("Custom workflows initialized")
        except Exception as e:
            logger.error(f"Failed to initialize custom workflows: {e}")
    
    async def route_request(
        self,
        agent_type: str,
        message: str,
        context: Dict[str, Any],
        organization_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Route request to appropriate agent system
        
        Args:
            agent_type: Type of agent (support, admin, content, insights)
            message: User message
            context: Request context
            organization_id: Organization ID
            user_id: User ID
            
        Returns:
            Agent response
        """
        try:
            agent_enum = AgentType(agent_type)
            routing_system = self.agent_routing[agent_enum]
            
            logger.info(f"Routing {agent_type} request to {routing_system}")
            
            if routing_system == "agent_space":
                return await self._handle_agent_space_request(
                    agent_type=agent_type,
                    message=message,
                    context=context,
                    organization_id=organization_id,
                    user_id=user_id
                )
            elif routing_system == "langgraph":
                return await self._handle_langgraph_request(
                    agent_type=agent_type,
                    message=message,
                    context=context,
                    organization_id=organization_id,
                    user_id=user_id
                )
            else:
                raise ValueError(f"Unknown routing system: {routing_system}")
                
        except Exception as e:
            logger.error(f"Failed to route request: {e}")
            raise
    
    async def _handle_agent_space_request(
        self,
        agent_type: str,
        message: str,
        context: Dict[str, Any],
        organization_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle request using Agent Space"""
        try:
            # Get agent configuration
            agent_config = self.config.get_agent_config(agent_type)
            agent_id = f"agent_{organization_id}_{agent_type}"
            
            # Use Vertex AI service to interact with Agent Space agent
            response = await self.vertex_ai.chat_with_agent(
                agent_id=agent_id,
                message=message,
                conversation_id=context.get("conversation_id", ""),
                context=context
            )
            
            return {
                "response": response["response"],
                "agent_type": agent_type,
                "system": "agent_space",
                "agent_id": agent_id,
                "metadata": response.get("metadata", {}),
                "citations": response.get("citations", []),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Agent Space request failed: {e}")
            raise
    
    async def _handle_langgraph_request(
        self,
        agent_type: str,
        message: str,
        context: Dict[str, Any],
        organization_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle request using custom LangGraph workflow"""
        try:
            # Initialize state
            state = AgentState()
            state.messages = [HumanMessage(content=message)]
            state.context = context
            state.agent_type = agent_type
            state.organization_id = organization_id
            state.user_id = user_id
            
            # Select appropriate workflow
            if agent_type == "content":
                workflow = self._content_workflow
            elif agent_type == "insights":
                workflow = self._insights_workflow
            else:
                raise ValueError(f"No LangGraph workflow for agent type: {agent_type}")
            
            # Execute workflow
            result = workflow.invoke(state)
            
            # Extract response from workflow result
            if isinstance(result, dict) and "response" in result:
                response_text = result["response"]
            elif hasattr(result, "messages") and result.messages:
                last_message = result.messages[-1]
                response_text = last_message.content if hasattr(last_message, "content") else str(last_message)
            else:
                response_text = str(result)
            
            return {
                "response": response_text,
                "agent_type": agent_type,
                "system": "langgraph",
                "workflow_data": getattr(result, "workflow_data", {}),
                "steps_executed": getattr(result, "current_step", "completed"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"LangGraph request failed: {e}")
            raise
    
    def _build_content_workflow(self) -> StateGraph:
        """Build Content Agent LangGraph workflow"""
        try:
            workflow = StateGraph(AgentState)
            
            # Content creation workflow nodes
            workflow.add_node("analyze_request", self._content_analyze_request)
            workflow.add_node("research_topic", self._content_research_topic)
            workflow.add_node("generate_content", self._content_generate_content)
            workflow.add_node("review_content", self._content_review_content)
            workflow.add_node("finalize_content", self._content_finalize_content)
            
            # Workflow edges
            workflow.set_entry_point("analyze_request")
            workflow.add_edge("analyze_request", "research_topic")
            workflow.add_edge("research_topic", "generate_content")
            workflow.add_edge("generate_content", "review_content")
            workflow.add_edge("review_content", "finalize_content")
            workflow.add_edge("finalize_content", END)
            
            return workflow.compile()
            
        except Exception as e:
            logger.error(f"Failed to build content workflow: {e}")
            raise
    
    def _build_insights_workflow(self) -> StateGraph:
        """Build Insights Agent LangGraph workflow"""
        try:
            workflow = StateGraph(AgentState)
            
            # Data insights workflow nodes
            workflow.add_node("parse_query", self._insights_parse_query)
            workflow.add_node("fetch_data", self._insights_fetch_data)
            workflow.add_node("analyze_data", self._insights_analyze_data)
            workflow.add_node("generate_insights", self._insights_generate_insights)
            workflow.add_node("create_visualization", self._insights_create_visualization)
            workflow.add_node("format_response", self._insights_format_response)
            
            # Workflow edges
            workflow.set_entry_point("parse_query")
            workflow.add_edge("parse_query", "fetch_data")
            workflow.add_edge("fetch_data", "analyze_data")
            workflow.add_edge("analyze_data", "generate_insights")
            workflow.add_edge("generate_insights", "create_visualization")
            workflow.add_edge("create_visualization", "format_response")
            workflow.add_edge("format_response", END)
            
            return workflow.compile()
            
        except Exception as e:
            logger.error(f"Failed to build insights workflow: {e}")
            raise
    
    # Content workflow node implementations
    async def _content_analyze_request(self, state: AgentState) -> AgentState:
        """Analyze content creation request"""
        try:
            message = state.messages[-1].content
            
            # Use Vertex AI to analyze the request
            analysis_prompt = f"""
            Analyze this content creation request and extract:
            1. Content type (blog post, social media, email, etc.)
            2. Target audience
            3. Key topics/themes
            4. Tone and style requirements
            5. Length requirements
            
            Request: {message}
            """
            
            # Mock analysis - in production would use Vertex AI
            state.workflow_data["content_analysis"] = {
                "content_type": "blog_post",
                "audience": "business_professionals", 
                "topics": ["AI", "automation", "productivity"],
                "tone": "professional",
                "length": "medium"
            }
            
            state.current_step = "analyze_request"
            return state
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            raise
    
    async def _content_research_topic(self, state: AgentState) -> AgentState:
        """Research content topics"""
        try:
            analysis = state.workflow_data.get("content_analysis", {})
            topics = analysis.get("topics", [])
            
            # Mock research - in production would use search APIs
            state.workflow_data["research_data"] = {
                "sources": [
                    {"title": "AI Trends 2024", "url": "example.com", "summary": "Latest AI developments"},
                    {"title": "Automation Best Practices", "url": "example.com", "summary": "How to implement automation"}
                ],
                "key_points": [
                    "AI adoption is accelerating in business",
                    "Automation improves productivity by 40%",
                    "Integration challenges remain"
                ]
            }
            
            state.current_step = "research_topic"
            return state
            
        except Exception as e:
            logger.error(f"Content research failed: {e}")
            raise
    
    async def _content_generate_content(self, state: AgentState) -> AgentState:
        """Generate content using Vertex AI"""
        try:
            analysis = state.workflow_data.get("content_analysis", {})
            research = state.workflow_data.get("research_data", {})
            
            # Generate content using Vertex AI
            content_prompt = f"""
            Create a {analysis.get('content_type', 'blog post')} for {analysis.get('audience', 'general audience')}.
            
            Topics: {', '.join(analysis.get('topics', []))}
            Tone: {analysis.get('tone', 'professional')}
            Length: {analysis.get('length', 'medium')}
            
            Research points to include:
            {chr(10).join(research.get('key_points', []))}
            
            Original request: {state.messages[-1].content}
            """
            
            # Mock content generation - in production would use Vertex AI
            generated_content = f"""
            # The Future of AI in Business Automation
            
            Artificial Intelligence is transforming how businesses operate, with automation leading the charge in productivity improvements. Recent studies show that companies implementing AI-driven automation see up to 40% increases in operational efficiency.
            
            ## Key Benefits of AI Automation
            
            1. **Increased Productivity**: Automated processes free up human resources for strategic work
            2. **Reduced Errors**: AI systems maintain consistent accuracy in repetitive tasks
            3. **24/7 Operations**: Automated systems work around the clock without breaks
            
            ## Implementation Challenges
            
            While the benefits are clear, organizations face integration challenges when adopting AI automation. Success requires careful planning and change management.
            
            ## Conclusion
            
            The future belongs to organizations that can effectively blend human creativity with AI automation capabilities.
            """
            
            state.workflow_data["generated_content"] = generated_content
            state.current_step = "generate_content"
            return state
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            raise
    
    async def _content_review_content(self, state: AgentState) -> AgentState:
        """Review and improve generated content"""
        try:
            content = state.workflow_data.get("generated_content", "")
            
            # Mock content review - in production would use AI for quality checks
            state.workflow_data["review_results"] = {
                "quality_score": 8.5,
                "suggestions": [
                    "Add more specific examples",
                    "Include relevant statistics",
                    "Strengthen the conclusion"
                ],
                "approved": True
            }
            
            state.current_step = "review_content"
            return state
            
        except Exception as e:
            logger.error(f"Content review failed: {e}")
            raise
    
    async def _content_finalize_content(self, state: AgentState) -> AgentState:
        """Finalize content for delivery"""
        try:
            content = state.workflow_data.get("generated_content", "")
            review = state.workflow_data.get("review_results", {})
            
            # Apply any final improvements
            final_content = content  # In production, would apply review suggestions
            
            state.workflow_data["final_content"] = final_content
            state.current_step = "finalize_content"
            
            # Add final response message
            state.messages.append(AIMessage(content=final_content))
            
            return state
            
        except Exception as e:
            logger.error(f"Content finalization failed: {e}")
            raise
    
    # Insights workflow node implementations  
    async def _insights_parse_query(self, state: AgentState) -> AgentState:
        """Parse data insights query"""
        try:
            query = state.messages[-1].content
            
            # Mock query parsing - in production would use NLP
            state.workflow_data["parsed_query"] = {
                "query_type": "trend_analysis",
                "metrics": ["revenue", "user_growth"],
                "time_period": "last_30_days",
                "filters": {}
            }
            
            state.current_step = "parse_query"
            return state
            
        except Exception as e:
            logger.error(f"Query parsing failed: {e}")
            raise
    
    async def _insights_fetch_data(self, state: AgentState) -> AgentState:
        """Fetch data for analysis"""
        try:
            query_info = state.workflow_data.get("parsed_query", {})
            
            # Mock data fetching - in production would query databases
            state.workflow_data["raw_data"] = {
                "revenue": [100000, 105000, 110000, 108000, 115000],
                "user_growth": [1000, 1200, 1150, 1300, 1400],
                "dates": ["2024-01-01", "2024-01-08", "2024-01-15", "2024-01-22", "2024-01-29"]
            }
            
            state.current_step = "fetch_data"
            return state
            
        except Exception as e:
            logger.error(f"Data fetching failed: {e}")
            raise
    
    async def _insights_analyze_data(self, state: AgentState) -> AgentState:
        """Analyze fetched data"""
        try:
            data = state.workflow_data.get("raw_data", {})
            
            # Mock data analysis - in production would use statistical analysis
            state.workflow_data["analysis_results"] = {
                "revenue_trend": "increasing",
                "revenue_growth_rate": 0.15,
                "user_growth_trend": "increasing", 
                "user_growth_rate": 0.40,
                "correlation": 0.85,
                "insights": [
                    "Revenue shows steady 15% growth",
                    "User growth accelerating at 40%",
                    "Strong correlation between users and revenue"
                ]
            }
            
            state.current_step = "analyze_data"
            return state
            
        except Exception as e:
            logger.error(f"Data analysis failed: {e}")
            raise
    
    async def _insights_generate_insights(self, state: AgentState) -> AgentState:
        """Generate business insights"""
        try:
            analysis = state.workflow_data.get("analysis_results", {})
            
            # Generate insights using AI
            insights_text = f"""
            ## Data Analysis Results
            
            Based on the last 30 days of data, here are the key insights:
            
            ### Revenue Performance
            - Revenue is trending {analysis.get('revenue_trend', 'stable')} with a {analysis.get('revenue_growth_rate', 0)*100:.1f}% growth rate
            - Current trajectory suggests strong business performance
            
            ### User Growth
            - User base is expanding at {analysis.get('user_growth_rate', 0)*100:.1f}% rate
            - Growth acceleration indicates successful acquisition strategies
            
            ### Key Insights
            {chr(10).join(f"- {insight}" for insight in analysis.get('insights', []))}
            
            ### Recommendations
            - Continue current growth strategies
            - Monitor user engagement metrics
            - Consider scaling infrastructure for continued growth
            """
            
            state.workflow_data["generated_insights"] = insights_text
            state.current_step = "generate_insights"
            return state
            
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            raise
    
    async def _insights_create_visualization(self, state: AgentState) -> AgentState:
        """Create data visualizations"""
        try:
            data = state.workflow_data.get("raw_data", {})
            
            # Mock visualization creation - in production would generate charts
            state.workflow_data["visualizations"] = {
                "charts": [
                    {
                        "type": "line_chart",
                        "title": "Revenue Trend",
                        "data": data.get("revenue", []),
                        "labels": data.get("dates", [])
                    },
                    {
                        "type": "bar_chart", 
                        "title": "User Growth",
                        "data": data.get("user_growth", []),
                        "labels": data.get("dates", [])
                    }
                ]
            }
            
            state.current_step = "create_visualization"
            return state
            
        except Exception as e:
            logger.error(f"Visualization creation failed: {e}")
            raise
    
    async def _insights_format_response(self, state: AgentState) -> AgentState:
        """Format final insights response"""
        try:
            insights = state.workflow_data.get("generated_insights", "")
            visualizations = state.workflow_data.get("visualizations", {})
            
            # Format complete response
            final_response = f"""
            {insights}
            
            ## Visualizations
            Generated {len(visualizations.get('charts', []))} charts to support the analysis.
            
            *Note: Charts would be displayed in the UI*
            """
            
            state.workflow_data["final_response"] = final_response
            state.current_step = "format_response"
            
            # Add final response message
            state.messages.append(AIMessage(content=final_response))
            
            return state
            
        except Exception as e:
            logger.error(f"Response formatting failed: {e}")
            raise
    
    async def get_agent_capabilities(self, agent_type: str) -> Dict[str, Any]:
        """Get capabilities for specific agent type"""
        try:
            agent_enum = AgentType(agent_type)
            routing_system = self.agent_routing[agent_enum]
            
            if routing_system == "agent_space":
                # Agent Space capabilities
                agent_config = self.config.get_agent_config(agent_type)
                return {
                    "agent_type": agent_type,
                    "system": "agent_space",
                    "capabilities": agent_config.get("tools", []),
                    "model": agent_config.get("model"),
                    "max_conversation_turns": agent_config.get("max_conversation_turns")
                }
            else:
                # LangGraph workflow capabilities
                workflows = {
                    "content": [
                        "content_creation",
                        "topic_research", 
                        "content_review",
                        "multi_format_output"
                    ],
                    "insights": [
                        "data_analysis",
                        "trend_identification",
                        "visualization_creation",
                        "business_recommendations"
                    ]
                }
                
                return {
                    "agent_type": agent_type,
                    "system": "langgraph",
                    "capabilities": workflows.get(agent_type, []),
                    "workflow_steps": 5 if agent_type == "content" else 6
                }
                
        except Exception as e:
            logger.error(f"Failed to get agent capabilities: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check orchestrator health"""
        try:
            # Check Agent Space manager
            agent_space_health = await self.agent_space_manager.health_check()
            
            # Check custom workflows
            workflows_healthy = (
                self._content_workflow is not None and 
                self._insights_workflow is not None
            )
            
            return {
                "status": "healthy" if agent_space_health["status"] == "healthy" and workflows_healthy else "unhealthy",
                "agent_space_status": agent_space_health["status"],
                "custom_workflows_loaded": workflows_healthy,
                "supported_agent_types": [agent.value for agent in AgentType],
                "routing_configuration": {agent.value: system for agent, system in self.agent_routing.items()},
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global instance
hybrid_agent_orchestrator = HybridAgentOrchestrator()