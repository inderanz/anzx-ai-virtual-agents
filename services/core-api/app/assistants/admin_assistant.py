"""
Admin Assistant Implementation
Specialized assistant for administrative tasks, calendar management, and scheduling
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..services.assistant_factory import BaseAssistant
from ..services.vertex_ai_service import vertex_ai_service
from ..services.agent_space_connector_manager import agent_space_connector_manager
from ..config.google_connectors import GOOGLE_CALENDAR_CONFIG

logger = logging.getLogger(__name__)


class AdminAssistant(BaseAssistant):
    """
    Administrative Assistant
    
    Specialized for calendar management, meeting scheduling,
    task management, and administrative workflows.
    """
    
    async def initialize(self, db: Session) -> Dict[str, Any]:
        """Initialize admin assistant with Agent Space integration"""
        logger.info(f"Initializing admin assistant with ID: {self.assistant_id}")
        
        self.capabilities = [
            "communication", "general", "analytics"
        ]
        
        self.system_prompt = """
You are an administrative assistant specializing in calendar management and scheduling. Your role is to:

1. Schedule meetings and appointments with conflict detection
2. Manage calendar events and send invitations
3. Handle task management and reminders
4. Compose and send professional emails
5. Coordinate between multiple participants and time zones
6. Provide scheduling recommendations and alternatives

