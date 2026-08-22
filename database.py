"""
Local SQLite Caching Module.
Protects free API tiers by storing JSON responses with configurable Time-To-Live (TTL).
"""

import json
import sqlite3
import time
from typing import Any, Optional
from config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection object with WAL mode enabled for fast concurrent reads."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db() -> None:
    """Initializes the database schema if it doesn't already exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS api_cache (
                cache_key TEXT PRIMARY KEY,
                response_json TEXT NOT NULL,
                fetched_at REAL NOT NULL,
                ttl_seconds INTEGER NOT NULL
            )
        """)
        conn.commit()


def get_cached_data(cache_key: str) -> Optional[Any]:
    """
    Retrieves cached data if it exists and has not expired.
    
    Args:
        cache_key: Unique identifier for the query (e.g., 'nfl_games_2026-09-10').
        
    Returns:
        The deserialized JSON data (dict or list), or None if missing/expired.
    """
    init_db()
    current_time = time.time()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT response_json, fetched_at, ttl_seconds FROM api_cache WHERE cache_key = ?",
            (cache_key,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
            
        response_json, fetched_at, ttl_seconds = row
        age_seconds = current_time - fetched_at
        
        # Check if the cache entry is still valid
        if age_seconds <= ttl_seconds:
            try:
                return json.loads(response_json)
            except json.JSONDecodeError:
                return None
        else:
            # Cache is expired; remove it to keep DB lightweight
            conn.execute("DELETE FROM api_cache WHERE cache_key = ?", (cache_key,))
            conn.commit()
            return None


def set_cached_data(cache_key: str, data: Any, ttl_seconds: int) -> None:
    """
    Saves data into the SQLite cache with an expiration duration.
    
    Args:
        cache_key: Unique key for this request.
        data: Python dict or list to store.
        ttl_seconds: How long (in seconds) the data remains valid.
    """
    init_db()
    current_time = time.time()
    serialized = json.dumps(data)
    
    with get_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO api_cache (cache_key, response_json, fetched_at, ttl_seconds)
            VALUES (?, ?, ?, ?)
        """, (cache_key, serialized, current_time, ttl_seconds))
        conn.commit()


def clear_all_cache() -> None:
    """Clears all cached API responses."""
    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM api_cache")
        conn.commit()
