"""
NFL API Client (BallDontLie).
Fetches and parses NFL games with rate-limiting, caching, and demo fallback.
"""

from datetime import datetime
from typing import List, Tuple, Optional
from config import (
    BALLDONTLIE_API_KEY,
    BALLDONTLIE_GAMES_URL,
    BALLDONTLIE_MIN_INTERVAL_SECONDS,
    CACHE_TTL_LIVE_GAMES,
    CACHE_TTL_STATIC_GAMES
)
from models.game import Game
from api.base_client import BaseClient


class NFLClient(BaseClient):
    """Client for BallDontLie NFL API."""

    def __init__(self):
        super().__init__(name="BallDontLie NFL", min_interval_seconds=BALLDONTLIE_MIN_INTERVAL_SECONDS)

    def get_games_for_date(self, target_date_str: str) -> Tuple[List[Game], bool, Optional[str]]:
        """
        Fetches NFL games for a specific date (YYYY-MM-DD).
        
        Returns:
            (games_list, is_cached, message)
        """
        # If no API key is provided, return rich mock data
        if not BALLDONTLIE_API_KEY or BALLDONTLIE_API_KEY == "your_balldontlie_api_key_here":
            return self._get_mock_nfl_games(target_date_str), True, "Demo Mode: Add BALLDONTLIE_API_KEY in .env for live data"

        cache_key = f"nfl_games_{target_date_str}"
        headers = {
            "Authorization": BALLDONTLIE_API_KEY
        }
        params = {
            "dates[]": target_date_str
        }

        raw_data, is_cached, error = self.fetch_with_cache(
            url=BALLDONTLIE_GAMES_URL,
            headers=headers,
            params=params,
            cache_key=cache_key,
            ttl_seconds=CACHE_TTL_LIVE_GAMES
        )

        if error or not raw_data:
            # Fallback to mock data on error so UI never crashes
            mock_games = self._get_mock_nfl_games(target_date_str)
            msg = f"{error} (Displaying Demo Data)" if error else "No API data available (Displaying Demo Data)"
            return mock_games, False, msg

        # Parse API response
        games_list = []
        try:
            items = raw_data.get("data", [])
            for item in items:
                home = item.get("home_team", {})
                visitor = item.get("visitor_team", {})
                status_raw = str(item.get("status", "Scheduled"))
                home_score = item.get("home_team_score")
                visitor_score = item.get("visitor_team_score")
                period = item.get("period", 0)
                clock = item.get("time", "")

                is_live = "progress" in status_raw.lower() or (period > 0 and "final" not in status_raw.lower())

                if "final" in status_raw.lower():
                    status = "Final"
                    period_str = "Final"
                elif is_live:
                    status = "Live"
                    period_str = f"Q{period} {clock}".strip()
                else:
                    status = "Scheduled"
                    period_str = "Pre-game"

                home_name = home.get("full_name") or home.get("name") or "Home Team"
                visitor_name = visitor.get("full_name") or visitor.get("name") or "Away Team"
                start_date = item.get("date", target_date_str)

                game = Game(
                    id=f"nfl_{item.get('id', 0)}",
                    sport="NFL",
                    home_team=home_name,
                    away_team=visitor_name,
                    home_score=home_score,
                    away_score=visitor_score,
                    status=status,
                    start_time=f"{start_date} {item.get('datetime', '')[:16]}".strip(),
                    period_or_quarter=period_str,
                    venue=item.get("venue", "NFL Stadium"),
                    broadcast=item.get("broadcast", "National TV"),
                    is_live=is_live
                )
                games_list.append(game)

            if not games_list:
                # If API returned 0 games (e.g. offseason or Tuesday with no games), provide demo view
                return self._get_mock_nfl_games(target_date_str), is_cached, "No live games scheduled today (Displaying Demo Schedule)"

            return games_list, is_cached, None

        except Exception as e:
            return self._get_mock_nfl_games(target_date_str), False, f"Parser error: {str(e)} (Demo Data)"

    def _get_mock_nfl_games(self, date_str: str) -> List[Game]:
        """Provides realistic mock NFL games for demonstration and testing."""
        return [
            Game(
                id="mock_nfl_1",
                sport="NFL",
                home_team="Kansas City Chiefs",
                away_team="Baltimore Ravens",
                home_score=27,
                away_score=20,
                status="Final",
                start_time=f"{date_str} 8:20 PM ET",
                period_or_quarter="Final",
                venue="GEHA Field at Arrowhead Stadium",
                broadcast="NBC / Peacock",
                is_live=False
            ),
            Game(
                id="mock_nfl_2",
                sport="NFL",
                home_team="Philadelphia Eagles",
                away_team="Green Bay Packers",
                home_score=34,
                away_score=29,
                status="Final",
                start_time=f"{date_str} 8:15 PM ET",
                period_or_quarter="Final",
                venue="Corinthians Arena (São Paulo)",
                broadcast="Peacock",
                is_live=False
            ),
            Game(
                id="mock_nfl_3",
                sport="NFL",
                home_team="Detroit Lions",
                away_team="Los Angeles Rams",
                home_score=17,
                away_score=13,
                status="Live",
                start_time=f"{date_str} 8:20 PM ET",
                period_or_quarter="Q3 6:42",
                venue="Ford Field",
                broadcast="NBC",
                is_live=True
            ),
            Game(
                id="mock_nfl_4",
                sport="NFL",
                home_team="San Francisco 49ers",
                away_team="New York Jets",
                home_score=None,
                away_score=None,
                status="Scheduled",
                start_time=f"{date_str} 8:15 PM ET",
                period_or_quarter="Pre-game",
                venue="Levi's Stadium",
                broadcast="ESPN / ABC",
                is_live=False
            ),
        ]
