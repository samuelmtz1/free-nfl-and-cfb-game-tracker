"""
NFL API Client (BallDontLie).
Fetches and parses NFL games with rate-limiting, caching, team colors, records, and stadium weather.
"""

from typing import List, Tuple, Optional
from config import (
    BALLDONTLIE_API_KEY,
    BALLDONTLIE_GAMES_URL,
    BALLDONTLIE_MIN_INTERVAL_SECONDS,
    CACHE_TTL_LIVE_GAMES
)
from models.game import Game
from models.team_colors import get_team_color
from api.weather_service import get_venue_weather
from api.base_client import BaseClient


class NFLClient(BaseClient):
    """Client for BallDontLie NFL API."""

    def __init__(self):
        super().__init__(name="BallDontLie NFL", min_interval_seconds=BALLDONTLIE_MIN_INTERVAL_SECONDS)

    def get_games_for_date(self, target_date_str: str) -> Tuple[List[Game], bool, Optional[str]]:
        """
        Fetches NFL games for a specific date (YYYY-MM-DD).
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
            mock_games = self._get_mock_nfl_games(target_date_str)
            msg = f"{error} (Displaying Demo Data)" if error else "No API data available (Displaying Demo Data)"
            return mock_games, False, msg

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
                venue_name = item.get("venue") or "NFL Stadium"

                game = Game(
                    id=f"nfl_{item.get('id', 0)}",
                    sport="NFL",
                    home_team=home_name,
                    away_team=visitor_name,
                    home_score=home_score,
                    away_score=visitor_score,
                    home_record=home.get("record"),
                    away_record=visitor.get("record"),
                    home_color=get_team_color(home_name, "NFL"),
                    away_color=get_team_color(visitor_name, "NFL"),
                    status=status,
                    start_time=f"{start_date} {item.get('datetime', '')[:16]}".strip(),
                    period_or_quarter=period_str,
                    venue=venue_name,
                    broadcast=item.get("broadcast", "National TV"),
                    weather=get_venue_weather(venue_name),
                    is_live=is_live
                )
                games_list.append(game)

            if not games_list:
                return self._get_mock_nfl_games(target_date_str), is_cached, "No live games scheduled today (Displaying Demo Schedule)"

            return games_list, is_cached, None

        except Exception as e:
            return self._get_mock_nfl_games(target_date_str), False, f"Parser error: {str(e)} (Demo Data)"

    def _get_mock_nfl_games(self, date_str: str) -> List[Game]:
        """Provides realistic mock NFL games enriched with team colors, records, and weather."""
        return [
            Game(
                id="mock_nfl_1",
                sport="NFL",
                home_team="Kansas City Chiefs",
                away_team="Baltimore Ravens",
                home_score=27,
                away_score=20,
                home_record="11-2",
                away_record="9-4",
                home_color=get_team_color("Kansas City Chiefs", "NFL"),
                away_color=get_team_color("Baltimore Ravens", "NFL"),
                status="Final",
                start_time=f"{date_str} 8:20 PM ET",
                period_or_quarter="Final",
                venue="GEHA Field at Arrowhead Stadium",
                broadcast="NBC / Peacock",
                weather=get_venue_weather("GEHA Field at Arrowhead Stadium"),
                is_live=False
            ),
            Game(
                id="mock_nfl_2",
                sport="NFL",
                home_team="Philadelphia Eagles",
                away_team="Green Bay Packers",
                home_score=34,
                away_score=29,
                home_record="10-3",
                away_record="9-4",
                home_color=get_team_color("Philadelphia Eagles", "NFL"),
                away_color=get_team_color("Green Bay Packers", "NFL"),
                status="Final",
                start_time=f"{date_str} 8:15 PM ET",
                period_or_quarter="Final",
                venue="Corinthians Arena (São Paulo)",
                broadcast="Peacock",
                weather=get_venue_weather("Corinthians Arena"),
                is_live=False
            ),
            Game(
                id="mock_nfl_3",
                sport="NFL",
                home_team="Detroit Lions",
                away_team="Los Angeles Rams",
                home_score=17,
                away_score=13,
                home_record="11-1",
                away_record="7-6",
                home_color=get_team_color("Detroit Lions", "NFL"),
                away_color=get_team_color("Los Angeles Rams", "NFL"),
                status="Live",
                start_time=f"{date_str} 8:20 PM ET",
                period_or_quarter="Q3 6:42",
                venue="Ford Field",
                broadcast="NBC",
                weather=get_venue_weather("Ford Field"),
                is_live=True
            ),
            Game(
                id="mock_nfl_4",
                sport="NFL",
                home_team="San Francisco 49ers",
                away_team="Dallas Cowboys",
                home_score=None,
                away_score=None,
                home_record="8-5",
                away_record="7-6",
                home_color=get_team_color("San Francisco 49ers", "NFL"),
                away_color=get_team_color("Dallas Cowboys", "NFL"),
                status="Scheduled",
                start_time=f"{date_str} 8:15 PM ET",
                period_or_quarter="Pre-game",
                venue="Levi's Stadium",
                broadcast="FOX",
                weather=get_venue_weather("Levi's Stadium"),
                is_live=False
            ),
        ]
