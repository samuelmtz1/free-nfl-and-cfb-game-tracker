"""
Game Card Component.
A customizable UI widget rendering a single football matchup card.
"""

import customtkinter as ctk
from models.game import Game
from ui.theme_manager import ThemeManager


class GameCard(ctk.CTkFrame):
    """Visual card representation of a single NFL or CFB game."""

    def __init__(self, master, game: Game, theme: ThemeManager, **kwargs):
        super().__init__(
            master,
            corner_radius=12,
            fg_color=theme.get_color("surface"),
            border_width=1,
            border_color=theme.get_color("border"),
            **kwargs
        )
        self.game = game
        self.theme = theme
        self._build_card()

    def _build_card(self) -> None:
        # Top Header Bar: Sport Badge + Status Badge + Time
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(12, 6))

        # Sport Badge (NFL / CFB)
        sport_color = self.theme.get_color("accent_nfl") if self.game.sport == "NFL" else self.theme.get_color("accent_cfb")
        sport_badge = ctk.CTkLabel(
            header_frame,
            text=f" {self.game.sport} ",
            font=self.theme.get_font("badge"),
            text_color="#ffffff",
            fg_color=sport_color,
            corner_radius=6
        )
        sport_badge.pack(side="left", padx=(0, 8))

        # Status Badge (Live / Final / Scheduled)
        if self.game.is_live:
            status_color = self.theme.get_color("badge_live")
            status_text = f" ● LIVE - {self.game.period_or_quarter} "
        elif self.game.status.lower() == "final":
            status_color = self.theme.get_color("badge_final")
            status_text = " FINAL "
        else:
            status_color = self.theme.get_color("badge_scheduled")
            status_text = f" {self.game.status} "

        status_badge = ctk.CTkLabel(
            header_frame,
            text=status_text,
            font=self.theme.get_font("badge"),
            text_color="#ffffff",
            fg_color=status_color,
            corner_radius=6
        )
        status_badge.pack(side="left")

        # Time / Clock Info (Right-aligned in header)
        time_label = ctk.CTkLabel(
            header_frame,
            text=self.game.start_time,
            font=self.theme.get_font("body"),
            text_color=self.theme.get_color("text_muted")
        )
        time_label.pack(side="right")

        # Matchup Body: Teams and Scores
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.pack(fill="x", padx=16, pady=8)

        # Away Team Row
        away_row = ctk.CTkFrame(body_frame, fg_color="transparent")
        away_row.pack(fill="x", pady=2)

        away_name = ctk.CTkLabel(
            away_row,
            text=self.game.away_team,
            font=self.theme.get_font("subtitle"),
            text_color=self.theme.get_color("text_main"),
            anchor="w"
        )
        away_name.pack(side="left", fill="x", expand=True)

        away_score_text = str(self.game.away_score) if self.game.away_score is not None else "-"
        away_score = ctk.CTkLabel(
            away_row,
            text=away_score_text,
            font=self.theme.get_font("score"),
            text_color=self.theme.get_color("text_main")
        )
        away_score.pack(side="right", padx=(8, 0))

        # Home Team Row
        home_row = ctk.CTkFrame(body_frame, fg_color="transparent")
        home_row.pack(fill="x", pady=2)

        home_name = ctk.CTkLabel(
            home_row,
            text=self.game.home_team,
            font=self.theme.get_font("subtitle"),
            text_color=self.theme.get_color("text_main"),
            anchor="w"
        )
        home_name.pack(side="left", fill="x", expand=True)

        home_score_text = str(self.game.home_score) if self.game.home_score is not None else "-"
        home_score = ctk.CTkLabel(
            home_row,
            text=home_score_text,
            font=self.theme.get_font("score"),
            text_color=self.theme.get_color("text_main")
        )
        home_score.pack(side="right", padx=(8, 0))

        # Footer Row: Broadcast & Venue
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", padx=16, pady=(4, 12))

        footer_text = f"📺 {self.game.broadcast}" if self.game.broadcast else ""
        if self.game.venue:
            footer_text += f"  •  📍 {self.game.venue}"

        footer_label = ctk.CTkLabel(
            footer_frame,
            text=footer_text,
            font=self.theme.get_font("body"),
            text_color=self.theme.get_color("text_muted"),
            anchor="w"
        )
        footer_label.pack(side="left", fill="x", expand=True)
