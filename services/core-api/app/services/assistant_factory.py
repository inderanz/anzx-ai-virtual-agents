"""
AI Assistant Factory
Creates and manages specialized assistant types with domain-specific capabilities
"""

import logging
from typing import Dict, Any, List, Optional, Type
from abc import ABC, abstractmethod
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.user import Assistant, Organization, User
from ..services.mcp_tool_registry import mcp_tool_registry
from ..config.assistant_config import ASSISTANT_TEMPLATES, ASSISTANT_CAPABILITIES

logger = logging.getLogger(__name__)


class BaseAssistant(ABC):
    """
    Base class for specialized AI assistants
    
    Defines common interface and functionality for all assistant types
    """
    
    def __init__(self, assistant_id: str, config: Dict[str, Any]):
        logger.info(f"Creating BaseAssistant with ID: {assistant_id}, config: {config}")
        self.assistant_id = assistant_id
        self.config = config
        self.type = self.__class__.__name__.lower().replace('assistant', '')
        self.capabilities = []
        self.tools = []
        self.system_prompt = ""
        self.conversation_starters = []
        self.escalation_triggers = []
        
    @abstractmethod
    async def initialize(self, db: Session) -> Dict[str, Any]:
        """Initialize the assistant with specific capabilities"""
        pass
    
    @abstractmethod
    async def process_message(
        self,
        db: Session,
        message: str,
        conversation_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process incoming message with assistant-specific logic"""
        pass
    
    @abstractmethod
    async def should_escalate(
        self,
        db: Session,
        conversation_context: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Determine if conversation should be escalated"""
        pass
    
    async def get_available_tools(self, db: Session) -> List[Dict[str, Any]]:
        """Get tools available to this assistant type"""
        try:
            # Get organization-specific tools
            tools = await mcp_tool_registry.get_available_tools(
                db=db,
                organization_id=self.config.get("organization_id"),
                category=None
            )
            
            # Filter tools based on assistant capabilities
            filtered_tools = []
            for tool in tools:
                if self._is_tool_allowed(tool):
                    filtered_tools.append(tool)
            
            return filtered_tools
            
        except Exception as e:
            logger.error(f"Failed to get available tools: {e}")
            return []
    
    def _is_tool_allowed(self, tool: Dict[str, Any]) -> bool:
        """Check if tool is allowed for this assistant type"""
        tool_category = tool.get("category", "general")
        return tool_category in self.capabilities or "general" in self.capabilities
    
    async def _execute_tool(
        self,
        db: Session,
        tool_id: str,
        parameters: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a tool with proper error handling"""
        try:
            result = await mcp_tool_registry.execute_tool(
                db=db,
                tool_id=tool_id,
                organization_id=self.config.get("organization_id"),
                input_parameters=parameters,
                user_id=None,  # System execution
                conversation_id=conversation_id
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _build_system_prompt(self, base_prompt: str, context: Dict[str, Any]) -> str:
        """Build system prompt with context"""
        prompt_parts = [base_prompt]
        
        # Add organization context
        if "organization_name" in context:
            prompt_parts.append(f"You are representing {context['organization_name']}.")
        
        # Add available tools context
        if "available_tools" in context and context["available_tools"]:
            tools_list = ", ".join([tool["name"] for tool in context["available_tools"]])
            prompt_parts.append(f"You have access to these tools: {tools_list}")
        
        # Add escalation context
        if self.escalation_triggers:
            triggers_text = ", ".join(self.escalation_triggers)
            prompt_parts.append(f"Escalate to human if: {triggers_text}")
        
        return "\n\n".join(prompt_parts)


class SupportAssistant(BaseAssistant):
    """
    Customer Support Assistant
    
    Specialized for handling customer inquiries, troubleshooting,
    and providing technical support with escalation capabilities.
    """
    
    async def initialize(self, db: Session) -> Dict[str, Any]:
        """Initialize support assistant"""
        self.capabilities = [
            "communication", "technical", "billing", "general"
        ]
        
        self.system_prompt = """
You are a helpful customer support assistant. Your role is to:

1. Assist customers with their inquiries and problems
2. Provide clear, step-by-step troubleshooting guidance
3. Access customer account information when needed
4. Escalate complex issues to human agents when appropriate
5. Maintain a friendly, professional, and empathetic tone

Always prioritize customer satisfaction and aim to resolve issues efficiently.
If you cannot resolve an issue, explain what you've tried and why escalation is needed.
        """.strip()
        
        self.conversation_starters = [
            "Hi! I'm here to help with any questions or issues you might have. What can I assist you with today?",
            "Welcome! How can I help resolve your inquiry today?",
            "Hello! I'm your support assistant. What brings you here today?"
        ]
        
        self.escalation_triggers = [
            "customer requests human agent",
            "billing dispute or refund request",
            "technical issue beyond troubleshooting steps",
            "customer expresses high frustration",
            "security or privacy concern",
            "legal or compliance matter"
        ]
        
        return {
            "type": "support",
            "capabilities": self.capabilities,
            "tools_available": len(await self.get_available_tools(db)),
            "escalation_triggers": len(self.escalation_triggers)
        }
    
    async def process_message(
        self,
        db: Session,
        message: str,
        conversation_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process support message with specialized logic"""
        try:
            # Analyze message for support-specific patterns
            analysis = await self._analyze_support_message(message)
            
            # Check if tools are needed
            tool_suggestions = await self._suggest_tools(db, message, analysis)
            
            # Build enhanced context
            enhanced_context = {
                **conversation_context,
                "message_analysis": analysis,
                "suggested_tools": tool_suggestions,
                "user_context": user_context or {},
                "assistant_type": "support"
            }
            
            # Generate response using Vertex AI
            system_prompt = self._build_system_prompt(
                self.system_prompt,
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
                temperature=0.7,
                max_tokens=1000
            )
            
            # Execute suggested tools if appropriate
            tool_results = []
            if tool_suggestions and analysis.get("requires_tools", False):
                for tool_suggestion in tool_suggestions[:2]:  # Limit to 2 tools
                    tool_result = await self._execute_tool(
                        db=db,
                        tool_id=tool_suggestion["tool_id"],
                        parameters=tool_suggestion["parameters"],
                        conversation_id=conversation_context.get("conversation_id")
                    )
                    tool_results.append(tool_result)
            
            return {
                "response": response["content"],
                "analysis": analysis,
                "tool_results": tool_results,
                "escalation_recommended": analysis.get("escalation_score", 0) > 0.7,
                "metadata": {
                    "assistant_type": "support",
                    "confidence": analysis.get("confidence", 0.8),
                    "category": analysis.get("category", "general"),
                    **response.get("metadata", {})
                }
            }
            
        except Exception as e:
            logger.error(f"Support message processing failed: {e}")
            return {
                "response": "I apologize, but I'm having trouble processing your request right now. Let me connect you with a human agent who can better assist you.",
                "escalation_recommended": True,
                "error": str(e)
            }
    
    async def should_escalate(
        self,
        db: Session,
        conversation_context: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Determine if support conversation should be escalated"""
        try:
            escalation_score = 0
            reasons = []
            
            # Check message count
            message_count = conversation_context.get("message_count", 0)
            if message_count > 10:
                escalation_score += 0.3
                reasons.append("Long conversation without resolution")
            
            # Check for escalation keywords in recent messages
            recent_messages = conversation_context.get("recent_messages", [])
            escalation_keywords = [
                "human", "agent", "manager", "supervisor", "escalate",
                "frustrated", "angry", "disappointed", "terrible",
                "refund", "cancel", "complaint", "legal"
            ]
            
            for msg in recent_messages[-3:]:  # Check last 3 messages
                content = msg.get("content", "").lower()
                for keyword in escalation_keywords:
                    if keyword in content:
                        escalation_score += 0.4
                        reasons.append(f"Customer mentioned: {keyword}")
                        break
            
            # Check for unresolved technical issues
            if conversation_context.get("category") == "technical":
                failed_attempts = conversation_context.get("failed_troubleshooting_attempts", 0)
                if failed_attempts > 2:
                    escalation_score += 0.5
                    reasons.append("Multiple failed troubleshooting attempts")
            
            should_escalate = escalation_score >= 0.7
            
            return {
                "should_escalate": should_escalate,
                "escalation_score": escalation_score,
                "reasons": reasons
            }
            
        except Exception as e:
            logger.error(f"Escalation check failed: {e}")
            return {"should_escalate": False, "error": str(e)}
    
    async def _analyze_support_message(self, message: str) -> Dict[str, Any]:
        """Analyze message for support-specific patterns"""
        try:
            message_lower = message.lower()
            
            # Categorize the inquiry
            categories = {
                "technical": ["error", "bug", "not working", "broken", "issue", "problem"],
                "billing": ["bill", "charge", "payment", "invoice", "subscription", "refund"],
                "account": ["login", "password", "account", "profile", "settings"],
                "general": ["help", "question", "how to", "information"]
            }
            
            category = "general"
            confidence = 0.5
            
            for cat, keywords in categories.items():
                matches = sum(1 for keyword in keywords if keyword in message_lower)
                if matches > 0:
                    category = cat
                    confidence = min(0.9, 0.5 + (matches * 0.1))
                    break
            
            # Check urgency indicators
            urgency_keywords = ["urgent", "asap", "immediately", "critical", "emergency"]
            urgency = "normal"
            if any(keyword in message_lower for keyword in urgency_keywords):
                urgency = "high"
            
            # Check sentiment
            negative_keywords = ["frustrated", "angry", "terrible", "awful", "hate"]
            positive_keywords = ["great", "excellent", "love", "perfect", "amazing"]
            
            sentiment = "neutral"
            if any(keyword in message_lower for keyword in negative_keywords):
                sentiment = "negative"
            elif any(keyword in message_lower for keyword in positive_keywords):
                sentiment = "positive"
            
            # Escalation score
            escalation_score = 0
            if sentiment == "negative":
                escalation_score += 0.3
            if urgency == "high":
                escalation_score += 0.2
            if "human" in message_lower or "agent" in message_lower:
                escalation_score += 0.5
            
            return {
                "category": category,
                "confidence": confidence,
                "urgency": urgency,
                "sentiment": sentiment,
                "escalation_score": escalation_score,
                "requires_tools": category in ["billing", "account", "technical"]
            }
            
        except Exception as e:
            logger.error(f"Message analysis failed: {e}")
            return {
                "category": "general",
                "confidence": 0.5,
                "urgency": "normal",
                "sentiment": "neutral",
                "escalation_score": 0,
                "requires_tools": False
            }
    
    async def _suggest_tools(self, db: Session, message: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest tools based on message analysis"""
        try:
            suggestions = []
            category = analysis.get("category", "general")
            
            # Get available tools
            available_tools = await self.get_available_tools(db)
            
            # Suggest tools based on category
            if category == "billing":
                billing_tools = [t for t in available_tools if "billing" in t.get("name", "").lower() or "stripe" in t.get("name", "").lower()]
                for tool in billing_tools[:2]:
                    suggestions.append({
                        "tool_id": tool["tool_id"],
                        "tool_name": tool["name"],
                        "parameters": self._extract_billing_parameters(message),
                        "reason": "Billing inquiry detected"
                    })
            
            elif category == "account":
                account_tools = [t for t in available_tools if "account" in t.get("name", "").lower() or "user" in t.get("name", "").lower()]
                for tool in account_tools[:2]:
                    suggestions.append({
                        "tool_id": tool["tool_id"],
                        "tool_name": tool["name"],
                        "parameters": self._extract_account_parameters(message),
                        "reason": "Account-related inquiry detected"
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Tool suggestion failed: {e}")
            return []
    
    def _extract_billing_parameters(self, message: str) -> Dict[str, Any]:
        """Extract billing-related parameters from message"""
        import re
        
        parameters = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, message)
        if emails:
            parameters["customer_email"] = emails[0]
        
        # Extract invoice/order numbers
        order_pattern = r'\b(?:order|invoice|ref|reference)[\s#:]*([A-Z0-9]{6,})\b'
        orders = re.findall(order_pattern, message, re.IGNORECASE)
        if orders:
            parameters["order_id"] = orders[0]
        
        return parameters
    
    def _extract_account_parameters(self, message: str) -> Dict[str, Any]:
        """Extract account-related parameters from message"""
        import re
        
        parameters = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, message)
        if emails:
            parameters["email"] = emails[0]
        
        return parameters


class SalesAssistant(BaseAssistant):
    """
    Sales Assistant
    
    Specialized for lead qualification, product recommendations,
    pricing inquiries, and sales process automation.
    """
    
    async def initialize(self, db: Session) -> Dict[str, Any]:
        """Initialize sales assistant"""
        self.capabilities = [
            "communication", "analytics", "finance", "general"
        ]
        
        self.system_prompt = """
You are a knowledgeable sales assistant. Your role is to:

1. Qualify leads and understand customer needs
2. Provide product information and recommendations
3. Handle pricing inquiries and create quotes
4. Guide customers through the sales process
5. Schedule demos and meetings with sales team
6. Maintain a consultative, helpful, and professional approach

Focus on understanding customer requirements and providing value.
Always aim to move qualified prospects toward a purchase decision.
        """.strip()
        
        self.conversation_starters = [
            "Hello! I'm here to help you find the perfect solution for your needs. What brings you here today?",
            "Hi! I'd love to learn more about your requirements and show you how we can help. What's your main challenge?",
            "Welcome! I'm your sales assistant. What would you like to know about our products and services?"
        ]
        
        self.escalation_triggers = [
            "customer requests custom pricing",
            "enterprise or large-scale deployment",
            "complex integration requirements",
            "customer wants to speak with sales manager",
            "contract negotiation needed"
        ]
        
        return {
            "type": "sales",
            "capabilities": self.capabilities,
            "tools_available": len(await self.get_available_tools(db)),
            "escalation_triggers": len(self.escalation_triggers)
        }
    
    async def process_message(
        self,
        db: Session,
        message: str,
        conversation_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process sales message with lead qualification logic"""
        try:
            # Analyze message for sales-specific patterns
            analysis = await self._analyze_sales_message(message)
            
            # Update lead qualification score
            lead_score = await self._calculate_lead_score(conversation_context, analysis)
            
            # Build enhanced context
            enhanced_context = {
                **conversation_context,
                "message_analysis": analysis,
                "lead_score": lead_score,
                "user_context": user_context or {},
                "assistant_type": "sales"
            }
            
            # Generate response
            system_prompt = self._build_system_prompt(
                self.system_prompt,
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
                temperature=0.8,
                max_tokens=1000
            )
            
            return {
                "response": response["content"],
                "analysis": analysis,
                "lead_score": lead_score,
                "escalation_recommended": lead_score.get("score", 0) > 80,
                "metadata": {
                    "assistant_type": "sales",
                    "lead_qualification": lead_score.get("qualification", "unknown"),
                    "sales_stage": analysis.get("sales_stage", "awareness"),
                    **response.get("metadata", {})
                }
            }
            
        except Exception as e:
            logger.error(f"Sales message processing failed: {e}")
            return {
                "response": "I'd be happy to help you learn more about our solutions. Could you tell me a bit about what you're looking for?",
                "error": str(e)
            }
    
    async def should_escalate(
        self,
        db: Session,
        conversation_context: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Determine if sales conversation should be escalated"""
        try:
            escalation_score = 0
            reasons = []
            
            # Check lead score
            lead_score = conversation_context.get("lead_score", {}).get("score", 0)
            if lead_score > 80:
                escalation_score += 0.6
                reasons.append("High-quality lead identified")
            
            # Check for enterprise indicators
            recent_messages = conversation_context.get("recent_messages", [])
            enterprise_keywords = [
                "enterprise", "team", "organization", "company", "employees",
                "custom", "integration", "api", "sso", "compliance"
            ]
            
            for msg in recent_messages[-3:]:
                content = msg.get("content", "").lower()
                for keyword in enterprise_keywords:
                    if keyword in content:
                        escalation_score += 0.3
                        reasons.append(f"Enterprise indicator: {keyword}")
                        break
            
            # Check for pricing/contract discussions
            pricing_keywords = ["price", "cost", "contract", "negotiate", "discount"]
            for msg in recent_messages[-3:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in pricing_keywords):
                    escalation_score += 0.4
                    reasons.append("Pricing discussion detected")
                    break
            
            should_escalate = escalation_score >= 0.7
            
            return {
                "should_escalate": should_escalate,
                "escalation_score": escalation_score,
                "reasons": reasons
            }
            
        except Exception as e:
            logger.error(f"Sales escalation check failed: {e}")
            return {"should_escalate": False, "error": str(e)}
    
    async def _analyze_sales_message(self, message: str) -> Dict[str, Any]:
        """Analyze message for sales-specific patterns"""
        try:
            message_lower = message.lower()
            
            # Determine sales stage
            stage_keywords = {
                "awareness": ["learn", "information", "what is", "tell me about"],
                "interest": ["interested", "features", "benefits", "how does"],
                "consideration": ["compare", "vs", "alternatives", "evaluation"],
                "intent": ["price", "cost", "buy", "purchase", "demo", "trial"],
                "decision": ["contract", "agreement", "sign up", "get started"]
            }
            
            sales_stage = "awareness"
            for stage, keywords in stage_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    sales_stage = stage
                    break
            
            # Detect buying signals
            buying_signals = [
                "budget", "timeline", "decision maker", "approval", "when",
                "implementation", "rollout", "team size", "requirements"
            ]
            
            signals_detected = [signal for signal in buying_signals if signal in message_lower]
            
            # Detect company size indicators
            company_size = "unknown"
            if any(word in message_lower for word in ["startup", "small business"]):
                company_size = "small"
            elif any(word in message_lower for word in ["medium", "growing", "scale"]):
                company_size = "medium"
            elif any(word in message_lower for word in ["enterprise", "large", "corporation"]):
                company_size = "large"
            
            return {
                "sales_stage": sales_stage,
                "buying_signals": signals_detected,
                "company_size": company_size,
                "intent_level": len(signals_detected),
                "qualification_data": self._extract_qualification_data(message)
            }
            
        except Exception as e:
            logger.error(f"Sales message analysis failed: {e}")
            return {
                "sales_stage": "awareness",
                "buying_signals": [],
                "company_size": "unknown",
                "intent_level": 0,
                "qualification_data": {}
            }
    
    def _extract_qualification_data(self, message: str) -> Dict[str, Any]:
        """Extract lead qualification data from message"""
        import re
        
        data = {}
        
        # Extract company name
        company_patterns = [
            r'(?:at|from|with)\s+([A-Z][a-zA-Z\s&]+(?:Inc|LLC|Corp|Ltd|Company))',
            r'(?:company|organization)\s+(?:is|called)\s+([A-Z][a-zA-Z\s&]+)'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, message)
            if matches:
                data["company"] = matches[0].strip()
                break
        
        # Extract team size
        size_patterns = [
            r'(\d+)\s+(?:people|employees|team members|users)',
            r'team\s+of\s+(\d+)',
            r'(\d+)\s+person\s+team'
        ]
        
        for pattern in size_patterns:
            matches = re.findall(pattern, message)
            if matches:
                data["team_size"] = int(matches[0])
                break
        
        # Extract budget indicators
        budget_keywords = ["budget", "spend", "investment", "cost"]
        if any(keyword in message.lower() for keyword in budget_keywords):
            data["budget_mentioned"] = True
        
        return data
    
    async def _calculate_lead_score(self, conversation_context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate lead qualification score"""
        try:
            score = 0
            factors = []
            
            # Sales stage scoring
            stage_scores = {
                "awareness": 10,
                "interest": 25,
                "consideration": 50,
                "intent": 75,
                "decision": 90
            }
            
            stage = analysis.get("sales_stage", "awareness")
            stage_score = stage_scores.get(stage, 10)
            score += stage_score
            factors.append(f"Sales stage: {stage} (+{stage_score})")
            
            # Buying signals scoring
            intent_level = analysis.get("intent_level", 0)
            score += intent_level * 5
            factors.append(f"Buying signals: {intent_level} (+{intent_level * 5})")
            
            # Company size scoring
            size_scores = {"small": 5, "medium": 15, "large": 25}
            company_size = analysis.get("company_size", "unknown")
            if company_size in size_scores:
                size_score = size_scores[company_size]
                score += size_score
                factors.append(f"Company size: {company_size} (+{size_score})")
            
            # Qualification data scoring
            qual_data = analysis.get("qualification_data", {})
            if qual_data.get("company"):
                score += 10
                factors.append("Company identified (+10)")
            if qual_data.get("team_size"):
                score += 15
                factors.append("Team size provided (+15)")
            if qual_data.get("budget_mentioned"):
                score += 20
                factors.append("Budget mentioned (+20)")
            
            # Determine qualification level
            if score >= 80:
                qualification = "hot"
            elif score >= 60:
                qualification = "warm"
            elif score >= 30:
                qualification = "qualified"
            else:
                qualification = "cold"
            
            return {
                "score": min(100, score),  # Cap at 100
                "qualification": qualification,
                "factors": factors
            }
            
        except Exception as e:
            logger.error(f"Lead score calculation failed: {e}")
            return {"score": 0, "qualification": "unknown", "factors": []}


class TechnicalAssistant(BaseAssistant):
    """
    Technical Assistant
    
    Specialized for technical support, API documentation,
    integration guidance, and developer assistance.
    """
    
    async def initialize(self, db: Session) -> Dict[str, Any]:
        """Initialize technical assistant"""
        self.capabilities = [
            "technical", "development", "analytics", "general"
        ]
        
        self.system_prompt = """
You are a technical assistant specializing in developer support. Your role is to:

1. Provide technical documentation and API guidance
2. Help with integration and implementation questions
3. Troubleshoot technical issues and errors
4. Explain complex technical concepts clearly
5. Guide developers through best practices
6. Escalate to engineering team when needed

Focus on providing accurate, actionable technical guidance.
Always include code examples and step-by-step instructions when helpful.
        """.strip()
        
        self.conversation_starters = [
            "Hi! I'm here to help with technical questions and integration support. What can I assist you with?",
            "Hello! I'm your technical assistant. Are you working on an integration or have a technical question?",
            "Welcome! I specialize in technical support and developer guidance. How can I help you today?"
        ]
        
        self.escalation_triggers = [
            "bug report or system issue",
            "feature request or enhancement",
            "complex integration requirements",
            "performance or scaling concerns",
            "security vulnerability report"
        ]
        
        return {
            "type": "technical",
            "capabilities": self.capabilities,
            "tools_available": len(await self.get_available_tools(db)),
            "escalation_triggers": len(self.escalation_triggers)
        }
    
    async def process_message(
        self,
        db: Session,
        message: str,
        conversation_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process technical message with specialized logic"""
        try:
            # Analyze message for technical patterns
            analysis = await self._analyze_technical_message(message)
            
            # Get relevant tools
            tool_suggestions = await self._suggest_technical_tools(db, message, analysis)
            
            # Build enhanced context
            enhanced_context = {
                **conversation_context,
                "message_analysis": analysis,
                "suggested_tools": tool_suggestions,
                "user_context": user_context or {},
                "assistant_type": "technical"
            }
            
            # Generate response
            system_prompt = self._build_system_prompt(
                self.system_prompt,
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
                temperature=0.3,  # Lower temperature for technical accuracy
                max_tokens=1500
            )
            
            # Execute tools if needed
            tool_results = []
            if tool_suggestions and analysis.get("requires_tools", False):
                for tool_suggestion in tool_suggestions[:1]:  # Limit to 1 tool for technical
                    tool_result = await self._execute_tool(
                        db=db,
                        tool_id=tool_suggestion["tool_id"],
                        parameters=tool_suggestion["parameters"],
                        conversation_id=conversation_context.get("conversation_id")
                    )
                    tool_results.append(tool_result)
            
            return {
                "response": response["content"],
                "analysis": analysis,
                "tool_results": tool_results,
                "escalation_recommended": analysis.get("complexity_score", 0) > 0.8,
                "metadata": {
                    "assistant_type": "technical",
                    "technical_category": analysis.get("category", "general"),
                    "complexity": analysis.get("complexity", "medium"),
                    **response.get("metadata", {})
                }
            }
            
        except Exception as e:
            logger.error(f"Technical message processing failed: {e}")
            return {
                "response": "I'm having trouble processing your technical question right now. Could you please rephrase it or provide more specific details about what you're trying to achieve?",
                "error": str(e)
            }
    
    async def should_escalate(
        self,
        db: Session,
        conversation_context: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Determine if technical conversation should be escalated"""
        try:
            escalation_score = 0
            reasons = []
            
            # Check for bug reports
            recent_messages = conversation_context.get("recent_messages", [])
            bug_keywords = ["bug", "error", "broken", "not working", "issue", "problem"]
            
            for msg in recent_messages[-3:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in bug_keywords):
                    escalation_score += 0.4
                    reasons.append("Potential bug report detected")
                    break
            
            # Check for feature requests
            feature_keywords = ["feature", "enhancement", "improvement", "add", "support"]
            for msg in recent_messages[-3:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in feature_keywords):
                    escalation_score += 0.3
                    reasons.append("Feature request detected")
                    break
            
            # Check complexity indicators
            complex_keywords = ["architecture", "scaling", "performance", "security", "enterprise"]
            for msg in recent_messages[-3:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in complex_keywords):
                    escalation_score += 0.5
                    reasons.append("Complex technical discussion")
                    break
            
            # Check for repeated failed attempts
            failed_attempts = conversation_context.get("failed_technical_attempts", 0)
            if failed_attempts > 2:
                escalation_score += 0.6
                reasons.append("Multiple failed resolution attempts")
            
            should_escalate = escalation_score >= 0.7
            
            return {
                "should_escalate": should_escalate,
                "escalation_score": escalation_score,
                "reasons": reasons
            }
            
        except Exception as e:
            logger.error(f"Technical escalation check failed: {e}")
            return {"should_escalate": False, "error": str(e)}
    
    async def _analyze_technical_message(self, message: str) -> Dict[str, Any]:
        """Analyze message for technical patterns"""
        try:
            message_lower = message.lower()
            
            # Categorize technical inquiry
            categories = {
                "api": ["api", "endpoint", "request", "response", "rest", "graphql"],
                "integration": ["integrate", "connect", "webhook", "callback", "oauth"],
                "authentication": ["auth", "login", "token", "jwt", "oauth", "sso"],
                "error": ["error", "exception", "bug", "issue", "problem", "fail"],
                "documentation": ["docs", "documentation", "guide", "tutorial", "example"],
                "performance": ["slow", "performance", "optimization", "speed", "latency"],
                "security": ["security", "vulnerability", "encryption", "ssl", "tls"]
            }
            
            category = "general"
            confidence = 0.5
            
            for cat, keywords in categories.items():
                matches = sum(1 for keyword in keywords if keyword in message_lower)
                if matches > 0:
                    category = cat
                    confidence = min(0.9, 0.6 + (matches * 0.1))
                    break
            
            # Assess complexity
            complexity_indicators = [
                "architecture", "scaling", "enterprise", "custom", "complex",
                "multiple", "integration", "workflow", "pipeline"
            ]
            
            complexity_score = sum(1 for indicator in complexity_indicators if indicator in message_lower)
            
            if complexity_score >= 3:
                complexity = "high"
            elif complexity_score >= 1:
                complexity = "medium"
            else:
                complexity = "low"
            
            # Check for code snippets or technical details
            has_code = any(indicator in message for indicator in ["```", "curl", "http", "json", "{", "function"])
            
            return {
                "category": category,
                "confidence": confidence,
                "complexity": complexity,
                "complexity_score": complexity_score / len(complexity_indicators),
                "has_code": has_code,
                "requires_tools": category in ["api", "integration", "authentication"]
            }
            
        except Exception as e:
            logger.error(f"Technical message analysis failed: {e}")
            return {
                "category": "general",
                "confidence": 0.5,
                "complexity": "medium",
                "complexity_score": 0.5,
                "has_code": False,
                "requires_tools": False
            }
    
    async def _suggest_technical_tools(self, db: Session, message: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest tools for technical inquiries"""
        try:
            suggestions = []
            category = analysis.get("category", "general")
            
            # Get available tools
            available_tools = await self.get_available_tools(db)
            
            # Suggest tools based on category
            if category == "api":
                api_tools = [t for t in available_tools if any(keyword in t.get("name", "").lower() for keyword in ["api", "docs", "swagger"])]
                for tool in api_tools[:1]:
                    suggestions.append({
                        "tool_id": tool["tool_id"],
                        "tool_name": tool["name"],
                        "parameters": {},
                        "reason": "API documentation inquiry"
                    })
            
            elif category == "integration":
                integration_tools = [t for t in available_tools if any(keyword in t.get("name", "").lower() for keyword in ["integration", "webhook", "connect"])]
                for tool in integration_tools[:1]:
                    suggestions.append({
                        "tool_id": tool["tool_id"],
                        "tool_name": tool["name"],
                        "parameters": {},
                        "reason": "Integration guidance needed"
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Technical tool suggestion failed: {e}")
            return []


class AssistantFactory:
    """
    Factory for creating and managing specialized AI assistants
    """
    
    def __init__(self):
        self.assistant_types = {
            "support": SupportAssistant,
            "sales": SalesAssistant,
            "technical": TechnicalAssistant
        }
        
        # Import and register additional assistant types
        self._register_additional_assistants()
    
    async def create_assistant(
        self,
        db: Session,
        assistant_type: str,
        assistant_id: str,
        config: Dict[str, Any]
    ) -> BaseAssistant:
        """Create a specialized assistant instance"""
        try:
            if assistant_type not in self.assistant_types:
                raise ValueError(f"Unknown assistant type: {assistant_type}")
            
            assistant_class = self.assistant_types[assistant_type]
            assistant = assistant_class(assistant_id, config)
            
            # Initialize the assistant
            await assistant.initialize(db)
            
            logger.info(f"Created {assistant_type} assistant: {assistant_id}")
            return assistant
            
        except Exception as e:
            logger.error(f"Failed to create assistant: {e}")
            raise
    
    async def get_assistant_capabilities(self, assistant_type: str) -> Dict[str, Any]:
        """Get capabilities for an assistant type"""
        try:
            if assistant_type not in self.assistant_types:
                return {}
            
            # Create a temporary instance to get capabilities
            assistant_class = self.assistant_types[assistant_type]
            temp_assistant = assistant_class("temp", {})
            
            return {
                "type": assistant_type,
                "capabilities": getattr(temp_assistant, "capabilities", []),
                "escalation_triggers": getattr(temp_assistant, "escalation_triggers", []),
                "conversation_starters": getattr(temp_assistant, "conversation_starters", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to get assistant capabilities: {e}")
            return {}
    
    def get_available_types(self) -> List[str]:
        """Get list of available assistant types"""
        return list(self.assistant_types.keys())
    
    def _register_additional_assistants(self):
        """Register additional assistant types"""
        try:
            logger.info("Starting registration of additional assistant types...")
            
            # Import and register AdminAssistant
            logger.info("Importing AdminAssistant...")
            from ..assistants.admin_assistant import AdminAssistant
            self.assistant_types["admin"] = AdminAssistant
            logger.info("AdminAssistant registered successfully")
            
            # Import and register ContentAssistant
            logger.info("Importing ContentAssistant...")
            from ..assistants.content_assistant import ContentAssistant
            self.assistant_types["content"] = ContentAssistant
            logger.info("ContentAssistant registered successfully")
            
            # Import and register InsightsAssistant
            logger.info("Importing InsightsAssistant...")
            from ..assistants.insights_assistant import InsightsAssistant
            self.assistant_types["insights"] = InsightsAssistant
            logger.info("InsightsAssistant registered successfully")
            
            logger.info(f"All additional assistant types registered. Total types: {list(self.assistant_types.keys())}")
            
        except ImportError as e:
            logger.warning(f"Could not import additional assistant types: {e}")
        except Exception as e:
            logger.error(f"Failed to register additional assistant types: {e}")


# Global factory instance
assistant_factory = AssistantFactory()