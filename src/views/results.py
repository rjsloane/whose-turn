"""Results screen: a quick "shuffling" reveal, then a numbered turn order or one big winner/loser."""

import asyncio
from collections.abc import Callable

import flet as ft

from models import Mode, Player
from picker import RoundResult, ordinal
from reveal import reveal_delays, teaser_players
from views.widgets import player_avatar

BUTTON_HEIGHT = 64
BUTTON_TEXT = ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)

TEASER_HEADINGS: dict[Mode, str] = {
    Mode.ORDER: "Who goes first?",
    Mode.WINNER: "Who's the winner?",
    Mode.LOSER: "Who's the loser?",
}
# How the result pops in: a bouncy scale for one name, a gentler one for a list.
POP_CURVES: dict[Mode, ft.AnimationCurve] = {
    Mode.ORDER: ft.AnimationCurve.EASE_OUT_BACK,
    Mode.WINNER: ft.AnimationCurve.ELASTIC_OUT,
    Mode.LOSER: ft.AnimationCurve.ELASTIC_OUT,
}

SINGLE_STYLE: dict[Mode, tuple[str, ft.IconData, ft.Colors]] = {
    Mode.WINNER: ("The winner is…", ft.Icons.EMOJI_EVENTS, ft.Colors.AMBER),
    Mode.LOSER: ("Oh no! The loser is…", ft.Icons.SENTIMENT_VERY_DISSATISFIED, ft.Colors.BLUE_GREY),
}


class ResultsView:
    def __init__(self, on_pick_again: Callable[[], None], on_back: Callable[[], None]) -> None:
        self.body = ft.Container(expand=True)
        self.pick_again_button = ft.FilledButton(
            "Pick again",
            icon=ft.Icons.REFRESH,
            height=BUTTON_HEIGHT,
            expand=True,
            style=ft.ButtonStyle(text_style=BUTTON_TEXT),
            on_click=lambda _: on_pick_again(),
        )
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
                        self.pick_again_button,
                    ],
                    spacing=12,
                ),
            ],
            expand=True,
            spacing=16,
        )

    async def reveal(self, page: ft.Page, result: RoundResult, is_current: Callable[[], bool]) -> None:
        """Flash random names, slowing down, then pop the result in.

        `is_current` turns False if a newer pick or leaving the screen makes this
        reveal stale; it then just stops.
        """
        self.pick_again_button.disabled = True  # no double-picks mid-reveal
        avatar_slot = ft.Container()
        name = ft.Text(size=52, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        self.body.content = _centred(
            ft.Icon(ft.Icons.CASINO, size=96, color=ft.Colors.PRIMARY),
            ft.Text(TEASER_HEADINGS[result.mode], size=26),
            avatar_slot,
            name,
        )
        frames = teaser_players(result.candidates, result.chosen)
        for player, delay in zip(frames, reveal_delays()):
            if not is_current():
                return
            avatar_slot.content = player_avatar(player, radius=56)
            name.value = player.name
            page.update()
            await asyncio.sleep(delay)
        if not is_current():
            return
        await self._pop_in(page, result)
        self.pick_again_button.disabled = False
        page.update()

    async def _pop_in(self, page: ft.Page, result: RoundResult) -> None:
        content = self._order(result) if result.mode is Mode.ORDER else self._single(result)
        pop = ft.Container(
            content,
            expand=True,
            scale=0.5,
            opacity=0,
            animate_scale=ft.Animation(600, POP_CURVES[result.mode]),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )
        self.body.content = pop
        page.update()
        # Let the small/transparent starting state reach the screen, then animate to full size.
        await asyncio.sleep(0.05)
        pop.scale = 1
        pop.opacity = 1

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
        return _centred(
            ft.Icon(icon, size=120, color=color),
            ft.Text(heading, size=26, text_align=ft.TextAlign.CENTER),
            player_avatar(player, radius=56),
            ft.Text(player.name, size=52, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        )


def _centred(*controls: ft.Control) -> ft.Control:
    column = ft.Column(
        list(controls),
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16,
    )
    # A Column is only as wide as its content; the Container centres it on screen.
    return ft.Container(column, alignment=ft.Alignment.CENTER, expand=True)
