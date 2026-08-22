"""
Theme Manager.
Loads, parses, and provides customizable color schemes and typography from theme.json.
"""

import json
from pathlib import Path
from typing import Any, Dict
from config import THEME_FILE_PATH


class ThemeManager:
    """Manages the UI palette and styling definitions."""

    DEFAULT_THEME: Dict[str, Any] = {
        "theme_name": "Default Dark",
        "mode": "dark",
        "colors": {
            "background": "#0f172a",
            "surface": "#1e293b",
            "surface_hover": "#334155",
            "primary": "#3b82f6",
            "primary_hover": "#2563eb",
            "accent_nfl": "#38bdf8",
            "accent_cfb": "#f97316",
            "text_main": "#f8fafc",
            "text_muted": "#94a3b8",
            "badge_live": "#ef4444",
            "badge_final": "#64748b",
            "badge_scheduled": "#10b981",
            "border": "#334155"
        },
        "fonts": {
            "title": ["Helvetica", 20, "bold"],
            "subtitle": ["Helvetica", 14, "bold"],
            "body": ["Helvetica", 12, "normal"],
            "score": ["Helvetica", 22, "bold"],
            "badge": ["Helvetica", 10, "bold"]
        }
    }

    def __init__(self, file_path: Path = THEME_FILE_PATH):
        self.file_path = file_path
        self.theme = self.load_theme()

    def load_theme(self) -> Dict[str, Any]:
        """Loads theme from JSON file or falls back to defaults."""
        if not self.file_path.exists():
            return self.DEFAULT_THEME.copy()
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception:
            return self.DEFAULT_THEME.copy()

    def get_color(self, name: str) -> str:
        """Retrieves a hex color string by name."""
        colors = self.theme.get("colors", self.DEFAULT_THEME["colors"])
        return colors.get(name, self.DEFAULT_THEME["colors"].get(name, "#ffffff"))

    def get_font(self, name: str) -> tuple:
        """Retrieves font configuration tuple by name."""
        fonts = self.theme.get("fonts", self.DEFAULT_THEME["fonts"])
        return tuple(fonts.get(name, self.DEFAULT_THEME["fonts"].get(name, ("Helvetica", 12, "normal"))))

    @property
    def mode(self) -> str:
        """Returns 'dark' or 'light'."""
        return self.theme.get("mode", "dark")
