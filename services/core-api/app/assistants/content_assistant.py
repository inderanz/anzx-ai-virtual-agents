"""
Content Assistant Implementation
Specialized assistant for content generation, brand consistency, and multi-platform content creation
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..services.assistant_factory import BaseAssistant
from ..services.vertex_ai_service import vertex_ai_service
# Mock import for development
# from ..services.hybrid_agent_orchestrator import hybrid_agent_orchestrator
hybrid_agent_orchestrator = None

logger = logging.getLogger(__name__)


class ContentAssistant(BaseAssistant):
    """
    Content Assistant
    
    Specialized for content generation, brand tone analysis,
    multi-platform content adaptation, and content workflows.
    """
    
    async def initialize(self, db: Session) -> Dict[str, Any]:
        """Initialize content assistant with custom LangGraph workflows"""
        self.capabilities = [
            "communication", "analytics", "general"
        ]
        
        self.system_prompt = """
You are a creative content assistant specializing in content generation and brand consistency. Your role is to:

1. Generate high-quality content for various platforms and purposes
2. Maintain brand voice and tone consistency across all content
3. Adapt content for different platforms (social media, email, web, blog)
4. Analyze and improve existing content for engagement and clarity
5. Create content calendars and publishing schedules
6. Ensure content aligns with brand guidelines and messaging

