"""
Conversation Context Manager
Handles conversation state, context continuity, and memory management
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from dataclasses import dataclass, asdict

from ..models.user import Conversation, Message, Assistant

logger = logging.getLogger(__name__)


@dataclass
class ConversationContext:
    """Conversation context data structure"""
    conversation_id: str
    assistant_id: str
    organization_id: str
    user_id: Optional[str]
    channel: str
    
    # Context state
    current_topic: Optional[str] = None
    user_intent: Optional[str] = None
    conversation_stage: str = "greeting"  # greeting, information_gathering, problem_solving, resolution
    
    # User information
    user_profile: Dict[str, Any] = None
    user_preferences: Dict[str, Any] = None
    
    # Conversation memory
    key_facts: List[str] = None
    mentioned_entities: Dict[str, Any] = None
    previous_solutions: List[str] = None
    
    # State tracking
    escalation_triggers: List[str] = None
    satisfaction_indicators: Dict[str, Any] = None
    
    # Metadata
    last_updated: datetime = None
    context_version: int = 1
    
    def __post_init__(self):
        if self.user_profile is None:
            self.user_profile = {}
        if self.user_preferences is None:
            self.user_preferences = {}
        if self.key_facts is None:
            self.key_facts = []
        if self.mentioned_entities is None:
            self.mentioned_entities = {}
        if self.previous_solutions is None:
            self.previous_solutions = []
        if self.escalation_triggers is None:
            self.escalation_triggers = []
        if self.satisfaction_indicators is None:
            self.satisfaction_indicators = {}
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()


class ConversationContextManager:
    """
    Manages conversation context and state across messages
    
    Features:
    - Context persistence and retrieval
    - Automatic context updates from messages
    - Intent and topic tracking
    - Escalation trigger detection
    - Memory management and cleanup
    """
    
    def __init__(self):
        self.context_cache = {}  # In-memory cache for active contexts
        self.cache_ttl = timedelta(hours=2)  # Cache TTL
    
    async def get_context(
        self,
        db: Session,
        conversation_id: str
    ) -> Optional[ConversationContext]:
        """
        Get conversation context
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            
        Returns:
            Conversation context or None
        """
        try:
            # Check cache first
            if conversation_id in self.context_cache:
                cached_context, cached_time = self.context_cache[conversation_id]
                if datetime.utcnow() - cached_time < self.cache_ttl:
                    return cached_context
                else:
                    # Remove expired cache
                    del self.context_cache[conversation_id]
            
            # Get conversation from database
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if not conversation:
                return None
            
            # Load context from conversation metadata
            context_data = conversation.metadata.get("context", {}) if conversation.metadata else {}
            
            # Create context object
            context = ConversationContext(
                conversation_id=str(conversation.id),
                assistant_id=str(conversation.assistant_id),
                organization_id=str(conversation.organization_id),
                user_id=str(conversation.user_id) if conversation.user_id else None,
                channel=conversation.metadata.get("channel", "web") if conversation.metadata else "web"
            )
            
            # Load context state from metadata
            if context_data:
                context.current_topic = context_data.get("current_topic")
                context.user_intent = context_data.get("user_intent")
                context.conversation_stage = context_data.get("conversation_stage", "greeting")
                context.user_profile = context_data.get("user_profile", {})
                context.user_preferences = context_data.get("user_preferences", {})
                context.key_facts = context_data.get("key_facts", [])
                context.mentioned_entities = context_data.get("mentioned_entities", {})
                context.previous_solutions = context_data.get("previous_solutions", [])
                context.escalation_triggers = context_data.get("escalation_triggers", [])
                context.satisfaction_indicators = context_data.get("satisfaction_indicators", {})
                context.context_version = context_data.get("context_version", 1)
                
                # Parse last_updated if present
                if context_data.get("last_updated"):
                    try:
                        context.last_updated = datetime.fromisoformat(context_data["last_updated"])
                    except:
                        context.last_updated = datetime.utcnow()
            
            # Cache the context
            self.context_cache[conversation_id] = (context, datetime.utcnow())
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get conversation context: {e}")
            return None
    
    async def update_context(
        self,
        db: Session,
        conversation_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update conversation context
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            updates: Context updates
            
        Returns:
            Success status
        """
        try:
            # Get current context
            context = await self.get_context(db, conversation_id)
            if not context:
                return False
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(context, key):
                    setattr(context, key, value)
            
            context.last_updated = datetime.utcnow()
            context.context_version += 1
            
            # Save to database
            await self.save_context(db, context)
            
            # Update cache
            self.context_cache[conversation_id] = (context, datetime.utcnow())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update conversation context: {e}")
            return False
    
    async def save_context(
        self,
        db: Session,
        context: ConversationContext
    ) -> bool:
        """
        Save conversation context to database
        
        Args:
            db: Database session
            context: Conversation context
            
        Returns:
            Success status
        """
        try:
            # Get conversation
            conversation = db.query(Conversation).filter(
                Conversation.id == context.conversation_id
            ).first()
            
            if not conversation:
                return False
            
            # Prepare context data
            context_data = {
                "current_topic": context.current_topic,
                "user_intent": context.user_intent,
                "conversation_stage": context.conversation_stage,
                "user_profile": context.user_profile,
                "user_preferences": context.user_preferences,
                "key_facts": context.key_facts,
                "mentioned_entities": context.mentioned_entities,
                "previous_solutions": context.previous_solutions,
                "escalation_triggers": context.escalation_triggers,
                "satisfaction_indicators": context.satisfaction_indicators,
                "last_updated": context.last_updated.isoformat(),
                "context_version": context.context_version
            }
            
            # Update conversation metadata
            metadata = conversation.metadata or {}
            metadata["context"] = context_data
            conversation.metadata = metadata
            conversation.updated_at = datetime.utcnow()
            
            db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save conversation context: {e}")
            db.rollback()
            return False
    
    async def analyze_message_for_context(
        self,
        db: Session,
        conversation_id: str,
        message: str,
        role: str
    ) -> Dict[str, Any]:
        """
        Analyze message and extract context updates
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            message: Message content
            role: Message role (user/assistant)
            
        Returns:
            Context updates
        """
        try:
            context_updates = {}
            
            # Get current context
            context = await self.get_context(db, conversation_id)
            if not context:
                return {}
            
            # Analyze user messages for context
            if role == "user":
                # Extract entities and facts
                entities = self._extract_entities(message)
                if entities:
                    current_entities = context.mentioned_entities.copy()
                    current_entities.update(entities)
                    context_updates["mentioned_entities"] = current_entities
                
                # Detect intent
                intent = self._detect_intent(message)
                if intent and intent != context.user_intent:
                    context_updates["user_intent"] = intent
                
                # Extract key facts
                facts = self._extract_key_facts(message)
                if facts:
                    current_facts = context.key_facts.copy()
                    current_facts.extend(facts)
                    # Keep only unique facts and limit to last 10
                    unique_facts = list(dict.fromkeys(current_facts))[-10:]
                    context_updates["key_facts"] = unique_facts
                
                # Detect escalation triggers
                escalation_triggers = self._detect_escalation_triggers(message)
                if escalation_triggers:
                    current_triggers = context.escalation_triggers.copy()
                    current_triggers.extend(escalation_triggers)
                    context_updates["escalation_triggers"] = current_triggers
                
                # Update conversation stage
                new_stage = self._determine_conversation_stage(message, context.conversation_stage)
                if new_stage != context.conversation_stage:
                    context_updates["conversation_stage"] = new_stage
            
            # Analyze assistant messages
            elif role == "assistant":
                # Extract solutions provided
                solutions = self._extract_solutions(message)
                if solutions:
                    current_solutions = context.previous_solutions.copy()
                    current_solutions.extend(solutions)
                    # Keep only last 5 solutions
                    context_updates["previous_solutions"] = current_solutions[-5:]
                
                # Detect topic changes
                topic = self._extract_topic(message)
                if topic and topic != context.current_topic:
                    context_updates["current_topic"] = topic
            
            return context_updates
            
        except Exception as e:
            logger.error(f"Failed to analyze message for context: {e}")
            return {}
    
    async def get_context_summary(
        self,
        db: Session,
        conversation_id: str
    ) -> str:
        """
        Generate a context summary for the conversation
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            
        Returns:
            Context summary string
        """
        try:
            context = await self.get_context(db, conversation_id)
            if not context:
                return "No context available."
            
            summary_parts = []
            
            # Current state
            if context.current_topic:
                summary_parts.append(f"Current topic: {context.current_topic}")
            
            if context.user_intent:
                summary_parts.append(f"User intent: {context.user_intent}")
            
            summary_parts.append(f"Conversation stage: {context.conversation_stage}")
            
            # Key facts
            if context.key_facts:
                facts_str = "; ".join(context.key_facts[-3:])  # Last 3 facts
                summary_parts.append(f"Key facts: {facts_str}")
            
            # Entities
            if context.mentioned_entities:
                entities_str = ", ".join([f"{k}: {v}" for k, v in list(context.mentioned_entities.items())[:3]])
                summary_parts.append(f"Mentioned: {entities_str}")
            
            # Previous solutions
            if context.previous_solutions:
                solutions_str = "; ".join(context.previous_solutions[-2:])  # Last 2 solutions
                summary_parts.append(f"Previous solutions: {solutions_str}")
            
            # Escalation indicators
            if context.escalation_triggers:
                summary_parts.append(f"Escalation triggers: {len(context.escalation_triggers)} detected")
            
            return " | ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Failed to generate context summary: {e}")
            return "Context summary unavailable."
    
    async def should_escalate(
        self,
        db: Session,
        conversation_id: str
    ) -> Tuple[bool, List[str]]:
        """
        Determine if conversation should be escalated
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            
        Returns:
            (should_escalate, reasons)
        """
        try:
            context = await self.get_context(db, conversation_id)
            if not context:
                return False, []
            
            escalation_reasons = []
            
            # Check escalation triggers
            if len(context.escalation_triggers) >= 3:
                escalation_reasons.append("Multiple escalation triggers detected")
            
            # Check conversation length
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if conversation and conversation.message_count > 20:
                escalation_reasons.append("Long conversation without resolution")
            
            # Check for specific trigger phrases
            trigger_phrases = [
                "speak to human", "human agent", "not helpful", "frustrated",
                "cancel", "refund", "complaint", "manager", "supervisor"
            ]
            
            recent_triggers = [t for t in context.escalation_triggers if any(phrase in t.lower() for phrase in trigger_phrases)]
            if recent_triggers:
                escalation_reasons.append("Direct request for human assistance")
            
            # Check satisfaction indicators
            if context.satisfaction_indicators.get("negative_sentiment", 0) > 0.7:
                escalation_reasons.append("High negative sentiment detected")
            
            should_escalate = len(escalation_reasons) > 0
            
            return should_escalate, escalation_reasons
            
        except Exception as e:
            logger.error(f"Failed to check escalation criteria: {e}")
            return False, []
    
    def _extract_entities(self, message: str) -> Dict[str, str]:
        """Extract named entities from message (simplified)"""
        entities = {}
        
        # Simple patterns for common entities
        import re
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, message)
        if emails:
            entities["email"] = emails[0]
        
        # Phone numbers (simple pattern)
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        phones = re.findall(phone_pattern, message)
        if phones:
            entities["phone"] = "-".join(phones[0])
        
        # Order/ticket numbers
        order_pattern = r'\b(?:order|ticket|ref|reference)[\s#:]*([A-Z0-9]{6,})\b'
        orders = re.findall(order_pattern, message, re.IGNORECASE)
        if orders:
            entities["order_number"] = orders[0]
        
        return entities
    
    def _detect_intent(self, message: str) -> Optional[str]:
        """Detect user intent from message (simplified)"""
        message_lower = message.lower()
        
        # Intent patterns
        intent_patterns = {
            "question": ["what", "how", "when", "where", "why", "?"],
            "problem": ["issue", "problem", "error", "bug", "broken", "not working"],
            "request": ["need", "want", "can you", "please", "help me"],
            "complaint": ["unhappy", "disappointed", "terrible", "awful", "bad"],
            "compliment": ["great", "excellent", "perfect", "amazing", "love"],
            "cancel": ["cancel", "refund", "return", "stop"],
            "information": ["tell me", "explain", "information", "details"]
        }
        
        for intent, keywords in intent_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        return "general"
    
    def _extract_key_facts(self, message: str) -> List[str]:
        """Extract key facts from message (simplified)"""
        facts = []
        
        # Look for factual statements
        sentences = message.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and any(word in sentence.lower() for word in ["is", "was", "have", "had", "am", "are"]):
                facts.append(sentence)
        
        return facts[:3]  # Limit to 3 facts per message
    
    def _detect_escalation_triggers(self, message: str) -> List[str]:
        """Detect escalation triggers in message"""
        triggers = []
        message_lower = message.lower()
        
        escalation_phrases = [
            "speak to human", "human agent", "real person", "not helpful",
            "frustrated", "angry", "upset", "disappointed", "terrible",
            "manager", "supervisor", "complaint", "cancel", "refund"
        ]
        
        for phrase in escalation_phrases:
            if phrase in message_lower:
                triggers.append(f"User mentioned: {phrase}")
        
        return triggers
    
    def _determine_conversation_stage(self, message: str, current_stage: str) -> str:
        """Determine conversation stage based on message"""
        message_lower = message.lower()
        
        # Stage transition logic
        if current_stage == "greeting":
            if any(word in message_lower for word in ["help", "problem", "issue", "need"]):
                return "information_gathering"
        
        elif current_stage == "information_gathering":
            if any(word in message_lower for word in ["try", "solution", "fix", "resolve"]):
                return "problem_solving"
        
        elif current_stage == "problem_solving":
            if any(word in message_lower for word in ["thanks", "solved", "fixed", "working", "resolved"]):
                return "resolution"
            elif any(word in message_lower for word in ["still", "not working", "didn't work"]):
                return "information_gathering"  # Back to gathering more info
        
        return current_stage
    
    def _extract_solutions(self, message: str) -> List[str]:
        """Extract solutions from assistant message"""
        solutions = []
        
        # Look for solution indicators
        solution_indicators = ["try", "solution", "fix", "resolve", "step", "follow"]
        
        sentences = message.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if any(indicator in sentence.lower() for indicator in solution_indicators):
                if len(sentence) > 20:  # Meaningful solution
                    solutions.append(sentence)
        
        return solutions[:2]  # Limit to 2 solutions per message
    
    def _extract_topic(self, message: str) -> Optional[str]:
        """Extract main topic from message"""
        # Simple topic extraction based on keywords
        topics = {
            "billing": ["bill", "payment", "charge", "invoice", "subscription"],
            "technical": ["error", "bug", "not working", "broken", "issue"],
            "account": ["account", "login", "password", "profile", "settings"],
            "product": ["product", "feature", "how to", "usage", "guide"],
            "support": ["help", "support", "assistance", "question"]
        }
        
        message_lower = message.lower()
        for topic, keywords in topics.items():
            if any(keyword in message_lower for keyword in keywords):
                return topic
        
        return None
    
    def cleanup_expired_contexts(self):
        """Clean up expired contexts from cache"""
        try:
            current_time = datetime.utcnow()
            expired_keys = []
            
            for conversation_id, (context, cached_time) in self.context_cache.items():
                if current_time - cached_time > self.cache_ttl:
                    expired_keys.append(conversation_id)
            
            for key in expired_keys:
                del self.context_cache[key]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired conversation contexts")
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired contexts: {e}")


# Global instance
conversation_context_manager = ConversationContextManager()