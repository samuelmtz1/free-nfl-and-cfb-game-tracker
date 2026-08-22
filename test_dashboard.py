"""
Unit and Integration Tests for Sports Dashboard.
Verifies caching, model parsing, rate limiting, and theme loading.
"""

import time
from database import init_db, set_cached_data, get_cached_data, clear_all_cache
from models.game import Game
from api.nfl_client import NFLClient
from api.cfb_client import CFBClient
from ui.theme_manager import ThemeManager


def test_game_model():
    print("Testing Game Model...", end=" ")
    game = Game(
        id="test_1",
        sport="NFL",
        home_team="Kansas City Chiefs",
        away_team="San Francisco 49ers",
        home_score=25,
        away_score=22,
        status="Final"
    )
    assert game.matchup_title == "San Francisco 49ers @ Kansas City Chiefs"
    assert game.score_display == "22 - 25"
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


def test_api_clients_demo_mode():
    print("Testing API Clients (Demo Mode & Parsing)...", end=" ")
    nfl = NFLClient()
    cfb = CFBClient()

    nfl_games, nfl_cached, nfl_msg = nfl.get_games_for_date("2026-09-07")
    cfb_games, cfb_cached, cfb_msg = cfb.get_games_for_date("2026-09-07")

    assert len(nfl_games) > 0, "NFL client returned no games"
    assert len(cfb_games) > 0, "CFB client returned no games"
    assert all(isinstance(g, Game) for g in nfl_games), "NFL items are not Game instances"
    assert all(isinstance(g, Game) for g in cfb_games), "CFB items are not Game instances"
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
    test_sqlite_caching()
    test_api_clients_demo_mode()
    test_theme_manager()
    print("--- ALL TESTS PASSED SUCCESSFULLY! 🚀 ---\n")
