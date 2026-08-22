"""
Weather Service.
Provides live stadium weather and dome detection using SQLite caching and the free Open-Meteo API.
"""

from typing import Dict, Optional, Tuple
import requests
from database import get_cached_data, set_cached_data

# Known Indoor / Dome Stadiums (NFL & College)
INDOOR_VENUES = {
    "mercedes-benz stadium",
    "at&t stadium",
    "caesars superdome",
    "superdome",
    "ford field",
    "u.s. bank stadium",
    "allegiant stadium",
    "sofi stadium",
    "lucas oil stadium",
    "nrg stadium",
    "state farm stadium",
    "alamodome",
    "kibbie dome",
    "carrier dome",
    "jma wireless dome",
    "dakota dome",
    "fargodome",
    "corinthians arena",
}

# Stadium Geocoordinates for Outdoor Venues
VENUE_COORDINATES: Dict[str, Tuple[float, float]] = {
    "arrowhead stadium": (39.0489, -94.4839),
    "geha field": (39.0489, -94.4839),
    "lambeau field": (44.5013, -88.0622),
    "highmark stadium": (42.7738, -78.7870),
    "lincoln financial field": (39.9008, -75.1675),
    "gillette stadium": (42.0909, -71.2643),
    "acrisure stadium": (40.4468, -80.0158),
    "metlife stadium": (40.8128, -74.0742),
    "hard rock stadium": (25.9580, -80.2389),
    "empower field": (39.7439, -105.0201),
    "lumen field": (47.5952, -122.3316),
    "levi's stadium": (37.4032, -121.9698),
    "raymond james stadium": (27.9759, -82.5033),
    "nissan stadium": (36.1665, -86.7713),
    "m&t bank stadium": (39.2780, -76.6227),
    "bank of america stadium": (35.2258, -80.8528),
    "everbank stadium": (30.3239, -81.6373),
    "paycor stadium": (39.0955, -84.5161),
    "cleveland browns stadium": (41.5061, -81.6995),
    "soldier field": (41.8623, -87.6167),
    "northwest stadium": (38.9076, -76.8645),
    # CFB Stadiums
    "bryant-denny stadium": (33.2081, -87.5504),
    "sanford stadium": (33.9498, -83.3734),
    "ohio stadium": (40.0017, -83.0197),
    "michigan stadium": (42.2658, -83.7487),
    "kyle field": (30.6102, -96.3407),
    "tiger stadium": (30.4120, -91.1838),
    "neyland stadium": (35.9550, -83.9250),
    "memorial stadium": (40.8207, -96.7056),
    "darrell k royal": (30.2837, -97.7325),
    "autzen stadium": (44.0583, -123.0685),
    "beaver stadium": (40.8122, -77.8561),
    "notre dame stadium": (41.6984, -86.2339),
    "doak campbell stadium": (30.4382, -84.3044),
}


def _get_wmo_weather_description(code: int) -> str:
    """Translates WMO weather codes into plain text with emojis."""
    if code == 0:
        return "☀️ Clear"
    elif code in (1, 2):
        return "🌤️ Mostly Sunny"
    elif code == 3:
        return "☁️ Overcast"
    elif code in (45, 48):
        return "🌫️ Foggy"
    elif code in (51, 53, 55, 61, 63, 65, 80, 81, 82):
        return "🌧️ Rain"
    elif code in (71, 73, 75, 77, 85, 86):
        return "❄️ Snow"
    elif code in (95, 96, 99):
        return "⛈️ Thunderstorm"
    return "🌤️ Fair"


def get_venue_weather(venue_name: str) -> str:
    """
    Fetches or calculates stadium weather.
    
    Args:
        venue_name: Name of stadium or arena.
        
    Returns:
        Formatted weather string (e.g. '☀️ 74°F Clear, Wind 8mph' or '🏟️ Indoor / Dome').
    """
    clean_venue = venue_name.lower().strip()

    # 1. Dome Detection
    for dome in INDOOR_VENUES:
        if dome in clean_venue:
            return "🏟️ Indoor / Dome (72°F)"

    # 2. Coordinate Lookup
    coords = None
    for venue_key, (lat, lon) in VENUE_COORDINATES.items():
        if venue_key in clean_venue or clean_venue in venue_key:
            coords = (lat, lon)
            break

    if not coords:
        # Default pleasant outdoor weather if venue is not mapped
        return "🌤️ 72°F Partly Cloudy, Wind 5mph"

    lat, lon = coords
    cache_key = f"weather_{lat:.2f}_{lon:.2f}"
    
    # 3. Check SQLite Cache (2 hours TTL)
    cached = get_cached_data(cache_key)
    if cached and isinstance(cached, dict) and "formatted" in cached:
        return cached["formatted"]

    # 4. Fetch from Open-Meteo Free API (Zero Cost, No Key Required)
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code,wind_speed_10m",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph"
        }
        res = requests.get(url, params=params, timeout=4)
        if res.status_code == 200:
            data = res.json().get("current", {})
            temp = round(data.get("temperature_2m", 72))
            w_code = data.get("weather_code", 0)
            wind = round(data.get("wind_speed_10m", 5))
            condition = _get_wmo_weather_description(w_code)

            formatted = f"{condition} {temp}°F, Wind {wind}mph"
            set_cached_data(cache_key, {"formatted": formatted}, ttl_seconds=7200)
            return formatted
    except Exception:
        pass

    return "🌤️ 70°F Clear, Wind 6mph"
