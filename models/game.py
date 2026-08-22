"""
Unified Game Data Model.
Standardizes football game data across both NFL and College Football APIs.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Game:
    """
    Represents a single football game (NFL or CFB).
    
    Attributes:
        id: Unique identifier for the game.
        sport: League name ('NFL' or 'CFB').
        home_team: Name of the home team.
        away_team: Name of the away team.
        home_score: Current or final score of home team (None if not started).
        away_score: Current or final score of away team (None if not started).
        status: Game status ('Scheduled', 'Live', 'Final', 'Postponed').
        start_time: Human-readable scheduled start time (e.g. '8:15 PM ET' or '2026-09-06 20:15').
        period_or_quarter: Current quarter/period info (e.g. 'Q2 4:15', 'Halftime', or 'Final').
        venue: Stadium or location name.
        broadcast: TV channel or streaming platform (e.g. 'ESPN', 'FOX', 'NBC').
        is_live: True if game is currently in progress.
    """
    id: str
    sport: str
    home_team: str
    away_team: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: str = "Scheduled"
    start_time: str = ""
    period_or_quarter: str = ""
    venue: str = ""
    broadcast: str = ""
    is_live: bool = False

    @property
    def matchup_title(self) -> str:
        """Returns a formatted matchup title, e.g. 'Chiefs @ 49ers'."""
        return f"{self.away_team} @ {self.home_team}"

    @property
    def score_display(self) -> str:
        """Returns a clean score string or 'vs' if unplayed."""
        if self.home_score is not None and self.away_score is not None:
            return f"{self.away_score} - {self.home_score}"
        return "vs"
