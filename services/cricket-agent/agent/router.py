"""
Cricket Agent Intent Router
Handles intent detection, planning, and response generation for cricket queries
"""

import re
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import pytz

from app.config import get_settings, is_private_mode, get_cscc_team_ids, get_cscc_org_id, get_cscc_season_id, get_cscc_grade_id
from agent.tools.vector_client import get_vector_client
from agent.tools.playhq import initialize_playhq_client
from agent.tools.normalize import CricketDataNormalizer, CricketSnippetGenerator
from agent.prompt import SYSTEM_PROMPT, format_response
from agent.llm_agent import LLMAgent

logger = logging.getLogger(__name__)

# In-memory cache for performance
_cache: Dict[str, Dict[str, Any]] = {}
_cache_ttl = 30 * 60  # 30 minutes

class IntentRouter:
    """Cricket agent intent router with RAG and tool fallback"""
    
    def __init__(self):
        self.settings = get_settings()
        self.vector_client = get_vector_client()
        self.normalizer = CricketDataNormalizer()
        self.snippet_generator = CricketSnippetGenerator()
        self.llm_agent = LLMAgent()
        
        # Intent patterns for regex detection
        self.intent_patterns = {
            "player_team": [
                r"which team.*is\s+(\w+).*in",
                r"what team.*(\w+).*in",
                r"(\w+).*team",
                r"team.*(\w+)",
                r"(\w+).*plays"
            ],
            "player_last_runs": [
                r"how many runs.*(\w+).*score.*last\s+match",
                r"(\w+).*runs.*last\s+match",
                r"(\w+).*scored.*last\s+game",
                r"last\s+match.*(\w+).*runs"
            ],
            "fixtures_list": [
                r"list.*fixtures.*(.*?)(?:\s+for|\s+of|\s*$)",
                r"fixtures.*(.*?)(?:\s+for|\s+of|\s*$)",
                r"upcoming.*matches.*(.*?)(?:\s+for|\s+of|\s*$)",
                r"schedule.*(.*?)(?:\s+for|\s+of|\s*$)"
            ],
            "ladder_position": [
                r"ladder.*for\s+(.*)",
                r"show.*ladder.*for\s+(.*)",
                r"ladder\s+(.*)",
                r"standings.*for\s+(.*)",
                r"position.*for\s+(.*)"
            ],
            "next_fixture": [
                r"next.*fixture.*(\w+.*\w+)",
                r"next.*match.*(\w+.*\w+)",
                r"upcoming.*(\w+.*\w+).*fixture",
                r"when.*(\w+.*\w+).*play.*next"
            ],
            "roster_list": [
                r"list.*players.*(.*?)(?:\s+for|\s+of|\s*$)",
                r"roster.*(.*?)(?:\s+for|\s+of|\s*$)",
                r"players.*(.*?)(?:\s+for|\s+of|\s*$)",
                r"team.*members.*(.*?)(?:\s+for|\s+of|\s*$)"
            ]
        }
    
    async def route_query(self, text: str, source: str = "web", team_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Route cricket query to appropriate handler
        
        Args:
            text: User query text
            source: Query source (web, whatsapp)
            team_hint: Optional team hint for disambiguation
            
        Returns:
            Response with answer and metadata
        """
        start_time = time.time()
        request_id = f"req_{int(start_time * 1000)}"
        
        try:
            # Check cache first
            cache_key = f"{text}_{team_hint or ''}"
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                logger.info(f"Cache hit for request {request_id}")
                return cached_response
            
            # Use LLM-driven RAG approach instead of complex regex patterns
            rag_start = time.time()
            answer = await self._llm_driven_rag(text, team_hint)
            rag_ms = int((time.time() - rag_start) * 1000)
            
            # Set intent to llm_rag for consistency
            intent = "llm_rag"
            entities = {}
            api_ms = 0
            
            total_latency = int((time.time() - start_time) * 1000)
            
            # Cache the response
            response = {
                "answer": answer,
                "meta": {
                    "intent": intent,
                    "entities": entities,
                    "rag_ms": rag_ms,
                    "api_ms": api_ms,
                    "latency_ms": total_latency,
                    "source": source,
                    "request_id": request_id
                }
            }
            
            self._cache_response(cache_key, response)
            
            logger.info(f"Query processed successfully", extra={
                "request_id": request_id,
                "intent": intent,
                "rag_ms": rag_ms,
                "api_ms": api_ms,
                "latency_ms": total_latency
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}", extra={"request_id": request_id})
            return {
                "answer": "I'm sorry, I encountered an error processing your request. Please try again.",
                "meta": {
                    "intent": "error",
                    "entities": {},
                    "rag_ms": 0,
                    "api_ms": 0,
                    "latency_ms": int((time.time() - start_time) * 1000),
                    "source": source,
                    "request_id": request_id,
                    "error": str(e)
                }
            }
    
    async def _detect_intent(self, text: str) -> Dict[str, Any]:
        """Detect intent using regex first, then LLM fallback"""
        text_lower = text.lower()
        
        # Try regex patterns first
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    entities = self._extract_entities_from_match(match, intent)
                    return {"intent": intent, "entities": entities}
        
        # Fallback to LLM classification
        try:
            llm_result = await self.llm_agent.classify_intent(text)
            return llm_result
        except Exception as e:
            logger.warning(f"LLM intent classification failed: {e}")
            return {"intent": "unknown", "entities": {}}
    
    def _extract_entities_from_match(self, match: re.Match, intent: str) -> Dict[str, str]:
        """Extract entities from regex match"""
        entities = {}
        
        if intent == "player_team":
            entities["player"] = match.group(1)
        elif intent == "player_last_runs":
            entities["player"] = match.group(1)
        elif intent in ["fixtures_list", "ladder_position", "next_fixture", "roster_list"]:
            team_name = match.group(1)
            entities["team"] = self._normalize_team_name(team_name)
        
        return entities
    
    def _normalize_team_name(self, team_name: str) -> str:
        """Normalize team name to match configured teams"""
        # Map common variations to configured team names
        team_mapping = {
            "blue 10s": "Caroline Springs Blue U10",
            "blue u10": "Caroline Springs Blue U10",
            "blue 10": "Caroline Springs Blue U10",
            "white 10s": "Caroline Springs White U10",
            "white u10": "Caroline Springs White U10",
            "white 10": "Caroline Springs White U10"
        }
        
        normalized = team_name.lower().strip()
        return team_mapping.get(normalized, team_name)
    
    async def _query_rag(self, text: str, entities: Dict[str, str]) -> List[str]:
        """Query vector store for relevant snippets"""
        try:
            # Build filters from entities
            filters = {}
            if "team" in entities:
                # Map team name to team_id if needed
                team_id = self._get_team_id_from_name(entities["team"])
                if team_id:
                    filters["team_id"] = team_id
            
            if "season_id" in entities:
                filters["season_id"] = entities["season_id"]
            
            if "grade_id" in entities:
                filters["grade_id"] = entities["grade_id"]
            
            # Query vector store to get document IDs
            doc_ids = self.vector_client.query(text, filters, k=6)
            
            # Retrieve actual document content
            results = []
            for doc_id in doc_ids:
                try:
                    # Get document content from vector store
                    doc_content = self.vector_client.get_document(doc_id)
                    if doc_content:
                        results.append(doc_content)
                except Exception as e:
                    logger.warning(f"Failed to retrieve document {doc_id}: {e}")
                    continue
            
            logger.info(f"RAG query returned {len(results)} document contents")
            return results
            
        except Exception as e:
            logger.warning(f"RAG query failed: {e}")
            return []
    
    def _get_team_id_from_name(self, team_name: str) -> Optional[str]:
        """Get team ID from team name"""
        from app.config import get_settings
        settings = get_settings()
        
        if settings.ids_bundle and settings.ids_bundle.teams:
            for team in settings.ids_bundle.teams:
                if team.name.lower() == team_name.lower():
                    return team.team_id
        
        return None
    
    async def _execute_handler(self, intent: str, entities: Dict[str, str], rag_results: List[str], original_text: str) -> str:
        """Execute appropriate handler based on intent"""
        try:
            if intent == "player_team":
                return await self._handle_player_team(entities, rag_results)
            elif intent == "player_last_runs":
                return await self._handle_player_last_runs(entities, rag_results)
            elif intent == "fixtures_list":
                return await self._handle_fixtures_list(entities, rag_results)
            elif intent == "ladder_position":
                return await self._handle_ladder_position(entities, rag_results)
            elif intent == "next_fixture":
                return await self._handle_next_fixture(entities, rag_results)
            elif intent == "roster_list":
                return await self._handle_roster_list(entities, rag_results)
            else:
                return await self._handle_unknown_intent(original_text, rag_results)
                
        except Exception as e:
            logger.error(f"Handler execution failed for intent {intent}: {e}")
            return "I'm sorry, I encountered an error processing your request."
    
    async def _handle_player_team(self, entities: Dict[str, str], rag_results: List[str]) -> str:
        """Handle player team lookup"""
        player_name = entities.get("player", "")
        
        if not player_name:
            return "I need a player name to find their team."
        
        # Check RAG results first
        for result in rag_results:
            if player_name.lower() in result.lower():
                # Extract team from snippet
                lines = result.split('\n')
                for line in lines:
                    if 'Team:' in line:
                        team_name = line.split('Team:')[1].strip()
                        return f"**{player_name}** plays for **{team_name}**"
        
        # Fallback to PlayHQ API
        try:
            playhq_client = await initialize_playhq_client()
            
            # Search for player in recent games
            from app.config import get_cscc_team_ids
            team_ids = get_cscc_team_ids()
            
            for team_id in team_ids:
                fixtures = await playhq_client.get_team_fixtures(team_id, "current_season")
                for fixture in fixtures:
                    if fixture.get("status") == "completed":
                        summary = await playhq_client.get_game_summary(fixture["id"])
                        if summary and self._player_in_summary(summary, player_name):
                            # Find team name
                            team_name = self._get_team_name_from_fixture(fixture, team_id)
                            await playhq_client.close()
                            return f"**{player_name}** plays for **{team_name}**"
            
            await playhq_client.close()
            return f"I don't have information about player **{player_name}** in the current data."
            
        except Exception as e:
            logger.error(f"Player team lookup failed: {e}")
            return f"I couldn't find information about **{player_name}**."
    
    async def _handle_player_last_runs(self, entities: Dict[str, str], rag_results: List[str]) -> str:
        """Handle player last match runs"""
        player_name = entities.get("player", "")
        
        if not player_name:
            return "I need a player name to find their last match runs."
        
        # Check RAG results first
        for result in rag_results:
            if player_name.lower() in result.lower() and "runs" in result.lower():
                # Extract runs from snippet
                lines = result.split('\n')
                for line in lines:
                    if player_name.lower() in line.lower() and "runs" in line.lower():
                        return f"**{player_name}** scored **{self._extract_runs_from_line(line)}** runs in their last match."
        
        # Fallback to PlayHQ API
        try:
            playhq_client = await initialize_playhq_client()
            
            from app.config import get_cscc_team_ids
            team_ids = get_cscc_team_ids()
            
            for team_id in team_ids:
                fixtures = await playhq_client.get_team_fixtures(team_id, "current_season")
                # Get most recent completed fixture
                completed_fixtures = [f for f in fixtures if f.get("status") == "completed"]
                if completed_fixtures:
                    latest_fixture = max(completed_fixtures, key=lambda x: x.get("date", ""))
                    summary = await playhq_client.get_game_summary(latest_fixture["id"])
                    
                    if summary and self._player_in_summary(summary, player_name):
                        runs = self._extract_player_runs_from_summary(summary, player_name)
                        await playhq_client.close()
                        return f"**{player_name}** scored **{runs}** runs in their last match."
            
            await playhq_client.close()
            return f"I don't have information about **{player_name}**'s last match runs."
            
        except Exception as e:
            logger.error(f"Player last runs lookup failed: {e}")
            return f"I couldn't find **{player_name}**'s last match runs."
    
    async def _handle_fixtures_list(self, entities: Dict[str, str], rag_results: List[str]) -> str:
        """Handle fixtures list request"""
        team_name = entities.get("team", "")
        
        if not team_name:
            return "I need a team name to list fixtures."
        
        team_id = self._get_team_id_from_name(team_name)
        if not team_id:
            return f"I don't have information about team **{team_name}**."
        
        try:
            playhq_client = await initialize_playhq_client()
            fixtures = await playhq_client.get_team_fixtures(team_id, "current_season")
            await playhq_client.close()
            
            if not fixtures:
                return f"No fixtures found for **{team_name}**."
            
            # Format fixtures
            response_lines = [f"**{team_name}** fixtures:"]
            for fixture in fixtures[:10]:  # Limit to 10 fixtures
                date_str = self._format_fixture_date(fixture.get("date", ""))
                opponent = fixture.get("opponent", "TBD")
                venue = fixture.get("venue", "TBD")
                status = fixture.get("status", "scheduled")
                
                response_lines.append(f"• **{date_str}** – {opponent} – {venue} – {status}")
            
            return "\n".join(response_lines)
            
        except Exception as e:
            logger.error(f"Fixtures list lookup failed: {e}")
            return f"I couldn't retrieve fixtures for **{team_name}**."
    
    async def _handle_ladder_position(self, entities: Dict[str, str], rag_results: List[str]) -> str:
        """Handle ladder position request"""
        team_name = entities.get("team", "")
        
        if not team_name:
            return "I need a team name to check ladder position."
        
        team_id = self._get_team_id_from_name(team_name)
        if not team_id:
            return f"I don't have information about team **{team_name}**."
        
        try:
            playhq_client = await initialize_playhq_client()
            
            # Get grade ID for the team
            from app.config import get_cscc_grade_id
            grade_id = get_cscc_grade_id()
            
            if not grade_id:
                return f"I don't have grade information for **{team_name}**."
            
            ladder = await playhq_client.get_ladder(grade_id)
            await playhq_client.close()
            
            if not ladder:
                return f"No ladder data available for **{team_name}**."
            
            # Find team position
            for entry in ladder:
                if entry.get("team_id") == team_id:
                    position = entry.get("position", "N/A")
                    points = entry.get("points", 0)
                    played = entry.get("matches_played", 0)
                    won = entry.get("matches_won", 0)
                    lost = entry.get("matches_lost", 0)
                    
                    current_date = datetime.now(pytz.timezone('Australia/Melbourne')).strftime("%d %b %Y")
                    
                    return f"**{team_name}** is in **{position}** position on the ladder (as of {current_date}):\n• Points: {points}\n• Played: {played}\n• Won: {won}\n• Lost: {lost}"
            
            return f"**{team_name}** not found on the ladder."
            
        except Exception as e:
            logger.error(f"Ladder position lookup failed: {e}")
            return f"I couldn't retrieve ladder position for **{team_name}**."
    
    async def _handle_next_fixture(self, entities: Dict[str, str], rag_results: List[str]) -> str:
        """Handle next fixture request"""
        team_name = entities.get("team", "")
        
        if not team_name:
            return "I need a team name to find the next fixture."
        
        team_id = self._get_team_id_from_name(team_name)
        if not team_id:
            return f"I don't have information about team **{team_name}**."
        
        try:
            playhq_client = await initialize_playhq_client()
            fixtures = await playhq_client.get_team_fixtures(team_id, "current_season")
            await playhq_client.close()
            
            if not fixtures:
                return f"No fixtures found for **{team_name}**."
            
            # Find next scheduled fixture
            upcoming_fixtures = [f for f in fixtures if f.get("status") == "scheduled"]
            if not upcoming_fixtures:
                return f"No upcoming fixtures for **{team_name}**."
            
            next_fixture = min(upcoming_fixtures, key=lambda x: x.get("date", ""))
            
            date_str = self._format_fixture_date(next_fixture.get("date", ""))
            opponent = next_fixture.get("opponent", "TBD")
            venue = next_fixture.get("venue", "TBD")
            
            return f"**{team_name}**'s next fixture:\n• **{date_str}** – vs {opponent}\n• Venue: {venue}"
            
        except Exception as e:
            logger.error(f"Next fixture lookup failed: {e}")
            return f"I couldn't retrieve the next fixture for **{team_name}**."
    
    async def _handle_roster_list(self, entities: Dict[str, str], rag_results: List[str]) -> str:
        """Handle roster list request"""
        team_name = entities.get("team", "")
        
        if not team_name:
            return "I need a team name to list the roster."
        
        team_id = self._get_team_id_from_name(team_name)
        if not team_id:
            return f"I don't have information about team **{team_name}**."
        
        try:
            playhq_client = await initialize_playhq_client()
            
            # Get roster from recent games
            from app.config import get_cscc_team_ids
            team_ids = get_cscc_team_ids()
            
            players = set()
            
            for team_id in team_ids:
                fixtures = await playhq_client.get_team_fixtures(team_id, "current_season")
                recent_fixtures = [f for f in fixtures if f.get("status") == "completed"][:3]  # Last 3 games
                
                for fixture in recent_fixtures:
                    summary = await playhq_client.get_game_summary(fixture["id"])
                    if summary:
                        fixture_players = self._extract_players_from_summary(summary, team_id)
                        players.update(fixture_players)
            
            await playhq_client.close()
            
            if not players:
                return f"No roster information available for **{team_name}**."
            
            # Filter by team if needed
            if team_id in team_ids:
                team_players = [p for p in players if self._player_belongs_to_team(p, team_id)]
            else:
                team_players = list(players)
            
            # Respect privacy mode
            if not is_private_mode():
                # Public mode: names only
                player_names = [p.get("name", "Unknown") for p in team_players]
            else:
                # Private mode: include contact info if available
                player_names = []
                for p in team_players:
                    name = p.get("name", "Unknown")
                    if p.get("email"):
                        name += f" ({p['email']})"
                    player_names.append(name)
            
            response_lines = [f"**{team_name}** roster:"]
            for player in sorted(player_names):
                response_lines.append(f"• {player}")
            
            return "\n".join(response_lines)
            
        except Exception as e:
            logger.error(f"Roster list lookup failed: {e}")
            return f"I couldn't retrieve the roster for **{team_name}**."
    
    async def _handle_unknown_intent(self, text: str, rag_results: List[str]) -> str:
        """Handle unknown intent with LLM summarization"""
        if rag_results:
            context = "\n".join(rag_results[:3])  # Use top 3 results
            try:
                return await self.llm_agent.summarise(context, text)
            except Exception as e:
                logger.warning(f"LLM summarization failed: {e}")
        
        return "I'm not sure how to help with that. Could you try asking about fixtures, ladder positions, player information, or team rosters?"
    
    # Helper methods
    def _player_in_summary(self, summary: Dict[str, Any], player_name: str) -> bool:
        """Check if player is in game summary"""
        # This would need to be implemented based on actual PlayHQ summary structure
        return player_name.lower() in str(summary).lower()
    
    def _get_team_name_from_fixture(self, fixture: Dict[str, Any], team_id: str) -> str:
        """Extract team name from fixture data"""
        # This would need to be implemented based on actual PlayHQ fixture structure
        return "Team Name"  # Placeholder
    
    def _extract_runs_from_line(self, line: str) -> str:
        """Extract runs number from text line"""
        import re
        match = re.search(r'(\d+)\s+runs?', line)
        return match.group(1) if match else "0"
    
    def _extract_player_runs_from_summary(self, summary: Dict[str, Any], player_name: str) -> int:
        """Extract player runs from game summary"""
        # This would need to be implemented based on actual PlayHQ summary structure
        return 0  # Placeholder
    
    def _extract_players_from_summary(self, summary: Dict[str, Any], team_id: str) -> List[Dict[str, Any]]:
        """Extract players from game summary"""
        # This would need to be implemented based on actual PlayHQ summary structure
        return []  # Placeholder
    
    def _player_belongs_to_team(self, player: Dict[str, Any], team_id: str) -> bool:
        """Check if player belongs to team"""
        # This would need to be implemented based on actual player data structure
        return True  # Placeholder
    
    def _format_fixture_date(self, date_str: str) -> str:
        """Format fixture date for display"""
        try:
            if not date_str:
                return "TBD"
            
            # Parse and format date
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            melbourne_tz = pytz.timezone('Australia/Melbourne')
            local_dt = dt.astimezone(melbourne_tz)
            
            return local_dt.strftime("%a %d %b %Y, %I:%M %p")
        except:
            return date_str
    
    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get response from cache"""
        if key in _cache:
            entry = _cache[key]
            if time.time() - entry["timestamp"] < _cache_ttl:
                return entry["response"]
            else:
                del _cache[key]
        return None
    
    def _cache_response(self, key: str, response: Dict[str, Any]) -> None:
        """Cache response"""
        _cache[key] = {
            "response": response,
            "timestamp": time.time()
        }
        
        # Clean old entries
        current_time = time.time()
        keys_to_remove = [k for k, v in _cache.items() if current_time - v["timestamp"] > _cache_ttl]
        for k in keys_to_remove:
            del _cache[k]

    async def _llm_driven_rag(self, text: str, team_hint: Optional[str] = None) -> str:
        """
        LLM-driven RAG approach that uses semantic search and LLM for response generation
        
        Args:
            text: User query text
            team_hint: Optional team hint for disambiguation
            
        Returns:
            Generated response based on retrieved context
        """
        try:
            # Step 1: Semantic search using vector database
            logger.info(f"Performing semantic search for: '{text}'")
            
            # Query vector store for relevant documents
            doc_ids = self.vector_client.query(text, k=6)
            logger.info(f"Vector search returned {len(doc_ids)} document IDs")
            
            # Retrieve document contents
            retrieved_docs = []
            for doc_id in doc_ids:
                doc_content = self.vector_client.get_document(doc_id)
                if doc_content:
                    retrieved_docs.append(doc_content)
            
            logger.info(f"Retrieved {len(retrieved_docs)} document contents")
            
            # Step 2: Use LLM to generate response based on retrieved context
            if retrieved_docs:
                # Combine retrieved documents as context
                context = "\n\n".join(retrieved_docs)
                
                # Create prompt for LLM
                prompt = f"""
You are a cricket assistant for Caroline Springs Cricket Club. Use the following context to answer the user's question.

Context:
{context}

User Question: {text}

Instructions:
- If the information is available in the context, provide a helpful and accurate answer
- If the information is not available, politely say you don't have that information
- Be conversational and friendly
- Focus on cricket-related information like teams, players, fixtures, ladder positions, etc.

Answer:"""
                
                # Use LLM to generate response
                response = await self.llm_agent.summarise(context, text)
                return response
            else:
                # No relevant documents found
                return "I don't have information about that. Could you try asking about fixtures, ladder positions, player information, or team rosters?"
                
        except Exception as e:
            logger.error(f"LLM-driven RAG failed: {e}")
            return "I'm sorry, I encountered an error processing your request. Please try again."

# Global router instance
_router_instance: Optional[IntentRouter] = None

def get_router() -> IntentRouter:
    """Get the global router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = IntentRouter()
    return _router_instance