Always focus on creating engaging, on-brand content that resonates with the target audience.
Consider platform-specific requirements and best practices for each content type.
        """.strip()
        
        self.conversation_starters = [
            "Hi! I'm your content assistant. I can help you create engaging content, maintain brand consistency, and adapt content for different platforms. What would you like to create today?",
            "Hello! I specialize in content creation and brand messaging. Whether you need social media posts, blog articles, or email campaigns, I'm here to help. What's your content goal?",
            "Welcome! I'm here to help you create compelling content that aligns with your brand voice. What type of content are you looking to develop?"
        ]
        
        self.escalation_triggers = [
            "legal or compliance review needed for content",
            "sensitive or controversial content topics",
            "large-scale content campaign planning",
            "brand guideline conflicts or updates needed",
            "content performance issues requiring strategy review"
        ]
        
        # Initialize custom LangGraph workflow
        try:
            await self._initialize_content_workflows(db)
        except Exception as e:
            logger.warning(f"Content workflow initialization failed: {e}")
        
        return {
            "type": "content",
            "capabilities": self.capabilities,
            "tools_available": len(await self.get_available_tools(db)),
            "escalation_triggers": len(self.escalation_triggers),
            "custom_workflows": True
        }
    
    async def process_message(
        self,
        db: Session,
        message: str,
        conversation_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process content message with specialized workflows"""
        try:
            # Analyze message for content-specific patterns
            analysis = await self._analyze_content_message(message)
            
            # Get brand context
            brand_context = await self._get_brand_context(db, user_context)
            
            # Build enhanced context
            enhanced_context = {
                **conversation_context,
                "message_analysis": analysis,
                "brand_context": brand_context,
                "user_context": user_context or {},
                "assistant_type": "content"
            }
            
            # Use custom LangGraph workflow for content generation
            if analysis.get("category") in ["generation", "adaptation", "optimization"]:
                response = await self._process_with_content_workflow(
                    db, message, enhanced_context
                )
            else:
                # Use Vertex AI for general content tasks
                response = await self._process_with_vertex_ai(
                    db, message, enhanced_context
                )
            
            # Execute content actions if needed
            content_actions = []
            if analysis.get("requires_content_action", False):
                content_actions = await self._execute_content_actions(
                    db, analysis, response, user_context
                )
            
            return {
                "response": response["content"],
                "analysis": analysis,
                "brand_context": brand_context,
                "content_actions": content_actions,
                "escalation_recommended": analysis.get("complexity_score", 0) > 0.8,
                "metadata": {
                    "assistant_type": "content",
                    "content_category": analysis.get("category", "general"),
                    "brand_alignment": analysis.get("brand_alignment", "unknown"),
                    "platforms": analysis.get("target_platforms", []),
                    **response.get("metadata", {})
                }
            }
            
        except Exception as e:
            logger.error(f"Content message processing failed: {e}")
            return {
                "response": "I'm having trouble processing your content request right now. Could you please provide more details about what type of content you'd like me to help you create?",
                "error": str(e)
            }
    
    async def should_escalate(
        self,
        db: Session,
        conversation_context: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Determine if content conversation should be escalated"""
        try:
            escalation_score = 0
            reasons = []
            
            # Check for sensitive content topics
            recent_messages = conversation_context.get("recent_messages", [])
            sensitive_keywords = [
                "legal", "compliance", "controversial", "political", "sensitive",
                "confidential", "proprietary", "lawsuit", "regulation"
            ]
            
            for msg in recent_messages[-3:]:
                content = msg.get("content", "").lower()
                for keyword in sensitive_keywords:
                    if keyword in content:
                        escalation_score += 0.6
                        reasons.append(f"Sensitive content topic: {keyword}")
                        break
            
            # Check for brand guideline conflicts
            brand_keywords = ["brand", "guideline", "voice", "tone", "style", "conflict"]
            conflict_count = 0
            for msg in recent_messages[-5:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in brand_keywords):
                    conflict_count += 1
            
            if conflict_count >= 3:
                escalation_score += 0.4
                reasons.append("Potential brand guideline conflicts")
            
            # Check for large-scale campaign requests
            campaign_keywords = ["campaign", "large scale", "multiple platforms", "strategy", "launch"]
            for msg in recent_messages[-3:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in campaign_keywords):
                    escalation_score += 0.5
                    reasons.append("Large-scale campaign planning detected")
                    break
            
            # Check for performance issues
            performance_keywords = ["not working", "poor performance", "low engagement", "failing"]
            for msg in recent_messages[-3:]:
                content = msg.get("content", "").lower()
                if any(keyword in content for keyword in performance_keywords):
                    escalation_score += 0.3
                    reasons.append("Content performance issues reported")
                    break
            
            should_escalate = escalation_score >= 0.7
            
            return {
                "should_escalate": should_escalate,
                "escalation_score": escalation_score,
                "reasons": reasons
            }
            
        except Exception as e:
            logger.error(f"Content escalation check failed: {e}")
            return {"should_escalate": False, "error": str(e)}
    
    async def _initialize_content_workflows(self, db: Session):
        """Initialize custom LangGraph workflows for content generation"""
        try:
            # Define content generation workflow
            content_workflow = {
                "workflow_id": f"content_generation_{self.assistant_id}",
                "workflow_type": "content_generation",
                "steps": [
                    {
                        "step_id": "analyze_request",
                        "type": "analysis",
                        "description": "Analyze content request and requirements"
                    },
                    {
                        "step_id": "brand_alignment",
                        "type": "brand_check",
                        "description": "Check brand voice and tone alignment"
                    },
                    {
                        "step_id": "content_generation",
                        "type": "generation",
                        "description": "Generate content based on requirements"
                    },
                    {
                        "step_id": "platform_adaptation",
                        "type": "adaptation",
                        "description": "Adapt content for target platforms"
                    },
                    {
                        "step_id": "quality_review",
                        "type": "review",
                        "description": "Review content quality and consistency"
                    }
                ],
                "tools": [
                    "brand_analyzer",
                    "content_generator",
                    "platform_adapter",
                    "quality_checker"
                ]
            }
            
            # Register workflow with hybrid orchestrator (mock for development)
            if hybrid_agent_orchestrator:
                await hybrid_agent_orchestrator.register_workflow(
                    db=db,
                    workflow_config=content_workflow
                )
            else:
                logger.info("Mock workflow registration for content generation")
            
            logger.info(f"Content workflows initialized for assistant: {self.assistant_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize content workflows: {e}")
            raise
    
    async def _analyze_content_message(self, message: str) -> Dict[str, Any]:
        """Analyze message for content-specific patterns"""
        try:
            message_lower = message.lower()
            
            # Categorize content request
            categories = {
                "generation": [
                    "create", "write", "generate", "draft", "compose",
                    "content", "post", "article", "blog", "copy"
                ],
                "adaptation": [
                    "adapt", "convert", "transform", "rewrite", "modify",
                    "platform", "social media", "email", "web"
                ],
                "optimization": [
                    "optimize", "improve", "enhance", "better", "engagement",
                    "seo", "keywords", "performance"
                ],
                "analysis": [
                    "analyze", "review", "check", "evaluate", "assess",
                    "brand", "tone", "voice", "consistency"
                ],
                "planning": [
                    "plan", "strategy", "calendar", "schedule", "campaign",
                    "timeline", "roadmap"
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
            
            # Extract content details
            content_details = self._extract_content_details(message)
            
            # Identify target platforms
            platform_keywords = {
                "social": ["social", "facebook", "twitter", "instagram", "linkedin", "tiktok"],
                "email": ["email", "newsletter", "campaign", "mailchimp"],
                "web": ["website", "web", "landing page", "homepage"],
                "blog": ["blog", "article", "post", "medium"],
                "video": ["video", "youtube", "vimeo", "script"],
                "print": ["print", "brochure", "flyer", "poster"]
            }
            
            target_platforms = []
            for platform, keywords in platform_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    target_platforms.append(platform)
            
            # Assess complexity
            complexity_indicators = [
                "multiple", "campaign", "series", "brand", "strategy",
                "guidelines", "approval", "review", "legal"
            ]
            
            complexity_score = sum(1 for indicator in complexity_indicators if indicator in message_lower)
            complexity = "high" if complexity_score >= 3 else "medium" if complexity_score >= 1 else "low"
            
            # Check brand alignment requirements
            brand_keywords = ["brand", "voice", "tone", "style", "guidelines", "consistency"]
            brand_alignment = "required" if any(keyword in message_lower for keyword in brand_keywords) else "standard"
            
            return {
                "category": category,
                "confidence": confidence,
                "complexity": complexity,
                "complexity_score": complexity_score / len(complexity_indicators),
                "content_details": content_details,
                "target_platforms": target_platforms,
                "brand_alignment": brand_alignment,
                "requires_content_action": category in ["generation", "adaptation", "optimization"]
            }
            
        except Exception as e:
            logger.error(f"Content message analysis failed: {e}")
            return {
                "category": "general",
                "confidence": 0.5,
                "complexity": "medium",
                "complexity_score": 0.5,
                "content_details": {},
                "target_platforms": [],
                "brand_alignment": "standard",
                "requires_content_action": False
            }
    
    def _extract_content_details(self, message: str) -> Dict[str, Any]:
        """Extract content details from message"""
        import re
        
        details = {}
        
        # Extract content type
        content_types = [
            "blog post", "article", "social media post", "email", "newsletter",
            "landing page", "product description", "press release", "ad copy",
            "video script", "podcast script", "whitepaper", "case study"
        ]
        
        for content_type in content_types:
            if content_type in message.lower():
                details["content_type"] = content_type
                break
        
        # Extract target audience
        audience_patterns = [
            r'(?:for|targeting|audience)\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|!|\?)',
            r'(?:customers|clients|users|people)\s+(?:who|that)\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|!|\?)'
        ]
        
        for pattern in audience_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                details["target_audience"] = matches[0].strip()
                break
        
        # Extract tone/style requirements
        tone_keywords = [
            "professional", "casual", "friendly", "formal", "conversational",
            "authoritative", "playful", "serious", "humorous", "technical"
        ]
        
        for tone in tone_keywords:
            if tone in message.lower():
                details["tone"] = tone
                break
        
        # Extract length requirements
        length_pattern = r'(\d+)\s*(?:words|characters|sentences|paragraphs)'
        length_matches = re.findall(length_pattern, message, re.IGNORECASE)
        if length_matches:
            details["length"] = length_matches[0]
        
        # Extract keywords/topics
        keyword_patterns = [
            r'(?:about|regarding|on)\s+([a-zA-Z\s,]+?)(?:\s|$|\.|!|\?)',
            r'(?:keywords?|topics?|subjects?)[:\s]+([a-zA-Z\s,]+?)(?:\s|$|\.|!|\?)'
        ]
        
        for pattern in keyword_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                keywords = [kw.strip() for kw in matches[0].split(',')]
                details["keywords"] = keywords
                break
        
        return details
    
    async def _get_brand_context(self, db: Session, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get brand context for content generation"""
        try:
            # Mock brand context - in real implementation would query brand guidelines
            context = {
                "brand_name": user_context.get("organization_name", "Your Brand") if user_context else "Your Brand",
                "brand_voice": {
                    "tone": "professional yet approachable",
                    "personality": ["helpful", "knowledgeable", "trustworthy"],
                    "avoid": ["jargon", "overly technical language", "aggressive sales language"]
                },
                "brand_guidelines": {
                    "colors": ["#007bff", "#28a745", "#ffc107"],
                    "fonts": ["Arial", "Helvetica", "sans-serif"],
                    "logo_usage": "Always include brand logo in visual content"
                },
                "messaging": {
                    "value_proposition": "Empowering businesses with AI-driven solutions",
                    "key_messages": [
                        "Innovation through AI",
                        "Customer-centric approach",
                        "Reliable and secure solutions"
                    ]
                },
                "content_standards": {
                    "max_sentence_length": 20,
                    "reading_level": "grade 8-10",
                    "call_to_action_style": "clear and direct"
                }
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get brand context: {e}")
            return {}
    
    async def _process_with_content_workflow(
        self,
        db: Session,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process message using custom content generation workflow"""
        try:
            # Use hybrid orchestrator for content workflow (mock for development)
            if hybrid_agent_orchestrator:
                workflow_response = await hybrid_agent_orchestrator.execute_workflow(
                    db=db,
                    workflow_id=f"content_generation_{self.assistant_id}",
                    input_data={
                        "message": message,
                        "context": context,
                        "brand_context": context.get("brand_context", {}),
                        "analysis": context.get("message_analysis", {})
                    }
                )
            else:
                # Mock workflow response
                workflow_response = {
                    "generated_content": f"This is mock generated content based on your request: '{message}'. In a full implementation, this would be created using our advanced content generation workflow.",
                    "metadata": {"mock": True, "workflow": "content_generation"}
                }
            
            return {
                "content": workflow_response.get("generated_content", "I've processed your content request using our specialized workflow."),
                "metadata": {
                    "source": "content_workflow",
                    "workflow_id": f"content_generation_{self.assistant_id}",
                    **workflow_response.get("metadata", {})
                }
            }
            
        except Exception as e:
            logger.error(f"Content workflow processing failed: {e}")
            # Fallback to Vertex AI
            return await self._process_with_vertex_ai(db, message, context)
    
    async def _process_with_vertex_ai(
        self,
        db: Session,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process message using Vertex AI for general content tasks"""
        try:
            # Build enhanced system prompt with brand context
            brand_context = context.get("brand_context", {})
            enhanced_prompt = self.system_prompt
            
            if brand_context:
                brand_info = f"""
                
Brand Context:
- Brand: {brand_context.get('brand_name', 'N/A')}
- Voice: {brand_context.get('brand_voice', {}).get('tone', 'professional')}
- Key Messages: {', '.join(brand_context.get('messaging', {}).get('key_messages', []))}
- Content Standards: Reading level {brand_context.get('content_standards', {}).get('reading_level', 'grade 8-10')}
                """
                enhanced_prompt += brand_info
            
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
                temperature=0.8,  # Higher temperature for creativity
                max_tokens=1500
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Vertex AI processing failed: {e}")
            return {
                "content": "I'm having trouble generating content right now. Please try again or provide more specific requirements.",
                "metadata": {"error": str(e)}
            }
    
    async def _execute_content_actions(
        self,
        db: Session,
        analysis: Dict[str, Any],
        response: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute content actions based on analysis and response"""
        try:
            actions = []
            content_details = analysis.get("content_details", {})
            target_platforms = analysis.get("target_platforms", [])
            
            # Content generation action
            if analysis.get("category") == "generation":
                action = {
                    "type": "generate_content",
                    "details": {
                        "content_type": content_details.get("content_type", "general"),
                        "target_audience": content_details.get("target_audience"),
                        "tone": content_details.get("tone", "professional"),
                        "length": content_details.get("length"),
                        "keywords": content_details.get("keywords", [])
                    },
                    "status": "completed"
                }
                actions.append(action)
            
            # Platform adaptation actions
            if target_platforms and analysis.get("category") == "adaptation":
                for platform in target_platforms:
                    action = {
                        "type": "adapt_for_platform",
                        "details": {
                            "platform": platform,
                            "original_content": response.get("content", ""),
                            "platform_requirements": self._get_platform_requirements(platform)
                        },
                        "status": "ready"
                    }
                    actions.append(action)
            
            # Brand consistency check action
            if analysis.get("brand_alignment") == "required":
                action = {
                    "type": "brand_consistency_check",
                    "details": {
                        "content": response.get("content", ""),
                        "brand_guidelines": content_details.get("brand_guidelines", {})
                    },
                    "status": "pending"
                }
                actions.append(action)
            
            return actions
            
        except Exception as e:
            logger.error(f"Content action execution failed: {e}")
            return []
    
    def _get_platform_requirements(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific content requirements"""
        requirements = {
            "social": {
                "max_length": 280,
                "hashtags": True,
                "mentions": True,
                "visual_required": True
            },
            "email": {
                "subject_line": True,
                "call_to_action": True,
                "personalization": True,
                "unsubscribe_link": True
            },
            "web": {
                "seo_optimized": True,
                "meta_description": True,
                "headings": True,
                "internal_links": True
            },
            "blog": {
                "title": True,
                "introduction": True,
                "conclusion": True,
                "word_count": "800-1500"
            }
        }
        
        return requirements.get(platform, {})


# Add ContentAssistant to the factory
def register_content_assistant():
    """Register ContentAssistant with the factory"""
    from ..services.assistant_factory import assistant_factory
    assistant_factory.assistant_types["content"] = ContentAssistant