"""Results screen: a numbered turn order, or one big winner/loser."""

from collections.abc import Callable

import flet as ft

from models import Mode, Player
from picker import RoundResult, ordinal
from views.widgets import player_avatar

BUTTON_HEIGHT = 64
BUTTON_TEXT = ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)

SINGLE_STYLE: dict[Mode, tuple[str, ft.IconData, ft.Colors]] = {
    Mode.WINNER: ("The winner is…", ft.Icons.EMOJI_EVENTS, ft.Colors.AMBER),
    Mode.LOSER: ("Oh no! The loser is…", ft.Icons.SENTIMENT_VERY_DISSATISFIED, ft.Colors.BLUE_GREY),
}


class ResultsView:
    def __init__(self, on_pick_again: Callable[[], None], on_back: Callable[[], None]) -> None:
        self.body = ft.Container(expand=True)
        self.control = ft.Column(
            [
                self.body,
                ft.Row(
                    [
                        ft.OutlinedButton(
                            "Players",
                            icon=ft.Icons.ARROW_BACK,
                            height=BUTTON_HEIGHT,
                            style=ft.ButtonStyle(text_style=BUTTON_TEXT),
                            on_click=lambda _: on_back(),
                        ),
                        ft.FilledButton(
                            "Pick again",
                            icon=ft.Icons.REFRESH,
                            height=BUTTON_HEIGHT,
                            expand=True,
                            style=ft.ButtonStyle(text_style=BUTTON_TEXT),
                            on_click=lambda _: on_pick_again(),
                        ),
                    ],
                    spacing=12,
                ),
            ],
            expand=True,
            spacing=16,
        )

    def render(self, result: RoundResult) -> None:
        """Show `result`. Caller is responsible for page.update()."""
        if result.mode is Mode.ORDER:
            self.body.content = self._order(result)
        else:
            self.body.content = self._single(result)

    def _order(self, result: RoundResult) -> ft.Control:
        rows = [self._order_row(i, player, first=i == 1) for i, player in enumerate(result.players, 1)]
        return ft.Column(
            [
                ft.Text("Turn order", size=28, weight=ft.FontWeight.BOLD),
                ft.ListView(rows, spacing=8, expand=True),
            ],
            expand=True,
            spacing=12,
        )

    def _order_row(self, position: int, player: Player, first: bool) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(ordinal(position), size=26, weight=ft.FontWeight.BOLD, width=72),
                    player_avatar(player, radius=26),
                    ft.Text(player.name, size=28, weight=ft.FontWeight.BOLD if first else None, expand=True),
                ],
                spacing=12,
            ),
            # The player who goes first stands out.
            bgcolor=ft.Colors.PRIMARY_CONTAINER if first else ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=16,
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
        )

    def _single(self, result: RoundResult) -> ft.Control:
        heading, icon, color = SINGLE_STYLE[result.mode]
        player = result.chosen
        column = ft.Column(
            [
                ft.Icon(icon, size=120, color=color),
                ft.Text(heading, size=26, text_align=ft.TextAlign.CENTER),
                player_avatar(player, radius=56),
                ft.Text(player.name, size=52, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
        )
        # A Column is only as wide as its content; the Container centres it on screen.
        return ft.Container(column, alignment=ft.Alignment.CENTER, expand=True)
