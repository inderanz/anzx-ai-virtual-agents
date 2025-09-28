"""
Cricket Agent Prompt Templates
System prompts and formatting helpers for the cricket agent
"""

from typing import Dict, List, Any
from datetime import datetime
import pytz

# System prompt for the cricket agent
SYSTEM_PROMPT = """You are a helpful cricket assistant for Caroline Springs Cricket Club. 

Your role is to answer questions about:
- Team fixtures and schedules
- Ladder positions and standings  
- Player information and statistics
- Team rosters and lineups

Guidelines:
- Answer concisely and accurately
- Use bullet lists for multiple items
- Bold important information like team names, dates, and scores
- If information is not available, say "I don't have that information"
- For dates, use Australian timezone (AET/AEDT)
- Be helpful but don't make up information

Format examples:
- Fixtures: "• **Sat 12 Oct 2025, 9:00 AM** – vs Melbourne CC – Home Ground – scheduled"
- Ladder: "**Caroline Springs Blue U10** is in **2nd** position (as of 15 Oct 2025)"
- Player stats: "**John Smith** scored **45** runs in their last match"
- Roster: "• John Smith\n• Sarah Jones\n• Mike Wilson"

Always be respectful and professional in your responses."""

def format_response(answer: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the final response with answer and metadata
    
    Args:
        answer: The formatted answer text
        meta: Response metadata
        
    Returns:
        Formatted response dictionary
    """
    return {
        "answer": answer,
        "meta": meta
    }

def format_fixture_date(date_str: str) -> str:
    """
    Format fixture date for display in Australian timezone
    
    Args:
        date_str: ISO date string
        
    Returns:
        Formatted date string
    """
    try:
        if not date_str:
            return "TBD"
        
        # Parse date and convert to Melbourne timezone
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        melbourne_tz = pytz.timezone('Australia/Melbourne')
        local_dt = dt.astimezone(melbourne_tz)
        
        return local_dt.strftime("%a %d %b %Y, %I:%M %p")
    except Exception:
        return date_str

def format_ladder_entry(entry: Dict[str, Any]) -> str:
    """
    Format ladder entry for display
    
    Args:
        entry: Ladder entry data
        
    Returns:
        Formatted ladder entry string
    """
    position = entry.get("position", "N/A")
    team_name = entry.get("team_name", "Unknown")
    points = entry.get("points", 0)
    played = entry.get("matches_played", 0)
    won = entry.get("matches_won", 0)
    lost = entry.get("matches_lost", 0)
    
    return f"**{position}.** {team_name} - {points} pts ({played} played, {won} won, {lost} lost)"

def format_player_stats(player: Dict[str, Any]) -> str:
    """
    Format player statistics for display
    
    Args:
        player: Player data with stats
        
    Returns:
        Formatted player stats string
    """
    name = player.get("name", "Unknown")
    runs = player.get("runs", 0)
    balls = player.get("balls", 0)
    
    return f"**{name}**: {runs} runs ({balls} balls)"

def format_roster_entry(player: Dict[str, Any], include_contact: bool = False) -> str:
    """
    Format roster entry for display
    
    Args:
        player: Player data
        include_contact: Whether to include contact information
        
    Returns:
        Formatted roster entry string
    """
    name = player.get("name", "Unknown")
    
    if include_contact and player.get("email"):
        return f"• {name} ({player['email']})"
    else:
        return f"• {name}"

def get_current_timestamp() -> str:
    """
    Get current timestamp in Australian timezone
    
    Returns:
        Formatted timestamp string
    """
    melbourne_tz = pytz.timezone('Australia/Melbourne')
    now = datetime.now(melbourne_tz)
    return now.strftime("%d %b %Y")

def bold_text(text: str) -> str:
    """
    Wrap text in bold formatting
    
    Args:
        text: Text to bold
        
    Returns:
        Bold formatted text
    """
    return f"**{text}**"

def create_bullet_list(items: List[str]) -> str:
    """
    Create a bullet list from items
    
    Args:
        items: List of items
        
    Returns:
        Formatted bullet list string
    """
    return "\n".join(f"• {item}" for item in items)

def format_team_name(team_name: str) -> str:
    """
    Format team name consistently
    
    Args:
        team_name: Raw team name
        
    Returns:
        Formatted team name
    """
    return bold_text(team_name)

def format_score(home_score: int, away_score: int, home_team: str, away_team: str) -> str:
    """
    Format match score for display
    
    Args:
        home_score: Home team score
        away_score: Away team score
        home_team: Home team name
        away_team: Away team name
        
    Returns:
        Formatted score string
    """
    return f"{bold_text(home_team)} {home_score} - {away_score} {bold_text(away_team)}"

def format_fixture_summary(fixture: Dict[str, Any]) -> str:
    """
    Format fixture summary for display
    
    Args:
        fixture: Fixture data
        
    Returns:
        Formatted fixture summary string
    """
    date_str = format_fixture_date(fixture.get("date", ""))
    home_team = bold_text(fixture.get("home_team", "TBD"))
    away_team = bold_text(fixture.get("away_team", "TBD"))
    venue = fixture.get("venue", "TBD")
    status = fixture.get("status", "scheduled")
    
    return f"• {date_str} – {home_team} vs {away_team} – {venue} – {status}"

def format_ladder_position(position: int, team_name: str, points: int, played: int, won: int, lost: int) -> str:
    """
    Format ladder position for display
    
    Args:
        position: Ladder position
        team_name: Team name
        points: Points
        played: Matches played
        won: Matches won
        lost: Matches lost
        
    Returns:
        Formatted ladder position string
    """
    current_date = get_current_timestamp()
    
    return f"{bold_text(team_name)} is in {bold_text(f'{position}')} position on the ladder (as of {current_date}):\n• Points: {points}\n• Played: {played}\n• Won: {won}\n• Lost: {lost}"

def format_player_runs(player_name: str, runs: int) -> str:
    """
    Format player runs for display
    
    Args:
        player_name: Player name
        runs: Number of runs
        
    Returns:
        Formatted player runs string
    """
    return f"{bold_text(player_name)} scored {bold_text(str(runs))} runs in their last match"

def format_team_roster(team_name: str, players: List[Dict[str, Any]], include_contact: bool = False) -> str:
    """
    Format team roster for display
    
    Args:
        team_name: Team name
        players: List of player data
        include_contact: Whether to include contact information
        
    Returns:
        Formatted roster string
    """
    if not players:
        return f"No roster information available for {bold_text(team_name)}"
    
    roster_lines = [f"{bold_text(team_name)} roster:"]
    
    for player in sorted(players, key=lambda x: x.get("name", "")):
        roster_lines.append(format_roster_entry(player, include_contact))
    
    return "\n".join(roster_lines)

def format_fixtures_list(team_name: str, fixtures: List[Dict[str, Any]]) -> str:
    """
    Format fixtures list for display
    
    Args:
        team_name: Team name
        fixtures: List of fixture data
        
    Returns:
        Formatted fixtures list string
    """
    if not fixtures:
        return f"No fixtures found for {bold_text(team_name)}"
    
    fixture_lines = [f"{bold_text(team_name)} fixtures:"]
    
    for fixture in fixtures[:10]:  # Limit to 10 fixtures
        fixture_lines.append(format_fixture_summary(fixture))
    
    return "\n".join(fixture_lines)

def format_next_fixture(team_name: str, fixture: Dict[str, Any]) -> str:
    """
    Format next fixture for display
    
    Args:
        team_name: Team name
        fixture: Fixture data
        
    Returns:
        Formatted next fixture string
    """
    date_str = format_fixture_date(fixture.get("date", ""))
    opponent = fixture.get("opponent", "TBD")
    venue = fixture.get("venue", "TBD")
    
    return f"{bold_text(team_name)}'s next fixture:\n• {date_str} – vs {opponent}\n• Venue: {venue}"

def format_error_message(error_type: str, details: str = "") -> str:
    """
    Format error message for display
    
    Args:
        error_type: Type of error
        details: Additional error details
        
    Returns:
        Formatted error message string
    """
    if error_type == "not_found":
        return f"I don't have that information. {details}"
    elif error_type == "no_data":
        return f"I don't have that in public data. {details}"
    elif error_type == "error":
        return f"I'm sorry, I encountered an error. {details}"
    else:
        return f"I'm not sure how to help with that. {details}"
