"""
Unified Game Data Model.
Standardizes football game data across both NFL and College Football APIs with branding, records, and weather.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Game:
    """
    Represents a single football game (NFL or CFB).
    """
    id: str
    sport: str
    home_team: str
    away_team: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    home_record: Optional[str] = None
    away_record: Optional[str] = None
    home_rank: Optional[str] = None
    away_rank: Optional[str] = None
    status: str = "Scheduled"
    start_time: str = ""
    period_or_quarter: str = ""
    venue: str = ""
    broadcast: str = ""
    weather: Optional[str] = None
    home_color: Optional[str] = None
    away_color: Optional[str] = None
    is_live: bool = False

    @property
    def matchup_title(self) -> str:
        """Returns a formatted matchup title, e.g. 'Chiefs @ 49ers'."""
        away_prefix = f"{self.away_rank} " if self.away_rank else ""
        home_prefix = f"{self.home_rank} " if self.home_rank else ""
        return f"{away_prefix}{self.away_team} @ {home_prefix}{self.home_team}"

    @property
    def score_display(self) -> str:
        """Returns a clean score string or 'vs' if unplayed."""
        if self.home_score is not None and self.away_score is not None:
            return f"{self.away_score} - {self.home_score}"
        return "vs"
