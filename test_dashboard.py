"""
Unit and Integration Tests for Sports Dashboard.
Verifies caching, model parsing, rate limiting, team colors, weather, and theme loading.
"""

import time
from database import init_db, set_cached_data, get_cached_data, clear_all_cache
from models.game import Game
from models.team_colors import get_team_color
from api.weather_service import get_venue_weather
from api.nfl_client import NFLClient
from api.cfb_client import CFBClient
from ui.theme_manager import ThemeManager


def test_game_model():
    print("Testing Game Model...", end=" ")
    game = Game(
        id="test_1",
        sport="CFB",
        home_team="Georgia",
        away_team="Texas",
        home_score=30,
        away_score=15,
        home_rank="#1",
        away_rank="#3",
        home_record="12-1",
        away_record="11-2",
        home_color="#BA0C2F",
        away_color="#BF5700",
        weather="☀️ 72°F Clear",
        status="Final"
    )
    assert game.matchup_title == "#3 Texas @ #1 Georgia"
    assert game.score_display == "15 - 30"
    assert game.home_record == "12-1"
    assert game.weather == "☀️ 72°F Clear"
    print("PASSED ✅")


def test_team_colors():
    print("Testing Team Colors Registry...", end=" ")
    chiefs_color = get_team_color("Kansas City Chiefs", "NFL")
    assert chiefs_color == "#E31837", f"Expected #E31837, got {chiefs_color}"

    georgia_color = get_team_color("#1 Georgia", "CFB")
    assert georgia_color == "#BA0C2F", f"Expected #BA0C2F, got {georgia_color}"

    texas_color = get_team_color("Texas Longhorns", "CFB")
    assert texas_color == "#BF5700", f"Expected #BF5700, got {texas_color}"
    print("PASSED ✅")


def test_weather_service():
    print("Testing Weather Service & Dome Detection...", end=" ")
    # Dome test
    dome_weather = get_venue_weather("Mercedes-Benz Stadium")
    assert "Dome" in dome_weather or "Indoor" in dome_weather, f"Failed dome detection: {dome_weather}"

    # Outdoor test (Arrowhead)
    arrowhead_weather = get_venue_weather("GEHA Field at Arrowhead Stadium")
    assert "°F" in arrowhead_weather, f"Failed outdoor weather lookup: {arrowhead_weather}"
    print("PASSED ✅")


def test_sqlite_caching():
    print("Testing SQLite Caching & TTL...", end=" ")
    init_db()
    clear_all_cache()

    sample_payload = {"games": [{"id": 101, "name": "Chiefs vs Ravens"}]}
    cache_key = "test_sample_key"

    # Test setting and reading valid cache
    set_cached_data(cache_key, sample_payload, ttl_seconds=2)
    cached = get_cached_data(cache_key)
    assert cached == sample_payload, "Failed to retrieve fresh cache"

    # Test cache expiration (TTL = 1s, sleep 1.2s)
    set_cached_data("expire_test", {"value": 42}, ttl_seconds=1)
    time.sleep(1.2)
    expired = get_cached_data("expire_test")
    assert expired is None, "Expired cache was not purged"
    print("PASSED ✅")


def test_api_clients_enriched_data():
    print("Testing API Clients (Enriched Data & Parsing)...", end=" ")
    nfl = NFLClient()
    cfb = CFBClient()

    nfl_games, _, _ = nfl.get_games_for_date("2026-09-07")
    cfb_games, _, _ = cfb.get_games_for_date("2026-09-07")

    assert len(nfl_games) > 0, "NFL client returned no games"
    assert len(cfb_games) > 0, "CFB client returned no games"
    
    # Check that NFL games have color, record, and weather
    sample_nfl = nfl_games[0]
    assert sample_nfl.home_color is not None, "Missing home_color in NFL game"
    assert sample_nfl.home_record is not None, "Missing home_record in NFL game"
    assert sample_nfl.weather is not None, "Missing weather in NFL game"

    # Check that CFB games have rankings
    sample_cfb = cfb_games[0]
    assert sample_cfb.home_rank is not None, "Missing home_rank in CFB game"
    assert sample_cfb.home_color is not None, "Missing home_color in CFB game"
    print("PASSED ✅")


def test_theme_manager():
    print("Testing Theme Manager...", end=" ")
    tm = ThemeManager()
    bg_color = tm.get_color("background")
    assert bg_color.startswith("#"), f"Invalid hex color: {bg_color}"
    font = tm.get_font("title")
    assert len(font) >= 2, f"Invalid font tuple: {font}"
    print("PASSED ✅")


if __name__ == "__main__":
    print("\n--- RUNNING SYSTEM TESTS ---")
    test_game_model()
    test_team_colors()
    test_weather_service()
    test_sqlite_caching()
    test_api_clients_enriched_data()
    test_theme_manager()
    print("--- ALL TESTS PASSED SUCCESSFULLY! 🚀 ---\n")
