"""Home screen: the player list on top, round options and Pick! fixed at the bottom."""

from collections.abc import Callable

import flet as ft

from models import Roster, RoundSetup
from views.players import PlayersView
from views.round_panel import RoundPanel


class HomeView:
    def __init__(
        self,
        page: ft.Page,
        roster: Roster,
        setup: RoundSetup,
        on_pick: Callable[[], None],
        on_change: Callable[[], None],
    ) -> None:
        self.on_change = on_change
        self.players = PlayersView(page, roster, setup, on_change=self._changed)
        self.round_panel = RoundPanel(page, roster, setup, on_pick=on_pick)
        self.control = ft.Column(
            [self.players.control, ft.Divider(height=1), self.round_panel.control],
            expand=True,
            spacing=12,
        )

    def refresh(self) -> None:
        """Re-render everything, e.g. after players are loaded. Caller does page.update()."""
        self.players.render()
        self.round_panel.render()

    def _changed(self) -> None:
        # The player list re-renders itself; the panel depends on who's selected.
        self.round_panel.render()
        self.on_change()
