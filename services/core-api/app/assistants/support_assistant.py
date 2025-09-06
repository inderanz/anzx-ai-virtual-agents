"""
Support Assistant Implementation
Agent Space-powered customer support assistant with escalation and CRM integration
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from ..services.agent_space_connector_manager import agent_space_manager
from ..services.conversation_context import conversation_context_manager
from ..services.email_service import email_service
from ..models.user import Assistant, Conversation, Message, Organization, User
from .base_assistant import BaseAssistant

logger = logging.getLogger(__name__)


class SupportAssistant(BaseAssistant):
    """
    Support Assistant with Agent Space integration
    
    Features:
    - Agent Space Support agent with knowledge base integration
    - Escalation logic with human handoff capabilities
    - Customer information collection and CRM integration
    - Support ticket creation and tracking workflows
    - Multi-channel support (chat, email, widget)
    """
    
    def __init__(self):
        super().__init__()
        self.assistant_type = "support"
        self.agent_space_manager = agent_space_manager
        
        # Support-specific configuration
        self.escalation_triggers = [
            "speak to human", "human agent", "manager", "supervisor",
            "not helpful", "frustrated", "angry", "complaint",
            "cancel", "refund", "billing issue", "technical problem"
        ]
        
        self.customer_info_fields = [
            "name", "email", "phone", "company", "account_id",
            "subscription_plan", "issue_type", "priority"
        ]
        
        self.support_categories = {
            "billing": {
                "keywords": ["bill", "payment", "charge", "invoice", "subscription", "refund"],
                "priority": "high",
                "escalation_threshold": 2
            },
            "technical": {
                "keywords": ["error", "bug", "not working", "broken", "crash", "slow"],
                "priority": "medium",
                "escalation_threshold": 3
            },
            "account": {
                "keywords": ["login", "password", "access", "account", "profile"],
                "priority": "medium",
                "escalation_threshold": 2
            },
            "general": {
                "keywords": ["help", "question", "how to", "information"],
                "priority": "low",
                "escalation_threshold": 4
            }
        }
    
    async def initialize_assistant(
        self,
        db: Session,
        assistant: Assistant,
        organization: Organization
    ) -> Dict[str, Any]:
        """Initialize Support Assistant with Agent Space"""
        try:
            # Create Agent Space support agent
            agent_config = {
                "name": f"{organization.name} Support Agent",
                "description": f"Customer support agent for {organization.name}",
                "instructions": self._get_support_instructions(organization),
                "tools": ["knowledge_search", "customer_lookup", "ticket_creation"],
                "model": "gemini-1.5-pro",
                "temperature": 0.3,  # More deterministic for support
                "max_tokens": 2000
            }
            
            # Initialize with Agent Space
            agent_space_result = await self.agent_space_manager.create_agent(
                organization_id=str(organization.id),
                agent_config=agent_config
            )
            
            # Update assistant with Agent Space ID
            assistant.agent_space_id = agent_space_result["agent_id"]
            assistant.config = {
                **assistant.config,
                "agent_space_config": agent_config,
                "support_categories": self.support_categories,
                "escalation_triggers": self.escalation_triggers,
                "auto_escalation_enabled": True,
                "collect_customer_info": True,
                "create_support_tickets": True
            }
            
            db.commit()
            
            logger.info(f"Initialized Support Assistant for organization {organization.id}")
            
            return {
                "assistant_id": str(assistant.id),
                "agent_space_id": agent_space_result["agent_id"],
                "capabilities": [
                    "customer_support",
                    "knowledge_base_search",
                    "escalation_management",
                    "ticket_creation",
                    "multi_channel_support"
                ],
                "configuration": assistant.config
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize Support Assistant: {e}")
            raise
    
    async def process_message(
        self,
        db: Session,
        assistant: Assistant,
        conversation: Conversation,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process support message with Agent Space"""
        try:
            # Get conversation context
            conv_context = await conversation_context_manager.get_context(
                db, str(conversation.id)
            )
            
            # Analyze message for support context
            support_analysis = await self._analyze_support_message(
                user_message, conv_context
            )
            
            # Check for escalation triggers
            should_escalate, escalation_reasons = await self._check_escalation_triggers(
                db, conversation, user_message, support_analysis
            )
            
            if should_escalate:
                return await self._handle_escalation(
                    db, assistant, conversation, escalation_reasons
                )
            
            # Collect customer information if needed
            customer_info_updates = await self._extract_customer_info(
                user_message, conv_context
            )
            
            if customer_info_updates:
                await self._update_customer_info(
                    db, conversation, customer_info_updates
                )
            
            # Generate response using Agent Space
            agent_response = await self.agent_space_manager.chat_with_agent(
                agent_id=assistant.agent_space_id,
                message=user_message,
                conversation_id=str(conversation.id),
                context={
                    "support_analysis": support_analysis,
                    "customer_info": conv_context.user_profile if conv_context else {},
                    "conversation_stage": conv_context.conversation_stage if conv_context else "greeting",
                    "previous_solutions": conv_context.previous_solutions if conv_context else []
                }
            )
            
            # Update conversation context
            if conv_context:
                context_updates = {
                    "current_topic": support_analysis.get("category"),
                    "user_intent": support_analysis.get("intent"),
                    "conversation_stage": self._determine_support_stage(
                        user_message, conv_context.conversation_stage
                    )
                }
                
                await conversation_context_manager.update_context(
                    db, str(conversation.id), context_updates
                )
            
            # Create support ticket if needed
            ticket_info = None
            if support_analysis.get("create_ticket", False):
                ticket_info = await self._create_support_ticket(
                    db, conversation, support_analysis
                )
            
            # Prepare response
            response_data = {
                "response": agent_response["response"],
                "metadata": {
                    **agent_response.get("metadata", {}),
                    "support_category": support_analysis.get("category"),
                    "priority": support_analysis.get("priority"),
                    "customer_info_collected": bool(customer_info_updates),
                    "ticket_created": ticket_info is not None
                }
            }
            
            if ticket_info:
                response_data["metadata"]["ticket_id"] = ticket_info["ticket_id"]
                response_data["response"] += f"\n\nI've created support ticket #{ticket_info['ticket_id']} for your issue."
            
            return response_data
            
        except Exception as e:
            logger.error(f"Support Assistant message processing failed: {e}")
            raise
    
    async def handle_escalation(
        self,
        db: Session,
        assistant: Assistant,
        conversation: Conversation,
        escalation_reason: str
    ) -> Dict[str, Any]:
        """Handle escalation to human agent"""
        try:
            # Update conversation status
            conversation.status = "escalated"
            conversation.metadata = conversation.metadata or {}
            conversation.metadata.update({
                "escalated_at": datetime.utcnow().isoformat(),
                "escalation_reason": escalation_reason,
                "escalated_from": "support_assistant"
            })
            
            # Create escalation message
            escalation_message = Message(
                conversation_id=conversation.id,
                content=f"This conversation has been escalated to a human agent. Reason: {escalation_reason}",
                role="system",
                metadata={
                    "escalation": True,
                    "escalation_reason": escalation_reason
                }
            )
            db.add(escalation_message)
            
            # Send escalation notification
            await self._send_escalation_notification(
                db, conversation, escalation_reason
            )
            
            # If email conversation, escalate via email service
            if conversation.metadata.get("channel") == "email":
                await email_service.escalate_email_thread(
                    db=db,
                    organization_id=str(conversation.organization_id),
                    thread_id=conversation.metadata.get("email_thread_id"),
                    escalation_reason=escalation_reason
                )
            
            db.commit()
            
            return {
                "escalated": True,
                "escalation_reason": escalation_reason,
                "message": "Your request has been escalated to a human agent who will assist you shortly."
            }
            
        except Exception as e:
            logger.error(f"Escalation handling failed: {e}")
            raise
    
    async def _analyze_support_message(
        self,
        message: str,
        context: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Analyze message for support-specific context"""
        try:
            message_lower = message.lower()
            
            # Determine category
            category = "general"
            priority = "low"
            
            for cat, config in self.support_categories.items():
                if any(keyword in message_lower for keyword in config["keywords"]):
                    category = cat
                    priority = config["priority"]
                    break
            
            # Determine intent
            intent = "question"
            if any(word in message_lower for word in ["problem", "issue", "error", "broken"]):
                intent = "problem"
            elif any(word in message_lower for word in ["cancel", "refund", "stop"]):
                intent = "cancellation"
            elif any(word in message_lower for word in ["billing", "payment", "charge"]):
                intent = "billing"
            
            # Check if ticket should be created
            create_ticket = (
                intent in ["problem", "billing", "cancellation"] or
                priority in ["high", "urgent"] or
                any(word in message_lower for word in ["ticket", "case", "complaint"])
            )
            
            # Detect urgency
            urgency = "normal"
            if any(word in message_lower for word in ["urgent", "asap", "immediately", "critical"]):
                urgency = "high"
                priority = "high"
            elif any(word in message_lower for word in ["soon", "quickly", "fast"]):
                urgency = "medium"
            
            return {
                "category": category,
                "intent": intent,
                "priority": priority,
                "urgency": urgency,
                "create_ticket": create_ticket,
                "sentiment": self._analyze_sentiment(message)
            }
            
        except Exception as e:
            logger.error(f"Support message analysis failed: {e}")
            return {"category": "general", "intent": "question", "priority": "low"}
    
    async def _check_escalation_triggers(
        self,
        db: Session,
        conversation: Conversation,
        message: str,
        support_analysis: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Check if conversation should be escalated"""
        try:
            escalation_reasons = []
            message_lower = message.lower()
            
            # Check for explicit escalation requests
            for trigger in self.escalation_triggers:
                if trigger in message_lower:
                    escalation_reasons.append(f"Customer requested: {trigger}")
            
            # Check conversation length
            if conversation.message_count > 15:
                escalation_reasons.append("Long conversation without resolution")
            
            # Check priority and category
            category = support_analysis.get("category", "general")
            if category in self.support_categories:
                threshold = self.support_categories[category]["escalation_threshold"]
                if conversation.message_count >= threshold * 2:
                    escalation_reasons.append(f"Exceeded escalation threshold for {category}")
            
            # Check sentiment
            if support_analysis.get("sentiment", {}).get("negative", 0) > 0.8:
                escalation_reasons.append("High negative sentiment detected")
            
            # Check for billing/payment issues
            if support_analysis.get("category") == "billing" and conversation.message_count > 3:
                escalation_reasons.append("Billing issue requires human attention")
            
            # Check conversation context for escalation triggers
            conv_context = await conversation_context_manager.get_context(
                db, str(conversation.id)
            )
            
            if conv_context and len(conv_context.escalation_triggers) >= 3:
                escalation_reasons.append("Multiple escalation indicators detected")
            
            should_escalate = len(escalation_reasons) > 0
            
            return should_escalate, escalation_reasons
            
        except Exception as e:
            logger.error(f"Escalation check failed: {e}")
            return False, []
    
    async def _extract_customer_info(
        self,
        message: str,
        context: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Extract customer information from message"""
        try:
            import re
            
            customer_info = {}
            
            # Extract email
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, message)
            if emails:
                customer_info["email"] = emails[0]
            
            # Extract phone
            phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
            phones = re.findall(phone_pattern, message)
            if phones:
                customer_info["phone"] = "-".join(phones[0])
            
            # Extract account/order numbers
            account_pattern = r'\b(?:account|order|ticket|ref|reference)[\s#:]*([A-Z0-9]{6,})\b'
            accounts = re.findall(account_pattern, message, re.IGNORECASE)
            if accounts:
                customer_info["account_id"] = accounts[0]
            
            # Extract name (simple pattern)
            name_pattern = r'\b(?:my name is|i am|i\'m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
            names = re.findall(name_pattern, message, re.IGNORECASE)
            if names:
                customer_info["name"] = names[0]
            
            # Extract company
            company_pattern = r'\b(?:company|organization|business)[\s:]+([A-Z][A-Za-z\s&]+)\b'
            companies = re.findall(company_pattern, message)
            if companies:
                customer_info["company"] = companies[0].strip()
            
            return customer_info
            
        except Exception as e:
            logger.error(f"Customer info extraction failed: {e}")
            return {}
    
    async def _update_customer_info(
        self,
        db: Session,
        conversation: Conversation,
        customer_info: Dict[str, Any]
    ):
        """Update customer information in conversation context"""
        try:
            conv_context = await conversation_context_manager.get_context(
                db, str(conversation.id)
            )
            
            if conv_context:
                # Update user profile
                current_profile = conv_context.user_profile.copy()
                current_profile.update(customer_info)
                
                await conversation_context_manager.update_context(
                    db, str(conversation.id), {"user_profile": current_profile}
                )
            
        except Exception as e:
            logger.error(f"Customer info update failed: {e}")
    
    async def _create_support_ticket(
        self,
        db: Session,
        conversation: Conversation,
        support_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create support ticket"""
        try:
            # Generate ticket ID
            ticket_id = f"SUP-{int(datetime.utcnow().timestamp())}"
            
            # Get customer info from context
            conv_context = await conversation_context_manager.get_context(
                db, str(conversation.id)
            )
            
            customer_info = conv_context.user_profile if conv_context else {}
            
            # Create ticket metadata
            ticket_data = {
                "ticket_id": ticket_id,
                "conversation_id": str(conversation.id),
                "category": support_analysis.get("category", "general"),
                "priority": support_analysis.get("priority", "low"),
                "status": "open",
                "customer_info": customer_info,
                "created_at": datetime.utcnow().isoformat(),
                "channel": conversation.metadata.get("channel", "chat") if conversation.metadata else "chat"
            }
            
            # Store ticket in conversation metadata
            conversation.metadata = conversation.metadata or {}
            conversation.metadata["support_ticket"] = ticket_data
            
            db.commit()
            
            logger.info(f"Created support ticket {ticket_id} for conversation {conversation.id}")
            
            return ticket_data
            
        except Exception as e:
            logger.error(f"Support ticket creation failed: {e}")
            return {}
    
    def _get_support_instructions(self, organization: Organization) -> str:
        """Get support-specific instructions for Agent Space"""
        return f"""
You are a helpful customer support agent for {organization.name}. Your role is to:

1. Provide excellent customer service with empathy and professionalism
2. Help customers resolve their issues quickly and effectively
3. Collect necessary customer information to assist with their requests
4. Search the knowledge base for relevant solutions
5. Escalate complex issues to human agents when appropriate
6. Create support tickets for tracking purposes

Guidelines:
- Always be polite, patient, and understanding
- Ask clarifying questions to better understand the issue
- Provide step-by-step solutions when possible
- If you cannot resolve an issue, escalate to a human agent
- Keep responses concise but comprehensive
- Use the customer's name when known

Available tools:
- Knowledge base search for finding solutions
- Customer information lookup
- Support ticket creation for issue tracking

Remember: Your goal is to provide the best possible customer experience while efficiently resolving issues.
        """.strip()
    
    def _determine_support_stage(self, message: str, current_stage: str) -> str:
        """Determine support conversation stage"""
        message_lower = message.lower()
        
        if current_stage == "greeting":
            if any(word in message_lower for word in ["help", "problem", "issue"]):
                return "problem_identification"
        
        elif current_stage == "problem_identification":
            if any(word in message_lower for word in ["try", "solution", "fix"]):
                return "solution_providing"
        
        elif current_stage == "solution_providing":
            if any(word in message_lower for word in ["worked", "fixed", "solved", "thanks"]):
                return "resolution"
            elif any(word in message_lower for word in ["didn't work", "still", "not working"]):
                return "problem_identification"  # Back to problem identification
        
        return current_stage
    
    def _analyze_sentiment(self, message: str) -> Dict[str, float]:
        """Simple sentiment analysis"""
        positive_words = ["good", "great", "excellent", "happy", "satisfied", "thanks", "perfect"]
        negative_words = ["bad", "terrible", "awful", "frustrated", "angry", "disappointed", "horrible"]
        
        message_lower = message.lower()
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        total_words = len(message.split())
        
        return {
            "positive": min(positive_count / max(total_words, 1), 1.0),
            "negative": min(negative_count / max(total_words, 1), 1.0),
            "neutral": max(0, 1.0 - (positive_count + negative_count) / max(total_words, 1))
        }
    
    async def _handle_escalation(
        self,
        db: Session,
        assistant: Assistant,
        conversation: Conversation,
        escalation_reasons: List[str]
    ) -> Dict[str, Any]:
        """Handle escalation process"""
        try:
            escalation_reason = "; ".join(escalation_reasons)
            
            result = await self.handle_escalation(
                db, assistant, conversation, escalation_reason
            )
            
            return {
                "response": result["message"],
                "metadata": {
                    "escalated": True,
                    "escalation_reason": escalation_reason,
                    "escalation_reasons": escalation_reasons
                }
            }
            
        except Exception as e:
            logger.error(f"Escalation handling failed: {e}")
            return {
                "response": "I apologize, but I'm having trouble escalating your request. Please contact our support team directly.",
                "metadata": {"escalation_failed": True}
            }
    
    async def _send_escalation_notification(
        self,
        db: Session,
        conversation: Conversation,
        escalation_reason: str
    ):
        """Send escalation notification to support team"""
        try:
            # This would integrate with notification service
            # For now, just log the escalation
            logger.info(f"Support escalation: Conversation {conversation.id} escalated. Reason: {escalation_reason}")
            
            # In a real implementation, this would:
            # 1. Send email notification to support team
            # 2. Create Slack notification
            # 3. Update support dashboard
            # 4. Potentially integrate with ticketing system
            
        except Exception as e:
            logger.error(f"Failed to send escalation notification: {e}")


# Global instance
support_assistant = SupportAssistant()