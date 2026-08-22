"""
College Football (CFB) API Client (CollegeFootballData.com).
Fetches and parses NCAA Football games with rate-limiting, caching, and demo fallback.
"""

from typing import List, Tuple, Optional
from config import (
    CFBD_API_KEY,
    CFBD_SCOREBOARD_URL,
    CFBD_MIN_INTERVAL_SECONDS,
    CACHE_TTL_LIVE_GAMES,
    CACHE_TTL_STATIC_GAMES
)
from models.game import Game
from api.base_client import BaseClient


class CFBClient(BaseClient):
    """Client for CollegeFootballData.com API."""

    def __init__(self):
        super().__init__(name="CollegeFootballData", min_interval_seconds=CFBD_MIN_INTERVAL_SECONDS)

    def get_games_for_date(self, target_date_str: str) -> Tuple[List[Game], bool, Optional[str]]:
        """
        Fetches College Football games for today/specified date.
        
        Returns:
            (games_list, is_cached, message)
        """
        # If no API key is provided, return rich mock data
        if not CFBD_API_KEY or CFBD_API_KEY == "your_cfbd_api_key_here":
            return self._get_mock_cfb_games(target_date_str), True, "Demo Mode: Add CFBD_API_KEY in .env for live data"

        cache_key = f"cfb_scoreboard_{target_date_str}"
        headers = {
            "Authorization": f"Bearer {CFBD_API_KEY}"
        }
        params = {}

        raw_data, is_cached, error = self.fetch_with_cache(
            url=CFBD_SCOREBOARD_URL,
            headers=headers,
            params=params,
            cache_key=cache_key,
            ttl_seconds=CACHE_TTL_LIVE_GAMES
        )

        if error or not raw_data:
            mock_games = self._get_mock_cfb_games(target_date_str)
            msg = f"{error} (Displaying Demo Data)" if error else "No API data available (Displaying Demo Data)"
            return mock_games, False, msg

        games_list = []
        try:
            items = raw_data if isinstance(raw_data, list) else []
            for item in items:
                home = item.get("homeTeam", {})
                away = item.get("awayTeam", {})
                status_raw = str(item.get("status", "scheduled")).lower()
                period = item.get("period", 0)
                clock = item.get("clock", "")

                is_live = "in_progress" in status_raw or (period > 0 and "completed" not in status_raw)

                if "completed" in status_raw or "final" in status_raw:
                    status = "Final"
                    period_str = "Final"
                elif is_live:
                    status = "Live"
                    period_str = f"Q{period} {clock}".strip()
                else:
                    status = "Scheduled"
                    period_str = "Pre-game"

                home_rank = f"#{home.get('ranking')} " if home.get("ranking") else ""
                away_rank = f"#{away.get('ranking')} " if away.get("ranking") else ""

                home_name = f"{home_rank}{home.get('name', 'Home Team')}"
                away_name = f"{away_rank}{away.get('name', 'Away Team')}"

                venue_info = item.get("venue", {})
                venue_name = venue_info.get("name", "College Stadium") if isinstance(venue_info, dict) else str(venue_info)
                start_date = item.get("startDate", target_date_str)

                game = Game(
                    id=f"cfb_{item.get('id', 0)}",
                    sport="CFB",
                    home_team=home_name,
                    away_team=away_name,
                    home_score=home.get("points"),
                    away_score=away.get("points"),
                    status=status,
                    start_time=start_date[:16].replace("T", " "),
                    period_or_quarter=period_str,
                    venue=venue_name,
                    broadcast=item.get("tv", "ESPN"),
                    is_live=is_live
                )
                games_list.append(game)

            if not games_list:
                return self._get_mock_cfb_games(target_date_str), is_cached, "No live games on schedule today (Displaying Demo Schedule)"

            return games_list, is_cached, None

        except Exception as e:
            return self._get_mock_cfb_games(target_date_str), False, f"Parser error: {str(e)} (Demo Data)"

    def _get_mock_cfb_games(self, date_str: str) -> List[Game]:
        """Provides realistic mock CFB games for demonstration and testing."""
        return [
            Game(
                id="mock_cfb_1",
                sport="CFB",
                home_team="#1 Georgia",
                away_team="#14 Clemson",
                home_score=34,
                away_score=3,
                status="Final",
                start_time=f"{date_str} 12:00 PM ET",
                period_or_quarter="Final",
                venue="Mercedes-Benz Stadium (Atlanta)",
                broadcast="ABC",
                is_live=False
            ),
            Game(
                id="mock_cfb_2",
                sport="CFB",
                home_team="#7 Notre Dame",
                away_team="#20 Texas A&M",
                home_score=13,
                away_score=23,
                status="Final",
                start_time=f"{date_str} 7:30 PM ET",
                period_or_quarter="Final",
                venue="Kyle Field (College Station)",
                broadcast="ABC",
                is_live=False
            ),
            Game(
                id="mock_cfb_3",
                sport="CFB",
                home_team="#2 Ohio State",
                away_team="#3 Texas",
                home_score=21,
                away_score=24,
                status="Live",
                start_time=f"{date_str} 8:00 PM ET",
                period_or_quarter="Q4 3:12",
                venue="Ohio Stadium (Columbus)",
                broadcast="FOX",
                is_live=True
            ),
            Game(
                id="mock_cfb_4",
                sport="CFB",
                home_team="#5 Alabama",
                away_team="#8 LSU",
                home_score=None,
                away_score=None,
                status="Scheduled",
                start_time=f"{date_str} 7:30 PM ET",
                period_or_quarter="Pre-game",
                venue="Bryant-Denny Stadium",
                broadcast="ESPN",
                is_live=False
            ),
        ]
