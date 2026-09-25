"""Home screen: the player list on top, round options and Pick! fixed at the bottom."""

import flet as ft

from models import Roster, RoundSetup
from views.players import PlayersView
from views.round_panel import RoundPanel


class HomeView:
    def __init__(self, page: ft.Page, roster: Roster, setup: RoundSetup) -> None:
        self.page = page
        self.roster = roster
        self.setup = setup
        self.players = PlayersView(page, roster, setup, on_change=self.render)
        self.round_panel = RoundPanel(page, roster, setup, on_pick=self._pick)
        self.control = ft.Column(
            [self.players.control, ft.Divider(height=1), self.round_panel.control],
            expand=True,
            spacing=12,
        )

    def render(self) -> None:
        # The player list re-renders itself; the panel depends on who's selected.
        self.round_panel.render()

    def _pick(self) -> None:
        # Placeholder until Phase 3 adds the picker and results screen.
        names = ", ".join(p.name for p in self.setup.selected_players(self.roster))
        self.page.show_dialog(
            ft.SnackBar(f"{self.setup.mode.name.title()} from: {names} (results coming in Phase 3)")
        )
