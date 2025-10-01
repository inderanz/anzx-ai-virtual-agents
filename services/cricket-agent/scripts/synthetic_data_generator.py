#!/usr/bin/env python3
"""
Synthetic Cricket Data Generator
Creates realistic cricket data based on PlayHQ API structure for testing
"""

import asyncio
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

from app.config import get_settings
from agent.tools.vector_client import get_vector_client
from agent.tools.normalize import CricketDataNormalizer, CricketSnippetGenerator
from models.fixture import Fixture, MatchStatus
from models.ladder import Ladder, LadderEntry
from models.team import Team, Player
from models.roster import Roster
from models.scorecard import Scorecard, TeamScorecard, BattingStats, BowlingStats

logger = logging.getLogger(__name__)

class SyntheticCricketDataGenerator:
    """Generates realistic synthetic cricket data for testing"""
    
    def __init__(self):
        self.settings = get_settings()
        self.vector_client = get_vector_client()
        self.normalizer = CricketDataNormalizer()
        self.snippet_generator = CricketSnippetGenerator()
        
        # Synthetic data configuration
        self.org_id = "synthetic-org-123"
        self.season_id = "synthetic-season-2025"
        self.grade_id = "synthetic-grade-u10"
        
        # Team configurations
        self.teams = [
            {"id": "team-blue-u10", "name": "Caroline Springs Blue U10", "color": "blue"},
            {"id": "team-white-u10", "name": "Caroline Springs White U10", "color": "white"},
            {"id": "team-gold-u10", "name": "Caroline Springs Gold U10", "color": "gold"},
            {"id": "opponent-1", "name": "Melbourne Cricket Club U10", "color": "red"},
            {"id": "opponent-2", "name": "Richmond Tigers U10", "color": "yellow"},
            {"id": "opponent-3", "name": "Hawthorn Hawks U10", "color": "brown"},
            {"id": "opponent-4", "name": "Collingwood Magpies U10", "color": "black"},
            {"id": "opponent-5", "name": "Essendon Bombers U10", "color": "red"},
        ]
        
        # Player names for synthetic data
        self.player_names = [
            "Harshvarshan", "Arjun", "Krishna", "Rohan", "Vikram", "Surya", "Aditya", "Ravi",
            "Kiran", "Suresh", "Rajesh", "Prakash", "Manoj", "Deepak", "Sunil", "Amit",
            "Rahul", "Vishal", "Nikhil", "Sandeep", "Ankit", "Rohit", "Karan", "Vivek",
            "Aryan", "Kartik", "Rishabh", "Yash", "Dhruv", "Arnav", "Kabir", "Ishaan"
        ]
        
        # Venues for matches
        self.venues = [
            "Caroline Springs Cricket Ground",
            "Melbourne Cricket Ground",
            "Richmond Cricket Club",
            "Hawthorn Cricket Ground",
            "Collingwood Oval",
            "Essendon Cricket Club",
            "Flemington Cricket Ground",
            "Kensington Cricket Club"
        ]
    
    def generate_team_data(self) -> List[Dict[str, Any]]:
        """Generate synthetic team data"""
        teams_data = []
        
        for team in self.teams:
            # Generate players for each team
            players = []
            num_players = random.randint(12, 16)
            
            for i in range(num_players):
                player = {
                    "id": f"player-{team['id']}-{i+1}",
                    "name": random.choice(self.player_names),
                    "position": random.choice(["Batsman", "Bowler", "All-rounder", "Wicket-keeper"]),
                    "jerseyNumber": i + 1,
                    "isCaptain": i == 0,
                    "isViceCaptain": i == 1,
                    "isWicketKeeper": random.choice([True, False]),
                    "age": random.randint(8, 11),
                    "battingStyle": random.choice(["Right-handed", "Left-handed"]),
                    "bowlingStyle": random.choice(["Right-arm fast", "Left-arm fast", "Right-arm spin", "Left-arm spin"])
                }
                players.append(player)
            
            team_data = {
                "id": team["id"],
                "name": team["name"],
                "grade": "U10",
                "season": "2025/26",
                "players": players,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            teams_data.append(team_data)
        
        return teams_data
    
    def generate_fixture_data(self) -> List[Dict[str, Any]]:
        """Generate synthetic fixture data"""
        fixtures = []
        start_date = datetime.now() - timedelta(days=30)
        
        # Generate fixtures for the next 3 months
        for week in range(12):
            match_date = start_date + timedelta(weeks=week)
            
            # Generate 2-3 matches per week
            num_matches = random.randint(2, 3)
            for match_num in range(num_matches):
                # Select random teams
                home_team = random.choice(self.teams)
                away_team = random.choice([t for t in self.teams if t["id"] != home_team["id"]])
                
                # Random match time
                match_time = match_date.replace(
                    hour=random.randint(9, 15),
                    minute=random.choice([0, 30])
                )
                
                # Random venue
                venue = random.choice(self.venues)
                
                # Random status
                status = random.choice(["scheduled", "in_progress", "completed", "cancelled"])
                
                fixture = {
                    "id": f"fixture-{week}-{match_num}",
                    "homeTeam": {
                        "id": home_team["id"],
                        "name": home_team["name"]
                    },
                    "awayTeam": {
                        "id": away_team["id"],
                        "name": away_team["name"]
                    },
                    "date": match_time.isoformat(),
                    "venue": venue,
                    "grade": "U10",
                    "status": status,
                    "result": None
                }
                
                # Add result if completed
                if status == "completed":
                    home_score = random.randint(80, 150)
                    away_score = random.randint(80, 150)
                    if home_score > away_score:
                        fixture["result"] = f"{home_team['name']} won by {home_score - away_score} runs"
                    elif away_score > home_score:
                        fixture["result"] = f"{away_team['name']} won by {away_score - home_score} runs"
                    else:
                        fixture["result"] = "Match tied"
                
                fixtures.append(fixture)
        
        return fixtures
    
    def generate_ladder_data(self) -> List[Dict[str, Any]]:
        """Generate synthetic ladder data"""
        ladder_entries = []
        
        for i, team in enumerate(self.teams):
            matches_played = random.randint(5, 10)
            matches_won = random.randint(0, matches_played)
            matches_lost = matches_played - matches_won
            matches_drawn = random.randint(0, 2)
            matches_tied = random.randint(0, 1)
            
            # Calculate points (2 for win, 1 for draw/tie)
            points = (matches_won * 2) + (matches_drawn * 1) + (matches_tied * 1)
            
            # Calculate percentage
            percentage = (points / (matches_played * 2)) * 100 if matches_played > 0 else 0
            
            entry = {
                "position": i + 1,
                "team": {
                    "id": team["id"],
                    "name": team["name"]
                },
                "matchesPlayed": matches_played,
                "matchesWon": matches_won,
                "matchesLost": matches_lost,
                "matchesDrawn": matches_drawn,
                "matchesTied": matches_tied,
                "points": points,
                "percentage": round(percentage, 2)
            }
            ladder_entries.append(entry)
        
        # Sort by points (descending)
        ladder_entries.sort(key=lambda x: x["points"], reverse=True)
        
        # Update positions
        for i, entry in enumerate(ladder_entries):
            entry["position"] = i + 1
        
        return ladder_entries
    
    def generate_scorecard_data(self) -> List[Dict[str, Any]]:
        """Generate synthetic scorecard data"""
        scorecards = []
        
        # Generate scorecards for completed matches
        completed_fixtures = [f for f in self.generate_fixture_data() if f["status"] == "completed"]
        
        for fixture in completed_fixtures[:5]:  # Limit to 5 recent matches
            home_team = fixture["homeTeam"]
            away_team = fixture["awayTeam"]
            
            # Generate batting stats for home team
            home_batting = []
            for i in range(random.randint(6, 10)):
                runs = random.randint(0, 50)
                balls = random.randint(0, 30)
                player = {
                    "playerName": random.choice(self.player_names),
                    "runs": runs,
                    "balls": balls,
                    "fours": runs // 4,
                    "sixes": runs // 6,
                    "strikeRate": round((runs / balls) * 100, 2) if balls > 0 else 0,
                    "out": random.choice([True, False])
                }
                home_batting.append(player)
            
            # Generate batting stats for away team
            away_batting = []
            for i in range(random.randint(6, 10)):
                runs = random.randint(0, 50)
                balls = random.randint(0, 30)
                player = {
                    "playerName": random.choice(self.player_names),
                    "runs": runs,
                    "balls": balls,
                    "fours": runs // 4,
                    "sixes": runs // 6,
                    "strikeRate": round((runs / balls) * 100, 2) if balls > 0 else 0,
                    "out": random.choice([True, False])
                }
                away_batting.append(player)
            
            # Generate bowling stats
            home_bowling = []
            for i in range(random.randint(4, 6)):
                overs = random.randint(1, 4)
                wickets = random.randint(0, 3)
                runs_conceded = random.randint(10, 40)
                player = {
                    "playerName": random.choice(self.player_names),
                    "overs": overs,
                    "maidens": random.randint(0, 2),
                    "runs": runs_conceded,
                    "wickets": wickets,
                    "economy": round(runs_conceded / overs, 2) if overs > 0 else 0
                }
                home_bowling.append(player)
            
            away_bowling = []
            for i in range(random.randint(4, 6)):
                overs = random.randint(1, 4)
                wickets = random.randint(0, 3)
                runs_conceded = random.randint(10, 40)
                player = {
                    "playerName": random.choice(self.player_names),
                    "overs": overs,
                    "maidens": random.randint(0, 2),
                    "runs": runs_conceded,
                    "wickets": wickets,
                    "economy": round(runs_conceded / overs, 2) if overs > 0 else 0
                }
                away_bowling.append(player)
            
            # Calculate team totals
            home_total = sum(player["runs"] for player in home_batting)
            away_total = sum(player["runs"] for player in away_batting)
            
            scorecard = {
                "id": f"scorecard-{fixture['id']}",
                "matchId": fixture["id"],
                "homeTeam": {
                    "id": home_team["id"],
                    "name": home_team["name"],
                    "score": home_total,
                    "wickets": random.randint(6, 10),
                    "overs": random.randint(15, 20),
                    "extras": random.randint(5, 15),
                    "batting": home_batting,
                    "bowling": home_bowling
                },
                "awayTeam": {
                    "id": away_team["id"],
                    "name": away_team["name"],
                    "score": away_total,
                    "wickets": random.randint(6, 10),
                    "overs": random.randint(15, 20),
                    "extras": random.randint(5, 15),
                    "batting": away_batting,
                    "bowling": away_bowling
                },
                "date": fixture["date"],
                "venue": fixture["venue"],
                "result": fixture["result"],
                "status": "completed"
            }
            scorecards.append(scorecard)
        
        return scorecards
    
    async def generate_and_store_synthetic_data(self) -> Dict[str, Any]:
        """Generate and store all synthetic cricket data"""
        logger.info("Starting synthetic cricket data generation")
        
        try:
            # Generate all data types
            teams_data = self.generate_team_data()
            fixtures_data = self.generate_fixture_data()
            ladder_data = self.generate_ladder_data()
            scorecards_data = self.generate_scorecard_data()
            
            # Process and store data
            stats = {
                "teams_processed": 0,
                "fixtures_processed": 0,
                "ladders_processed": 0,
                "scorecards_processed": 0,
                "vector_upserts": 0,
                "errors": 0
            }
            
            # Process teams
            for team_data in teams_data:
                try:
                    # Normalize team data
                    normalized_team = self.normalizer.normalize_team(
                        team_data, 
                        {"id": self.grade_id, "name": "U10"}, 
                        {"id": self.season_id, "name": "2025/26"}
                    )
                    
                    if normalized_team:
                        # Generate snippet
                        snippet = self.snippet_generator.generate_team_snippet(normalized_team)
                        
                        # Prepare document for vector store
                        doc = {
                            "id": f"team-{normalized_team.id}",
                            "text": snippet,
                            "metadata": {
                                "team_id": normalized_team.id,
                                "season_id": self.season_id,
                                "grade_id": self.grade_id,
                                "type": "team",
                                "date": datetime.utcnow().isoformat()
                            }
                        }
                        
                        # Upsert to vector store
                        self.vector_client.upsert([doc])
                        stats["vector_upserts"] += 1
                        stats["teams_processed"] += 1
                        
                except Exception as e:
                    logger.error(f"Failed to process team {team_data.get('name', 'unknown')}: {e}")
                    stats["errors"] += 1
            
            # Process fixtures
            for fixture_data in fixtures_data:
                try:
                    # Normalize fixture data
                    normalized_fixture = self.normalizer.normalize_fixture(
                        fixture_data, 
                        fixture_data.get("homeTeam", {}).get("id", "")
                    )
                    
                    if normalized_fixture:
                        # Generate snippet
                        snippet = self.snippet_generator.generate_fixture_snippet(normalized_fixture)
                        
                        # Prepare document for vector store
                        doc = {
                            "id": f"fixture-{normalized_fixture.id}",
                            "text": snippet,
                            "metadata": {
                                "team_id": fixture_data.get("homeTeam", {}).get("id", ""),
                                "season_id": self.season_id,
                                "grade_id": self.grade_id,
                                "type": "fixture",
                                "date": normalized_fixture.date.isoformat() if normalized_fixture.date else datetime.utcnow().isoformat()
                            }
                        }
                        
                        # Upsert to vector store
                        self.vector_client.upsert([doc])
                        stats["vector_upserts"] += 1
                        stats["fixtures_processed"] += 1
                        
                except Exception as e:
                    logger.error(f"Failed to process fixture {fixture_data.get('id', 'unknown')}: {e}")
                    stats["errors"] += 1
            
            # Process ladder
            try:
                # Normalize ladder data
                normalized_ladder = self.normalizer.normalize_ladder(
                    ladder_data, 
                    {"id": self.grade_id, "name": "U10"}
                )
                
                if normalized_ladder:
                    # Generate snippet
                    snippet = self.snippet_generator.generate_ladder_snippet(normalized_ladder)
                    
                    # Prepare document for vector store
                    doc = {
                        "id": f"ladder-{self.grade_id}",
                        "text": snippet,
                        "metadata": {
                            "team_id": None,
                            "season_id": self.season_id,
                            "grade_id": self.grade_id,
                            "type": "ladder",
                            "date": datetime.utcnow().isoformat()
                        }
                    }
                    
                    # Upsert to vector store
                    self.vector_client.upsert([doc])
                    stats["vector_upserts"] += 1
                    stats["ladders_processed"] += 1
                    
            except Exception as e:
                logger.error(f"Failed to process ladder: {e}")
                stats["errors"] += 1
            
            # Process scorecards
            for scorecard_data in scorecards_data:
                try:
                    # Normalize scorecard data
                    normalized_scorecard = self.normalizer.normalize_scorecard(
                        scorecard_data, 
                        {"id": scorecard_data["matchId"]}
                    )
                    
                    if normalized_scorecard:
                        # Generate snippet
                        snippet = self.snippet_generator.generate_scorecard_snippet(normalized_scorecard)
                        
                        # Prepare document for vector store
                        doc = {
                            "id": f"scorecard-{normalized_scorecard.id}",
                            "text": snippet,
                            "metadata": {
                                "team_id": None,
                                "season_id": self.season_id,
                                "grade_id": self.grade_id,
                                "type": "scorecard",
                                "date": normalized_scorecard.date.isoformat() if normalized_scorecard.date else datetime.utcnow().isoformat()
                            }
                        }
                        
                        # Upsert to vector store
                        self.vector_client.upsert([doc])
                        stats["vector_upserts"] += 1
                        stats["scorecards_processed"] += 1
                        
                except Exception as e:
                    logger.error(f"Failed to process scorecard {scorecard_data.get('id', 'unknown')}: {e}")
                    stats["errors"] += 1
            
            logger.info(f"Synthetic data generation completed: {stats}")
            return {
                "status": "success",
                "stats": stats,
                "generated_data": {
                    "teams": len(teams_data),
                    "fixtures": len(fixtures_data),
                    "ladder_entries": len(ladder_data),
                    "scorecards": len(scorecards_data)
                }
            }
            
        except Exception as e:
            logger.error(f"Synthetic data generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

async def main():
    """Main function to run synthetic data generation"""
    generator = SyntheticCricketDataGenerator()
    result = await generator.generate_and_store_synthetic_data()
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