Always confirm details before scheduling and provide clear confirmation messages.
Be proactive in suggesting optimal meeting times and handling conflicts.
        """.strip()
        
        self.conversation_starters = [
            "Hi! I'm your admin assistant. I can help you schedule meetings, manage your calendar, and handle administrative tasks. What would you like me to help you with?",
            "Hello! I'm here to help with scheduling, calendar management, and administrative support. How can I assist you today?",
            "Welcome! I specialize in calendar management and administrative tasks. What can I help you organize today?"
        ]
        
        self.escalation_triggers = [
            "complex multi-party scheduling conflicts",
            "urgent meeting requests requiring immediate attention",
            "calendar integration issues or technical problems",
            "sensitive or confidential meeting arrangements",
            "budget or resource allocation requests"
        ]
        
        # Initialize Agent Space connection for calendar integration
        try:
            await self._initialize_agent_space_integration(db)
        except Exception as e:
            logger.warning(f"Agent Space integration failed: {e}")
        
        return {
            "type": "admin",
            "capabilities": self.capabilities,
            "tools_available": len(await self.get_available_tools(db)),
            "escalation_triggers": len(self.escalation_triggers),
            "agent_space_enabled": True
        }
    
    async def process_message(
        self,
        db: Session,
        message: str,
        conversation_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process admin message with calendar and scheduling logic"""
        try:
            # Analyze message for admin-specific patterns
            analysis = await self._analyze_admin_message(message)
            
            # Get calendar context if needed
            calendar_context = {}
            if analysis.get("requires_calendar", False):
                calendar_context = await self._get_calendar_context(db, user_context)
            
            # Build enhanced context
            enhanced_context = {
                **conversation_context,
                "message_analysis": analysis,
                "calendar_context": calendar_context,
                "user_context": user_context or {},
                "assistant_type": "admin"
            }
            
            # Use Agent Space for calendar-related requests
            if analysis.get("category") in ["scheduling", "calendar"]:
                response = await self._process_with_agent_space(
                    db, message, enhanced_context
                )
            else:
                # Use Vertex AI for general admin tasks
                response = await self._process_with_vertex_ai(
                    db, message, enhanced_context
                )
            
            # Execute calendar actions if needed
            calendar_actions = []
            if analysis.get("requires_calendar_action", False):
                calendar_actions = await self._execute_calendar_actions(
                    db, analysis, response, user_context
                )
            
            return {
                "response": response["content"],
                "analysis": analysis,
                "calendar_context": calendar_context,
                "calendar_actions": calendar_actions,
                "escalation_recommended": analysis.get("complexity_score", 0) > 0.8,
                "metadata": {
                    "assistant_type": "admin",
                    "admin_category": analysis.get("category", "general"),
                    "calendar_integration": len(calendar_actions) > 0,
                    **response.get("metadata", {})
                }
            }
            
        except Exception as e:
            logger.error(f"Admin message processing failed: {e}")
            return {
                "response": "I'm having trouble processing your request right now. Could you please provide more specific details about what you'd like me to help you with?",
                "error": str(e)
            }
    
    async def should_escalate(
        self,
        db: Session,
        conversation_context: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Determine if admin conversation should be escalated"""
        try:
            escalation_score = 0
            reasons = []
            
            # Check for complex scheduling conflicts
            recent_messages = conversation_context.get("recent_messages", [])
            conflict_keywords = ["conflict", "busy", "unavailable", "reschedule", "urgent"]
            
            conflict_count = 0
            for msg in recent_messages[-5:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in conflict_keywords):
                    conflict_count += 1
            
            if conflict_count >= 3:
                escalation_score += 0.5
                reasons.append("Multiple scheduling conflicts detected")
            
            # Check for urgent requests
            urgent_keywords = ["urgent", "asap", "immediately", "emergency", "critical"]
            for msg in recent_messages[-3:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in urgent_keywords):
                    escalation_score += 0.4
                    reasons.append("Urgent request detected")
                    break
            
            # Check for sensitive meeting requests
            sensitive_keywords = ["confidential", "private", "board", "executive", "legal"]
            for msg in recent_messages[-3:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in sensitive_keywords):
                    escalation_score += 0.6
                    reasons.append("Sensitive meeting request")
                    break
            
            # Check for technical issues
            tech_keywords = ["error", "not working", "broken", "issue", "problem"]
            for msg in recent_messages[-3:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in tech_keywords):
                    escalation_score += 0.3
                    reasons.append("Technical issue reported")
                    break
            
            should_escalate = escalation_score >= 0.7
            
            return {
                "should_escalate": should_escalate,
                "escalation_score": escalation_score,
                "reasons": reasons
            }
            
        except Exception as e:
            logger.error(f"Admin escalation check failed: {e}")
            return {"should_escalate": False, "error": str(e)}
    
    async def _initialize_agent_space_integration(self, db: Session):
        """Initialize Agent Space integration for calendar management"""
        try:
            # Configure Agent Space admin agent
            agent_config = {
                "agent_type": "admin",
                "connectors": ["google_calendar", "gmail"],
                "capabilities": [
                    "calendar_management",
                    "meeting_scheduling", 
                    "email_composition",
                    "task_management"
                ],
                "tools": [
                    "create_calendar_event",
                    "find_meeting_times",
                    "send_calendar_invites",
                    "check_availability",
                    "compose_email",
                    "send_email"
                ]
            }
            
            # Initialize with Agent Space
            await agent_space_connector_manager.initialize_agent(
                db=db,
                agent_id=self.assistant_id,
                config=agent_config
            )
            
            logger.info(f"Agent Space integration initialized for admin assistant: {self.assistant_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Agent Space integration: {e}")
            raise
    
    async def _analyze_admin_message(self, message: str) -> Dict[str, Any]:
        """Analyze message for admin-specific patterns"""
        try:
            message_lower = message.lower()
            
            # Categorize admin request
            categories = {
                "scheduling": [
                    "schedule", "meeting", "appointment", "book", "calendar",
                    "available", "free time", "when can", "set up meeting"
                ],
                "calendar": [
                    "calendar", "event", "reminder", "reschedule", "cancel",
                    "move meeting", "change time", "availability"
                ],
                "email": [
                    "email", "send", "compose", "write", "message",
                    "follow up", "invitation", "notify"
                ],
                "tasks": [
                    "task", "reminder", "todo", "deadline", "follow up",
                    "action item", "track", "manage"
                ],
                "coordination": [
                    "coordinate", "organize", "arrange", "multiple people",
                    "team meeting", "group", "participants"
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
            
            # Extract scheduling details
            scheduling_details = self._extract_scheduling_details(message)
            
            # Assess complexity
            complexity_indicators = [
                "multiple", "several", "team", "group", "recurring",
                "series", "weekly", "monthly", "conflict", "reschedule"
            ]
            
            complexity_score = sum(1 for indicator in complexity_indicators if indicator in message_lower)
            complexity = "high" if complexity_score >= 3 else "medium" if complexity_score >= 1 else "low"
            
            # Check urgency
            urgency_keywords = ["urgent", "asap", "immediately", "today", "tomorrow"]
            urgency = "high" if any(keyword in message_lower for keyword in urgency_keywords) else "normal"
            
            return {
                "category": category,
                "confidence": confidence,
                "complexity": complexity,
                "complexity_score": complexity_score / len(complexity_indicators),
                "urgency": urgency,
                "scheduling_details": scheduling_details,
                "requires_calendar": category in ["scheduling", "calendar"],
                "requires_calendar_action": category in ["scheduling", "calendar"] and scheduling_details.get("action_required", False)
            }
            
        except Exception as e:
            logger.error(f"Admin message analysis failed: {e}")
            return {
                "category": "general",
                "confidence": 0.5,
                "complexity": "medium",
                "complexity_score": 0.5,
                "urgency": "normal",
                "scheduling_details": {},
                "requires_calendar": False,
                "requires_calendar_action": False
            }
    
    def _extract_scheduling_details(self, message: str) -> Dict[str, Any]:
        """Extract scheduling details from message"""
        import re
        from dateutil import parser
        
        details = {}
        
        # Extract dates and times
        date_patterns = [
            r'\b(?:today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b'
        ]
        
        time_patterns = [
            r'\b\d{1,2}:\d{2}\s*(?:am|pm)?\b',
            r'\b\d{1,2}\s*(?:am|pm)\b'
        ]
        
        dates_found = []
        times_found = []
        
        for pattern in date_patterns:
            dates_found.extend(re.findall(pattern, message, re.IGNORECASE))
        
        for pattern in time_patterns:
            times_found.extend(re.findall(pattern, message, re.IGNORECASE))
        
        if dates_found:
            details["dates"] = dates_found
        if times_found:
            details["times"] = times_found
        
        # Extract duration
        duration_pattern = r'\b(\d+)\s*(?:hour|hr|minute|min)s?\b'
        durations = re.findall(duration_pattern, message, re.IGNORECASE)
        if durations:
            details["duration"] = durations[0]
        
        # Extract participants
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, message)
        if emails:
            details["participants"] = emails
        
        # Extract meeting type/purpose
        meeting_keywords = ["meeting", "call", "discussion", "review", "standup", "demo", "presentation"]
        for keyword in meeting_keywords:
            if keyword in message.lower():
                details["meeting_type"] = keyword
                break
        
        # Determine if action is required
        action_keywords = ["schedule", "book", "set up", "arrange", "create"]
        details["action_required"] = any(keyword in message.lower() for keyword in action_keywords)
        
        return details
    
    async def _get_calendar_context(self, db: Session, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get calendar context for scheduling decisions"""
        try:
            # Mock calendar context - in real implementation would query Google Calendar
            context = {
                "current_time": datetime.now().isoformat(),
                "timezone": user_context.get("timezone", "UTC") if user_context else "UTC",
                "busy_times": [
                    {
                        "start": (datetime.now() + timedelta(hours=2)).isoformat(),
                        "end": (datetime.now() + timedelta(hours=3)).isoformat(),
                        "title": "Existing Meeting"
                    }
                ],
                "available_slots": [
                    {
                        "start": (datetime.now() + timedelta(hours=4)).isoformat(),
                        "end": (datetime.now() + timedelta(hours=5)).isoformat()
                    },
                    {
                        "start": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
                        "end": (datetime.now() + timedelta(days=1, hours=3)).isoformat()
                    }
                ],
                "working_hours": {
                    "start": "09:00",
                    "end": "17:00",
                    "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
                }
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get calendar context: {e}")
            return {}
    
    async def _process_with_agent_space(
        self,
        db: Session,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process message using Agent Space for calendar operations"""
        try:
            # Use Agent Space for calendar-related operations
            agent_response = await agent_space_connector_manager.process_message(
                db=db,
                agent_id=self.assistant_id,
                message=message,
                context=context
            )
            
            return {
                "content": agent_response.get("response", "I've processed your calendar request."),
                "metadata": {
                    "source": "agent_space",
                    "agent_id": self.assistant_id,
                    **agent_response.get("metadata", {})
                }
            }
            
        except Exception as e:
            logger.error(f"Agent Space processing failed: {e}")
            # Fallback to Vertex AI
            return await self._process_with_vertex_ai(db, message, context)
    
    async def _process_with_vertex_ai(
        self,
        db: Session,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process message using Vertex AI for general admin tasks"""
        try:
            system_prompt = self._build_system_prompt(
                self.system_prompt,
                {
                    "organization_name": self.config.get("organization_name"),
                    "available_tools": await self.get_available_tools(db),
                    "calendar_context": context.get("calendar_context", {})
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
            
            return response
            
        except Exception as e:
            logger.error(f"Vertex AI processing failed: {e}")
            return {
                "content": "I'm having trouble processing your request right now. Please try again or provide more specific details.",
                "metadata": {"error": str(e)}
            }
    
    async def _execute_calendar_actions(
        self,
        db: Session,
        analysis: Dict[str, Any],
        response: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute calendar actions based on analysis and response"""
        try:
            actions = []
            scheduling_details = analysis.get("scheduling_details", {})
            
            if scheduling_details.get("action_required", False):
                # Create calendar event action
                if analysis.get("category") == "scheduling":
                    action = {
                        "type": "create_event",
                        "details": {
                            "title": scheduling_details.get("meeting_type", "Meeting"),
                            "participants": scheduling_details.get("participants", []),
                            "duration": scheduling_details.get("duration", "60"),
                            "suggested_times": scheduling_details.get("times", []),
                            "dates": scheduling_details.get("dates", [])
                        },
                        "status": "pending_confirmation"
                    }
                    actions.append(action)
                
                # Send calendar invites action
                if scheduling_details.get("participants"):
                    action = {
                        "type": "send_invites",
                        "details": {
                            "recipients": scheduling_details["participants"],
                            "meeting_details": scheduling_details
                        },
                        "status": "ready"
                    }
                    actions.append(action)
            
            return actions
            
        except Exception as e:
            logger.error(f"Calendar action execution failed: {e}")
            return []


# Add AdminAssistant to the factory
def register_admin_assistant():
    """Register AdminAssistant with the factory"""
    from ..services.assistant_factory import assistant_factory
    assistant_factory.assistant_types["admin"] = AdminAssistant