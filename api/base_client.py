"""
Base API Client.
Provides rate-limiting, SQLite caching, error handling, and demo fallback.
"""

import time
import requests
from typing import Any, Dict, Optional, Tuple
from database import get_cached_data, set_cached_data


class BaseClient:
    """
    Abstract client that enforces request throttling and SQLite caching.
    """

    def __init__(self, name: str, min_interval_seconds: float = 1.0):
        self.name = name
        self.min_interval_seconds = min_interval_seconds
        self.last_request_time: float = 0.0

    def _wait_for_rate_limit(self) -> None:
        """Enforces minimum delay between outgoing HTTP calls to avoid hitting rate limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval_seconds:
            sleep_duration = self.min_interval_seconds - elapsed
            time.sleep(sleep_duration)
        self.last_request_time = time.time()

    def fetch_with_cache(
        self,
        url: str,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]] = None,
        cache_key: Optional[str] = None,
        ttl_seconds: int = 300,
        timeout: int = 10
    ) -> Tuple[Optional[Any], bool, Optional[str]]:
        """
        Fetches data from cache first; if not found, executes a rate-limited HTTP GET request.
        
        Returns:
            (data, is_from_cache, error_message)
        """
        # 1. Check local cache first
        if cache_key:
            cached_data = get_cached_data(cache_key)
            if cached_data is not None:
                return cached_data, True, None

        # 2. Enforce client-side rate limit
        self._wait_for_rate_limit()

        # 3. Perform network call
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if cache_key:
                    set_cached_data(cache_key, data, ttl_seconds)
                return data, False, None
            elif response.status_code == 401:
                return None, False, "Invalid or missing API key (401 Unauthorized)."
            elif response.status_code == 429:
                return None, False, "Rate limit reached (429 Too Many Requests). Cached or demo data used."
            else:
                return None, False, f"API returned status code {response.status_code}."
                
        except requests.exceptions.Timeout:
            return None, False, "Request timed out. Please check your internet connection."
        except requests.exceptions.RequestException as e:
            return None, False, f"Network error: {str(e)}"
        except Exception as e:
            return None, False, f"Unexpected error: {str(e)}"
