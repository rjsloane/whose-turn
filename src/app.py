"""App controller: owns the state, the two screens, and navigation between them.

Screens are Flet `View`s on a route stack ("/" = home, "/result" = results).
Using real views means Android's back button/gesture returns to the home
screen instead of closing the app.
"""

import logging

import flet as ft

import picker
from models import Player, Roster, RoundSetup
from picker import RoundResult
from storage import PlayerStore
from views.home import HomeView
from views.results import ResultsView

log = logging.getLogger(__name__)

HOME = "/"
RESULT = "/result"


def app_bar(title: str) -> ft.AppBar:
    return ft.AppBar(
        title=ft.Text(title, size=24, weight=ft.FontWeight.BOLD),
        center_title=True,
        bgcolor=ft.Colors.PRIMARY_CONTAINER,
    )


class WhoseTurnApp:
    def __init__(self, page: ft.Page, store: PlayerStore) -> None:
        self.page = page
        self.store = store
        self.roster = Roster()
        self.setup = RoundSetup()
        self.result: RoundResult | None = None
        # Only save once loading has succeeded, so a failed load can never
        # overwrite the saved players with an empty list.
        self.can_save = False
        # Bumped on every new pick or when leaving the results screen, so an
        # older reveal still running knows to stop.
        self.reveal_id = 0

    async def start(self) -> None:
        self.home = HomeView(self.page, self.roster, self.setup, on_pick=self.pick, on_change=self.save)
        self.results = ResultsView(on_pick_again=self.pick_again, on_back=self.go_home)
        # Views are built once and reused; routing only changes which are stacked.
        self.home_view = ft.View(
            route=HOME, appbar=app_bar("Whose Turn?"), controls=[ft.SafeArea(self.home.control, expand=True)]
        )
        self.results_view = ft.View(
            route=RESULT, appbar=app_bar("Result"), controls=[ft.SafeArea(self.results.control, expand=True)]
        )
        self.page.on_route_change = self._route_changed
        self.page.on_view_pop = self._view_popped
        # Draw the screen first, then load: storage talks to the client, which
        # must have the page before it can answer.
        self.home.control.disabled = True
        self._route_changed()
        await self._load_players()

    async def _load_players(self) -> None:
        try:
            self.roster.replace_all(await self.store.load())
            self.can_save = True
        except Exception:
            log.exception("Loading players failed")
            self.page.show_dialog(ft.SnackBar("Couldn't load saved players. Changes won't be saved."))
        self.home.control.disabled = False
        self.home.refresh()
        self.page.update()

    # --- navigation ------------------------------------------------------

    def _route_changed(self, _: ft.RouteChangeEvent | None = None) -> None:
        if self.page.route != RESULT:
            self.reveal_id += 1
        self.page.views.clear()
        self.page.views.append(self.home_view)
        if self.page.route == RESULT and self.result is not None:
            self.page.views.append(self.results_view)
        self.page.update()

    async def _view_popped(self, _: ft.ViewPopEvent) -> None:
        # Back button/gesture (or the app bar's back arrow) on the results screen.
        await self.page.push_route(HOME)

    def go_home(self) -> None:
        self.page.navigate(HOME)

    # --- actions ---------------------------------------------------------

    def pick(self) -> None:
        players = self.setup.selected_players(self.roster)
        self._show(picker.pick(self.setup.mode, players))
        self.page.navigate(RESULT)

    def pick_again(self) -> None:
        if self.result is not None:
            self._show(picker.pick(self.result.mode, self.result.candidates))

    def _show(self, result: RoundResult) -> None:
        self.result = result
        self.reveal_id += 1
        reveal_id = self.reveal_id
        self.page.run_task(self.results.reveal, self.page, result, lambda: reveal_id == self.reveal_id)

    def save(self) -> None:
        if not self.can_save:
            return
        # Handlers here are sync; run_task schedules the async save without blocking the UI.
        self.page.run_task(self._save, self.roster.players)

    async def _save(self, players: list[Player]) -> None:
        try:
            await self.store.save(players)
        except Exception:
            log.exception("Saving players failed")
            self.page.show_dialog(ft.SnackBar("Couldn't save players."))
            self.page.update()
