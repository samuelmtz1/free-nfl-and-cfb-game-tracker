"""
Configuration module for the Sports Dashboard.
Handles environment variables, API endpoints, rate limits, and caching durations.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base project directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from local .env file (if present)
load_dotenv(BASE_DIR / ".env")

# ==============================================================================
# API Keys (Loaded from .env securely)
# ==============================================================================
BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY", "").strip()
CFBD_API_KEY = os.getenv("CFBD_API_KEY", "").strip()

# ==============================================================================
# API Endpoints
# ==============================================================================
# BallDontLie NFL API
BALLDONTLIE_BASE_URL = "https://api.balldontlie.io/nfl/v1"
BALLDONTLIE_GAMES_URL = f"{BALLDONTLIE_BASE_URL}/games"

# College Football Data (CFBD) API
CFBD_BASE_URL = "https://api.collegefootballdata.com"
CFBD_SCOREBOARD_URL = f"{CFBD_BASE_URL}/scoreboard"
CFBD_GAMES_URL = f"{CFBD_BASE_URL}/games"

# ==============================================================================
# Rate Limiting & Safety Controls (Strict Free-Tier Defense)
# ==============================================================================
# BallDontLie Free Tier: 5 requests per minute -> Minimum 12 seconds between calls
BALLDONTLIE_MIN_INTERVAL_SECONDS = 12.0

# College Football Data Free Tier: 1,000 requests per month (~33/day)
# Minimum 1 hour cache duration for general schedules
CFBD_MIN_INTERVAL_SECONDS = 5.0

# ==============================================================================
# Caching Durations (TTL in Seconds)
# ==============================================================================
# Database file path (strictly local SQLite)
DATABASE_PATH = BASE_DIR / "sports_cache.sqlite"

# Live game cache TTL (e.g. 60 seconds for live score updates)
CACHE_TTL_LIVE_GAMES = 60

# Past/Completed games or future schedules (TTL: 12 hours)
CACHE_TTL_STATIC_GAMES = 12 * 3600

# Theme File Path
THEME_FILE_PATH = BASE_DIR / "theme.json"
