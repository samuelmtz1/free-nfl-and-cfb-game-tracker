"""
Main Sports Dashboard Application Window.
Handles navigation, sport filtering, live search, caching status, and theme switching.
"""

from datetime import datetime, timedelta
import threading
import customtkinter as ctk
from typing import List

from api.nfl_client import NFLClient
from api.cfb_client import CFBClient
from models.game import Game
from ui.theme_manager import ThemeManager
from ui.game_card import GameCard


class SportsDashboardApp(ctk.CTk):
    """Primary application window for the Football Dashboard."""

    def __init__(self):
        super().__init__()

        self.theme_manager = ThemeManager()
        ctk.set_appearance_mode(self.theme_manager.mode)
        ctk.set_default_color_theme("blue")

        self.title("🏈 Free Football Dashboard (NFL & CFB)")
        self.geometry("900x750")
        self.minsize(750, 600)
        self.configure(fg_color=self.theme_manager.get_color("background"))

        # Initialize API Clients
        self.nfl_client = NFLClient()
        self.cfb_client = CFBClient()

        # State Variables
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.selected_filter = "All"
        self.all_games: List[Game] = []
        self.is_loading = False

        # Build UI Components
        self._build_header()
        self._build_control_bar()
        self._build_status_banner()
        self._build_games_container()

        # Initial Load
        self.refresh_games()

    def _build_header(self) -> None:
        """Constructs the top header bar with branding and appearance toggle."""
        header = ctk.CTkFrame(self, fg_color=self.theme_manager.get_color("surface"), corner_radius=0, height=70)
        header.pack(fill="x", side="top")

        title_label = ctk.CTkLabel(
            header,
            text="🏈 FOOTBALL GAME CENTER",
            font=self.theme_manager.get_font("title"),
            text_color=self.theme_manager.get_color("text_main")
        )
        title_label.pack(side="left", padx=20, pady=16)

        sub_label = ctk.CTkLabel(
            header,
            text="100% Free • Rate-Limited • Local SQLite Caching",
            font=self.theme_manager.get_font("body"),
            text_color=self.theme_manager.get_color("text_muted")
        )
        sub_label.pack(side="left", padx=5, pady=(20, 16))

        # Mode Switcher (Dark / Light)
        self.mode_switch = ctk.CTkSwitch(
            header,
            text="Dark Mode",
            command=self._toggle_theme_mode,
            font=self.theme_manager.get_font("body"),
            text_color=self.theme_manager.get_color("text_main")
        )
        if self.theme_manager.mode == "dark":
            self.mode_switch.select()
        else:
            self.mode_switch.deselect()
        self.mode_switch.pack(side="right", padx=20, pady=16)

    def _build_control_bar(self) -> None:
        """Constructs league filter tabs, search bar, and refresh button."""
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=(16, 8))

        # League Selector Tabs
        self.league_selector = ctk.CTkSegmentedButton(
            bar,
            values=["All", "NFL", "CFB"],
            command=self._on_league_filter_change,
            selected_color=self.theme_manager.get_color("primary"),
            selected_hover_color=self.theme_manager.get_color("primary_hover"),
            unselected_color=self.theme_manager.get_color("surface"),
            text_color=self.theme_manager.get_color("text_main"),
            font=self.theme_manager.get_font("subtitle")
        )
        self.league_selector.set("All")
        self.league_selector.pack(side="left", padx=(0, 12))

        # Search Bar
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._apply_filters())
        self.search_entry = ctk.CTkEntry(
            bar,
            placeholder_text="🔍 Search team, matchup, or channel...",
            textvariable=self.search_var,
            width=280,
            fg_color=self.theme_manager.get_color("surface"),
            border_color=self.theme_manager.get_color("border"),
            text_color=self.theme_manager.get_color("text_main"),
            placeholder_text_color=self.theme_manager.get_color("text_muted")
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))

        # Refresh Button
        self.refresh_btn = ctk.CTkButton(
            bar,
            text="🔄 Refresh",
            width=100,
            command=self.refresh_games,
            fg_color=self.theme_manager.get_color("primary"),
            hover_color=self.theme_manager.get_color("primary_hover"),
            font=self.theme_manager.get_font("subtitle")
        )
        self.refresh_btn.pack(side="right")

    def _build_status_banner(self) -> None:
        """Constructs a lightweight status strip showing cache source and active notifications."""
        self.status_banner = ctk.CTkFrame(self, fg_color=self.theme_manager.get_color("surface"), height=30, corner_radius=6)
        self.status_banner.pack(fill="x", padx=20, pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            self.status_banner,
            text="⚡ Status: Ready",
            font=self.theme_manager.get_font("body"),
            text_color=self.theme_manager.get_color("text_muted")
        )
        self.status_label.pack(side="left", padx=12, pady=4)

        self.game_count_label = ctk.CTkLabel(
            self.status_banner,
            text="0 games",
            font=self.theme_manager.get_font("body"),
            text_color=self.theme_manager.get_color("text_muted")
        )
        self.game_count_label.pack(side="right", padx=12, pady=4)

    def _build_games_container(self) -> None:
        """Creates the scrollable container where game cards are rendered."""
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _toggle_theme_mode(self) -> None:
        """Toggles between Dark Mode and Light Mode."""
        if self.mode_switch.get() == 1:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def _on_league_filter_change(self, value: str) -> None:
        self.selected_filter = value
        self._apply_filters()

    def refresh_games(self) -> None:
        """Fetches games on a separate background thread to keep the GUI buttery smooth."""
        if self.is_loading:
            return

        self.is_loading = True
        self.refresh_btn.configure(state="disabled", text="⏳ Loading...")
        self.status_label.configure(text="🔄 Fetching games (Checking local SQLite cache)...")

        threading.Thread(target=self._fetch_games_worker, daemon=True).start()

    def _fetch_games_worker(self) -> None:
        """Worker thread for network and cache operations."""
        nfl_games, nfl_cached, nfl_msg = self.nfl_client.get_games_for_date(self.current_date)
        cfb_games, cfb_cached, cfb_msg = self.cfb_client.get_games_for_date(self.current_date)

        combined = nfl_games + cfb_games

        # Determine overall cache/demo badge
        status_parts = []
        if nfl_msg:
            status_parts.append(f"NFL: {nfl_msg}")
        elif nfl_cached:
            status_parts.append("NFL: ⚡ Cached")
        else:
            status_parts.append("NFL: 🌐 Live")

        if cfb_msg:
            status_parts.append(f"CFB: {cfb_msg}")
        elif cfb_cached:
            status_parts.append("CFB: ⚡ Cached")
        else:
            status_parts.append("CFB: 🌐 Live")

        status_text = " | ".join(status_parts)

        # Update GUI on main thread
        self.after(0, lambda: self._update_ui_with_games(combined, status_text))

    def _update_ui_with_games(self, games: List[Game], status_text: str) -> None:
        self.all_games = games
        self.is_loading = False
        self.refresh_btn.configure(state="normal", text="🔄 Refresh")
        self.status_label.configure(text=f"⚡ {status_text}")
        self._apply_filters()

    def _apply_filters(self) -> None:
        """Filters games according to selected league and search keyword."""
        # Clear existing cards
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        query = self.search_var.get().strip().lower()

        filtered = []
        for g in self.all_games:
            # Check league filter
            if self.selected_filter != "All" and g.sport != self.selected_filter:
                continue

            # Check search query
            if query:
                searchable_text = f"{g.home_team} {g.away_team} {g.venue} {g.broadcast} {g.sport}".lower()
                if query not in searchable_text:
                    continue

            filtered.append(g)

        self.game_count_label.configure(text=f"{len(filtered)} games displayed")

        if not filtered:
            empty_label = ctk.CTkLabel(
                self.scroll_frame,
                text="No games match your current filter or search.",
                font=self.theme_manager.get_font("subtitle"),
                text_color=self.theme_manager.get_color("text_muted")
            )
            empty_label.pack(pady=40)
            return

        # Render Game Cards
        for game in filtered:
            card = GameCard(self.scroll_frame, game=game, theme=self.theme_manager)
            card.pack(fill="x", pady=6)
