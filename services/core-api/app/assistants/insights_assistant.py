"""
Insights Assistant Implementation
Specialized assistant for data analysis, business intelligence, and proactive insights delivery
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..services.assistant_factory import BaseAssistant
from ..services.vertex_ai_service import vertex_ai_service
# Mock import for development  
# from ..services.hybrid_agent_orchestrator import hybrid_agent_orchestrator
hybrid_agent_orchestrator = None

logger = logging.getLogger(__name__)


class InsightsAssistant(BaseAssistant):
    """
    Insights Assistant
    
    Specialized for business analytics, data analysis,
    trend detection, and proactive insights delivery.
    """
    
    async def initialize(self, db: Session) -> Dict[str, Any]:
        """Initialize insights assistant with analytics integration"""
        self.capabilities = [
            "analytics", "technical", "general"
        ]
        
        self.system_prompt = """
You are an intelligent insights assistant specializing in data analysis and business intelligence. Your role is to:

1. Analyze business data and identify meaningful patterns and trends
2. Generate actionable insights from complex datasets
3. Create visualizations and dashboards to communicate findings
4. Provide proactive recommendations based on data analysis
5. Answer natural language queries about business metrics and performance
6. Detect anomalies and alert stakeholders to important changes

Always focus on providing clear, actionable insights that drive business decisions.
Use data-driven reasoning and explain your analytical methodology when presenting findings.
        """.strip()
        
        self.conversation_starters = [
            "Hi! I'm your insights assistant. I can help you analyze data, identify trends, and generate actionable business insights. What would you like to explore?",
            "Hello! I specialize in data analysis and business intelligence. Whether you need performance metrics, trend analysis, or custom reports, I'm here to help. What data are you curious about?",
            "Welcome! I'm here to turn your data into actionable insights. What business questions can I help you answer today?"
        ]
        
        self.escalation_triggers = [
            "complex statistical analysis requiring specialized expertise",
            "data privacy or compliance concerns with sensitive data",
            "large-scale data infrastructure or architecture questions",
            "strategic business decisions requiring executive input",
            "data quality issues affecting critical business processes"
        ]
        
        # Initialize analytics workflows
        try:
            await self._initialize_analytics_workflows(db)
        except Exception as e:
            logger.warning(f"Analytics workflow initialization failed: {e}")
        
        return {
            "type": "insights",
            "capabilities": self.capabilities,
            "tools_available": len(await self.get_available_tools(db)),
            "escalation_triggers": len(self.escalation_triggers),
            "analytics_integration": True
        }
    
    async def process_message(
        self,
        db: Session,
        message: str,
        conversation_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process insights message with analytics workflows"""
        try:
            # Analyze message for insights-specific patterns
            analysis = await self._analyze_insights_message(message)
            
            # Get data context
            data_context = await self._get_data_context(db, user_context, analysis)
            
            # Build enhanced context
            enhanced_context = {
                **conversation_context,
                "message_analysis": analysis,
                "data_context": data_context,
                "user_context": user_context or {},
                "assistant_type": "insights"
            }
            
            # Use custom analytics workflow for data analysis
            if analysis.get("category") in ["analysis", "trends", "metrics"]:
                response = await self._process_with_analytics_workflow(
                    db, message, enhanced_context
                )
            else:
                # Use Vertex AI for general insights tasks
                response = await self._process_with_vertex_ai(
                    db, message, enhanced_context
                )
            
            # Execute analytics actions if needed
            analytics_actions = []
            if analysis.get("requires_analytics_action", False):
                analytics_actions = await self._execute_analytics_actions(
                    db, analysis, response, user_context
                )
            
            return {
                "response": response["content"],
                "analysis": analysis,
                "data_context": data_context,
                "analytics_actions": analytics_actions,
                "escalation_recommended": analysis.get("complexity_score", 0) > 0.8,
                "metadata": {
                    "assistant_type": "insights",
                    "insights_category": analysis.get("category", "general"),
                    "data_sources": analysis.get("data_sources", []),
                    "visualization_suggested": analysis.get("visualization_type") is not None,
                    **response.get("metadata", {})
                }
            }
            
        except Exception as e:
            logger.error(f"Insights message processing failed: {e}")
            return {
                "response": "I'm having trouble processing your analytics request right now. Could you please provide more specific details about what data or insights you're looking for?",
                "error": str(e)
            }
    
    async def should_escalate(
        self,
        db: Session,
        conversation_context: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Determine if insights conversation should be escalated"""
        try:
            escalation_score = 0
            reasons = []
            
            # Check for complex statistical analysis requests
            recent_messages = conversation_context.get("recent_messages", [])
            complex_keywords = [
                "machine learning", "statistical significance", "regression analysis",
                "predictive modeling", "advanced analytics", "data science"
            ]
            
            for msg in recent_messages[-3:]:
                content = msg.get("content", "").lower()
                for keyword in complex_keywords:
                    if keyword in content:
                        escalation_score += 0.5
                        reasons.append(f"Complex analysis requested: {keyword}")
                        break
            
            # Check for data privacy concerns
            privacy_keywords = ["sensitive", "confidential", "privacy", "gdpr", "compliance", "personal data"]
            for msg in recent_messages[-3:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in privacy_keywords):
                    escalation_score += 0.6
                    reasons.append("Data privacy concerns detected")
                    break
            
            # Check for strategic business decisions
            strategic_keywords = ["strategy", "executive", "board", "investment", "budget", "critical decision"]
            for msg in recent_messages[-3:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in strategic_keywords):
                    escalation_score += 0.4
                    reasons.append("Strategic business decision context")
                    break
            
            # Check for data quality issues
            quality_keywords = ["data quality", "incorrect", "missing data", "inconsistent", "error"]
            for msg in recent_messages[-3:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in quality_keywords):
                    escalation_score += 0.3
                    reasons.append("Data quality issues reported")
                    break
            
            # Check for repeated failed analysis attempts
            failed_attempts = conversation_context.get("failed_analysis_attempts", 0)
            if failed_attempts > 2:
                escalation_score += 0.5
                reasons.append("Multiple failed analysis attempts")
            
            should_escalate = escalation_score >= 0.7
            
            return {
                "should_escalate": should_escalate,
                "escalation_score": escalation_score,
                "reasons": reasons
            }
            
        except Exception as e:
            logger.error(f"Insights escalation check failed: {e}")
            return {"should_escalate": False, "error": str(e)}
    
    async def _initialize_analytics_workflows(self, db: Session):
        """Initialize custom analytics workflows"""
        try:
            # Define analytics workflow
            analytics_workflow = {
                "workflow_id": f"analytics_engine_{self.assistant_id}",
                "workflow_type": "analytics_processing",
                "steps": [
                    {
                        "step_id": "query_parsing",
                        "type": "nlp_analysis",
                        "description": "Parse natural language query into analytical requirements"
                    },
                    {
                        "step_id": "data_retrieval",
                        "type": "data_access",
                        "description": "Retrieve relevant data from connected sources"
                    },
                    {
                        "step_id": "data_analysis",
                        "type": "computation",
                        "description": "Perform statistical analysis and calculations"
                    },
                    {
                        "step_id": "trend_detection",
                        "type": "pattern_analysis",
                        "description": "Identify trends, patterns, and anomalies"
                    },
                    {
                        "step_id": "insight_generation",
                        "type": "interpretation",
                        "description": "Generate actionable insights and recommendations"
                    },
                    {
                        "step_id": "visualization_creation",
                        "type": "visualization",
                        "description": "Create charts and visualizations"
                    }
                ],
                "tools": [
                    "bigquery_connector",
                    "statistical_analyzer",
                    "trend_detector",
                    "visualization_generator",
                    "insight_synthesizer"
                ]
            }
            
            # Register workflow with hybrid orchestrator (mock for development)
            if hybrid_agent_orchestrator:
                await hybrid_agent_orchestrator.register_workflow(
                    db=db,
                    workflow_config=analytics_workflow
                )
            else:
                logger.info("Mock workflow registration for analytics processing")
            
            logger.info(f"Analytics workflows initialized for assistant: {self.assistant_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize analytics workflows: {e}")
            raise
    
    async def _analyze_insights_message(self, message: str) -> Dict[str, Any]:
        """Analyze message for insights-specific patterns"""
        try:
            message_lower = message.lower()
            
            # Categorize insights request
            categories = {
                "analysis": [
                    "analyze", "analysis", "examine", "investigate", "study",
                    "breakdown", "deep dive", "explore"
                ],
                "trends": [
                    "trend", "pattern", "change", "growth", "decline",
                    "over time", "historical", "forecast", "predict"
                ],
                "metrics": [
                    "metrics", "kpi", "performance", "measure", "benchmark",
                    "compare", "comparison", "dashboard"
                ],
                "reporting": [
                    "report", "summary", "overview", "status", "update",
                    "executive summary", "brief"
                ],
                "anomalies": [
                    "anomaly", "unusual", "outlier", "spike", "drop",
                    "unexpected", "abnormal", "alert"
                ]
            }
            
            category = "general"
            confidence = 0.5
            
            for cat, keywords in categories.items():
                matches = sum(1 for keyword in keywords if keyword in message_lower)
                if matches > 0:
                    category = cat
                    confidence = min(0.9, 0.6 + (matches * 0.1))
                    break
            
            # Extract query details
            query_details = self._extract_query_details(message)
            
            # Identify data sources
            data_source_keywords = {
                "sales": ["sales", "revenue", "orders", "customers", "transactions"],
                "marketing": ["marketing", "campaigns", "leads", "conversions", "traffic"],
                "operations": ["operations", "performance", "efficiency", "costs"],
                "finance": ["finance", "profit", "expenses", "budget", "cash flow"],
                "users": ["users", "engagement", "retention", "churn", "activity"]
            }
            
            data_sources = []
            for source, keywords in data_source_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    data_sources.append(source)
            
            # Determine visualization type
            visualization_keywords = {
                "chart": ["chart", "graph", "plot"],
                "dashboard": ["dashboard", "overview", "summary"],
                "table": ["table", "list", "breakdown"],
                "map": ["map", "geographic", "location"],
                "timeline": ["timeline", "over time", "historical"]
            }
            
            visualization_type = None
            for viz_type, keywords in visualization_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    visualization_type = viz_type
                    break
            
            # Assess complexity
            complexity_indicators = [
                "complex", "advanced", "statistical", "machine learning",
                "predictive", "correlation", "regression", "segmentation"
            ]
            
            complexity_score = sum(1 for indicator in complexity_indicators if indicator in message_lower)
            complexity = "high" if complexity_score >= 2 else "medium" if complexity_score >= 1 else "low"
            
            return {
                "category": category,
                "confidence": confidence,
                "complexity": complexity,
                "complexity_score": complexity_score / len(complexity_indicators),
                "query_details": query_details,
                "data_sources": data_sources,
                "visualization_type": visualization_type,
                "requires_analytics_action": category in ["analysis", "trends", "metrics", "anomalies"]
            }
            
        except Exception as e:
            logger.error(f"Insights message analysis failed: {e}")
            return {
                "category": "general",
                "confidence": 0.5,
                "complexity": "medium",
                "complexity_score": 0.5,
                "query_details": {},
                "data_sources": [],
                "visualization_type": None,
                "requires_analytics_action": False
            }
    
    def _extract_query_details(self, message: str) -> Dict[str, Any]:
        """Extract analytical query details from message"""
        import re
        
        details = {}
        
        # Extract time periods
        time_patterns = [
            r'\b(?:last|past)\s+(\d+)\s+(day|week|month|year)s?\b',
            r'\b(?:this|current)\s+(day|week|month|year|quarter)\b',
            r'\b(\d{4})\b',  # Year
            r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b'
        ]
        
        time_periods = []
        for pattern in time_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            time_periods.extend(matches)
        
        if time_periods:
            details["time_periods"] = time_periods
        
        # Extract metrics
        metric_keywords = [
            "revenue", "sales", "profit", "cost", "users", "customers",
            "conversion", "retention", "churn", "engagement", "traffic",
            "orders", "transactions", "leads", "roi", "ctr", "cpc"
        ]
        
        metrics = [metric for metric in metric_keywords if metric in message.lower()]
        if metrics:
            details["metrics"] = metrics
        
        # Extract comparison terms
        comparison_keywords = ["vs", "versus", "compared to", "against", "than"]
        has_comparison = any(keyword in message.lower() for keyword in comparison_keywords)
        if has_comparison:
            details["comparison"] = True
        
        # Extract aggregation types
        aggregation_keywords = {
            "sum": ["total", "sum", "aggregate"],
            "average": ["average", "mean", "avg"],
            "count": ["count", "number of", "how many"],
            "max": ["maximum", "max", "highest", "peak"],
            "min": ["minimum", "min", "lowest", "bottom"]
        }
        
        for agg_type, keywords in aggregation_keywords.items():
            if any(keyword in message.lower() for keyword in keywords):
                details["aggregation"] = agg_type
                break
        
        # Extract filters/segments
        filter_patterns = [
            r'(?:where|filter|only|just)\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|!|\?)',
            r'(?:segment|group)\s+by\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|!|\?)'
        ]
        
        filters = []
        for pattern in filter_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            filters.extend([f.strip() for f in matches])
        
        if filters:
            details["filters"] = filters
        
        return details
    
    async def _get_data_context(
        self,
        db: Session,
        user_context: Optional[Dict[str, Any]],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get data context for analytics processing"""
        try:
            # Mock data context - in real implementation would query actual data sources
            context = {
                "available_data_sources": [
                    {
                        "name": "sales_data",
                        "type": "bigquery",
                        "tables": ["orders", "customers", "products"],
                        "last_updated": datetime.now().isoformat()
                    },
                    {
                        "name": "marketing_data",
                        "type": "analytics",
                        "metrics": ["sessions", "conversions", "traffic"],
                        "last_updated": datetime.now().isoformat()
                    },
                    {
                        "name": "user_engagement",
                        "type": "database",
                        "tables": ["user_events", "sessions", "features"],
                        "last_updated": datetime.now().isoformat()
                    }
                ],
                "data_freshness": {
                    "sales": "real-time",
                    "marketing": "hourly",
                    "users": "real-time"
                },
                "available_metrics": {
                    "sales": ["revenue", "orders", "avg_order_value", "customers"],
                    "marketing": ["traffic", "conversions", "cost_per_click", "roi"],
                    "users": ["active_users", "retention", "engagement", "churn"]
                },
                "time_ranges": {
                    "min_date": "2023-01-01",
                    "max_date": datetime.now().date().isoformat(),
                    "granularity": ["hour", "day", "week", "month", "quarter", "year"]
                }
            }
            
            # Filter context based on requested data sources
            requested_sources = analysis.get("data_sources", [])
            if requested_sources:
                context["relevant_sources"] = [
                    source for source in context["available_data_sources"]
                    if any(req_source in source["name"] for req_source in requested_sources)
                ]
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get data context: {e}")
            return {}
    
    async def _process_with_analytics_workflow(
        self,
        db: Session,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process message using custom analytics workflow"""
        try:
            # Use hybrid orchestrator for analytics workflow (mock for development)
            if hybrid_agent_orchestrator:
                workflow_response = await hybrid_agent_orchestrator.execute_workflow(
                    db=db,
                    workflow_id=f"analytics_engine_{self.assistant_id}",
                    input_data={
                        "query": message,
                        "context": context,
                        "data_context": context.get("data_context", {}),
                        "analysis": context.get("message_analysis", {})
                    }
                )
            else:
                # Mock workflow response
                workflow_response = {
                    "insights": f"Based on your query '{message}', here are the key insights: The data shows positive trends with a 15% increase over the last month. This is a mock analysis that would be generated by our advanced analytics engine.",
                    "metadata": {"mock": True, "workflow": "analytics_processing"}
                }
            
            return {
                "content": workflow_response.get("insights", "I've analyzed your data request using our analytics engine."),
                "metadata": {
                    "source": "analytics_workflow",
                    "workflow_id": f"analytics_engine_{self.assistant_id}",
                    "data_processed": workflow_response.get("data_processed", False),
                    "visualizations": workflow_response.get("visualizations", []),
                    **workflow_response.get("metadata", {})
                }
            }
            
        except Exception as e:
            logger.error(f"Analytics workflow processing failed: {e}")
            # Fallback to Vertex AI
            return await self._process_with_vertex_ai(db, message, context)
    
    async def _process_with_vertex_ai(
        self,
        db: Session,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process message using Vertex AI for general insights tasks"""
        try:
            # Build enhanced system prompt with data context
            data_context = context.get("data_context", {})
            enhanced_prompt = self.system_prompt
            
            if data_context:
                data_info = f"""

Data Context:
- Available Sources: {', '.join([source['name'] for source in data_context.get('available_data_sources', [])])}
- Data Freshness: {data_context.get('data_freshness', {})}
- Time Range: {data_context.get('time_ranges', {}).get('min_date')} to {data_context.get('time_ranges', {}).get('max_date')}
                """
                enhanced_prompt += data_info
            
            system_prompt = self._build_system_prompt(
                enhanced_prompt,
                {
                    "organization_name": self.config.get("organization_name"),
                    "available_tools": await self.get_available_tools(db)
                }
            )
            
            response = await vertex_ai_service.generate_response(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                model="gemini-1.5-pro",
                temperature=0.3,  # Lower temperature for analytical accuracy
                max_tokens=1500
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Vertex AI processing failed: {e}")
            return {
                "content": "I'm having trouble analyzing your data request right now. Please try again or provide more specific details about what insights you're looking for.",
                "metadata": {"error": str(e)}
            }
    
    async def _execute_analytics_actions(
        self,
        db: Session,
        analysis: Dict[str, Any],
        response: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute analytics actions based on analysis and response"""
        try:
            actions = []
            query_details = analysis.get("query_details", {})
            data_sources = analysis.get("data_sources", [])
            
            # Data query action
            if analysis.get("category") in ["analysis", "metrics"]:
                action = {
                    "type": "execute_query",
                    "details": {
                        "data_sources": data_sources,
                        "metrics": query_details.get("metrics", []),
                        "time_periods": query_details.get("time_periods", []),
                        "filters": query_details.get("filters", []),
                        "aggregation": query_details.get("aggregation", "sum")
                    },
                    "status": "ready"
                }
                actions.append(action)
            
            # Visualization creation action
            if analysis.get("visualization_type"):
                action = {
                    "type": "create_visualization",
                    "details": {
                        "visualization_type": analysis["visualization_type"],
                        "data_sources": data_sources,
                        "metrics": query_details.get("metrics", []),
                        "dimensions": query_details.get("filters", [])
                    },
                    "status": "pending"
                }
                actions.append(action)
            
            # Trend detection action
            if analysis.get("category") == "trends":
                action = {
                    "type": "detect_trends",
                    "details": {
                        "data_sources": data_sources,
                        "metrics": query_details.get("metrics", []),
                        "time_periods": query_details.get("time_periods", []),
                        "trend_type": "growth_analysis"
                    },
                    "status": "ready"
                }
                actions.append(action)
            
            # Anomaly detection action
            if analysis.get("category") == "anomalies":
                action = {
                    "type": "detect_anomalies",
                    "details": {
                        "data_sources": data_sources,
                        "metrics": query_details.get("metrics", []),
                        "sensitivity": "medium",
                        "alert_threshold": 2.0  # Standard deviations
                    },
                    "status": "ready"
                }
                actions.append(action)
            
            return actions
            
        except Exception as e:
            logger.error(f"Analytics action execution failed: {e}")
            return []


# Add InsightsAssistant to the factory
def register_insights_assistant():
    """Register InsightsAssistant with the factory"""
    from ..services.assistant_factory import assistant_factory
    assistant_factory.assistant_types["insights"] = InsightsAssistant