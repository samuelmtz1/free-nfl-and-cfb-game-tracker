"""
Game Card Component.
A customizable UI widget rendering a football matchup card with team branding, records, rankings, and weather.
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
        # 1. Top Header Bar: Sport Badge + Status Badge + Time
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

        # 2. Matchup Body: Teams, Colors, Records, Rankings, and Scores
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.pack(fill="x", padx=16, pady=8)

        # --- Away Team Row ---
        self._build_team_row(
            parent=body_frame,
            team_name=self.game.away_team,
            team_color=self.game.away_color or self.theme.get_color("primary"),
            rank=self.game.away_rank,
            record=self.game.away_record,
            score=self.game.away_score
        )

        # --- Home Team Row ---
        self._build_team_row(
            parent=body_frame,
            team_name=self.game.home_team,
            team_color=self.game.home_color or self.theme.get_color("primary"),
            rank=self.game.home_rank,
            record=self.game.home_record,
            score=self.game.home_score
        )

        # 3. Footer Row: Broadcast, Venue, and Weather Chip
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", padx=16, pady=(4, 12))

        # Venue & Broadcast (Left)
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

        # Weather Chip (Right)
        if self.game.weather:
            weather_label = ctk.CTkLabel(
                footer_frame,
                text=f" {self.game.weather} ",
                font=self.theme.get_font("body"),
                text_color=self.theme.get_color("text_main"),
                fg_color=self.theme.get_color("surface_hover"),
                corner_radius=6
            )
            weather_label.pack(side="right")

    def _build_team_row(
        self,
        parent,
        team_name: str,
        team_color: str,
        rank: str = None,
        record: str = None,
        score: int = None
    ) -> None:
        """Constructs a team row with color strip, rank badge, name, record, and score."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=3)

        # Team Color Vertical Accent Bar
        color_bar = ctk.CTkFrame(row, width=5, height=24, fg_color=team_color, corner_radius=2)
        color_bar.pack(side="left", padx=(0, 10))

        # Rank Badge (e.g. #1)
        if rank:
            rank_badge = ctk.CTkLabel(
                row,
                text=f" {rank} ",
                font=self.theme.get_font("badge"),
                text_color="#ffffff",
                fg_color="#475569",
                corner_radius=4
            )
            rank_badge.pack(side="left", padx=(0, 6))

        # Team Name
        name_label = ctk.CTkLabel(
            row,
            text=team_name,
            font=self.theme.get_font("subtitle"),
            text_color=self.theme.get_color("text_main"),
            anchor="w"
        )
        name_label.pack(side="left")

        # Team Record (e.g. (11-2))
        if record:
            record_label = ctk.CTkLabel(
                row,
                text=f" ({record})",
                font=self.theme.get_font("body"),
                text_color=self.theme.get_color("text_muted")
            )
            record_label.pack(side="left", padx=(4, 0))

        # Team Score
        score_text = str(score) if score is not None else "-"
        score_label = ctk.CTkLabel(
            row,
            text=score_text,
            font=self.theme.get_font("score"),
            text_color=self.theme.get_color("text_main")
        )
        score_label.pack(side="right", padx=(8, 0))
