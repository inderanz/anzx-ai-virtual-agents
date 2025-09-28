"""
LLM Agent for Cricket Assistant
Wrapper for Vertex AI chat (Gemini 1.5 Flash) with cricket-specific prompts
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.config import get_settings

logger = logging.getLogger(__name__)

class LLMAgent:
    """LLM agent wrapper for Vertex AI chat"""
    
    def __init__(self):
        self.settings = get_settings()
        self.model_name = self.settings.vertex_model
        self.location = self.settings.vertex_location
        
        # Initialize Vertex AI client
        try:
            from google.cloud import aiplatform
            aiplatform.init(project=self.settings.gcp_project, location=self.location)
            self.client = aiplatform.gapic.PredictionServiceClient()
            self.initialized = True
        except Exception as e:
            logger.warning(f"Failed to initialize Vertex AI client: {e}")
            self.client = None
            self.initialized = False
    
    async def classify_intent(self, text: str) -> Dict[str, Any]:
        """
        Classify user intent using LLM
        
        Args:
            text: User query text
            
        Returns:
            Intent classification result
        """
        if not self.initialized:
            return {"intent": "unknown", "entities": {}}
        
        try:
            prompt = f"""Classify the following cricket query into one of these intents:
- player_team: "Which team does [player] play for?"
- player_last_runs: "How many runs did [player] score in last match?"
- fixtures_list: "List fixtures for [team]"
- ladder_position: "Where is [team] on the ladder?"
- next_fixture: "Next fixture for [team]"
- roster_list: "List players for [team]"

Query: "{text}"

Respond with JSON only:
{{"intent": "intent_name", "entities": {{"player": "name", "team": "team_name"}}}}"""
            
            response = await self._call_vertex_ai(prompt, temperature=0.1)
            
            # Parse JSON response
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse LLM response as JSON: {response}")
                return {"intent": "unknown", "entities": {}}
                
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return {"intent": "unknown", "entities": {}}
    
    async def summarise(self, context: str, query: str) -> str:
        """
        Summarize context to answer query
        
        Args:
            context: Relevant context information
            query: User query
            
        Returns:
            Summarized response
        """
        if not self.initialized:
            return "I don't have that information."
        
        try:
            prompt = f"""Based on the following cricket data, answer the user's question concisely and accurately.

Context:
{context}

Question: {query}

Guidelines:
- Use bullet lists for multiple items
- Bold important information like team names, dates, and scores
- If information is not available, say "I don't have that information"
- Be helpful but don't make up information

Answer:"""
            
            response = await self._call_vertex_ai(prompt, temperature=0.2)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "I don't have that information."
    
    async def _call_vertex_ai(self, prompt: str, temperature: float = 0.1) -> str:
        """
        Call Vertex AI with the given prompt
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            
        Returns:
            Generated response
        """
        if not self.initialized or not self.client:
            raise Exception("Vertex AI client not initialized")
        
        try:
            # Prepare the request
            request = {
                "instances": [{
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }],
                "parameters": {
                    "temperature": temperature,
                    "maxOutputTokens": 1000,
                    "topP": 0.8,
                    "topK": 40
                }
            }
            
            # Make the prediction
            endpoint = f"projects/{self.settings.gcp_project}/locations/{self.location}/publishers/google/models/{self.model_name}"
            
            response = self.client.predict(
                endpoint=endpoint,
                instances=request["instances"],
                parameters=request["parameters"]
            )
            
            # Extract the response
            if response.predictions:
                prediction = response.predictions[0]
                if "candidates" in prediction:
                    candidate = prediction["candidates"][0]
                    if "content" in candidate:
                        return candidate["content"]
            
            return "I don't have that information."
            
        except Exception as e:
            logger.error(f"Vertex AI call failed: {e}")
            raise Exception(f"Vertex AI call failed: {e}")
    
    def is_available(self) -> bool:
        """Check if LLM agent is available"""
        return self.initialized and self.client is not None

# Mock implementation for testing
class MockLLMAgent(LLMAgent):
    """Mock LLM agent for testing"""
    
    def __init__(self):
        self.initialized = True
        self.client = None
    
    async def classify_intent(self, text: str) -> Dict[str, Any]:
        """Mock intent classification"""
        text_lower = text.lower()
        
        if "which team" in text_lower and "player" in text_lower:
            return {"intent": "player_team", "entities": {"player": "John Smith"}}
        elif "runs" in text_lower and "last" in text_lower:
            return {"intent": "player_last_runs", "entities": {"player": "John Smith"}}
        elif "fixtures" in text_lower or "schedule" in text_lower:
            return {"intent": "fixtures_list", "entities": {"team": "Caroline Springs Blue U10"}}
        elif "ladder" in text_lower or "position" in text_lower:
            return {"intent": "ladder_position", "entities": {"team": "Caroline Springs Blue U10"}}
        elif "next" in text_lower and "fixture" in text_lower:
            return {"intent": "next_fixture", "entities": {"team": "Caroline Springs Blue U10"}}
        elif "roster" in text_lower or "players" in text_lower:
            return {"intent": "roster_list", "entities": {"team": "Caroline Springs Blue U10"}}
        else:
            return {"intent": "unknown", "entities": {}}
    
    async def summarise(self, context: str, query: str) -> str:
        """Mock summarization"""
        return f"Based on the context: {context[:100]}... I can help with your query: {query}"
    
    def is_available(self) -> bool:
        """Mock availability check"""
        return True

def get_llm_agent() -> LLMAgent:
    """Get LLM agent instance"""
    settings = get_settings()
    
    # Use mock in test environment
    if settings.app_env == "test":
        return MockLLMAgent()
    
    return LLMAgent()
