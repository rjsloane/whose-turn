"""Player list: add, remove, and tick who is playing this round.

The view owns no data: it reads from a `Roster` and `RoundSetup` and calls
`render()` after every change, so those are always the single source of truth.
"""

from collections.abc import Callable

import flet as ft

from models import MAX_NAME_LENGTH, InvalidNameError, Player, Roster, RoundSetup
from views.widgets import player_avatar

NAME_SIZE = 22
BUTTON_HEIGHT = 56
DIALOG_BUTTON_STYLE = ft.ButtonStyle(text_style=ft.TextStyle(size=18))


class PlayersView:
    def __init__(
        self,
        page: ft.Page,
        roster: Roster,
        setup: RoundSetup,
        on_change: Callable[[], None] | None = None,
    ) -> None:
        self.page = page
        self.roster = roster
        self.setup = setup
        self.on_change = on_change

        self.name_field = ft.TextField(
            label="Player name",
            text_size=NAME_SIZE,
            max_length=MAX_NAME_LENGTH,
            capitalization=ft.TextCapitalization.WORDS,
            on_submit=self._handle_add,
            on_change=self._clear_error,
            expand=True,
        )
        self.add_button = ft.FilledButton(
            "Add",
            icon=ft.Icons.PERSON_ADD,
            height=BUTTON_HEIGHT,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=18)),
            on_click=self._handle_add,
        )
        self.heading = ft.Text(size=18, weight=ft.FontWeight.BOLD, expand=True)
        self.all_button = ft.TextButton("All", height=48, on_click=self._select_all)
        self.none_button = ft.TextButton("None", height=48, on_click=self._select_none)
        self.player_list = ft.ListView(spacing=8, expand=True)

        self.control = ft.Column(
            [
                # Button is aligned to the text box (top), not its counter line.
                ft.Row([self.name_field, self.add_button], vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Row([self.heading, self.all_button, self.none_button]),
                self.player_list,
            ],
            expand=True,
            spacing=12,
        )
        self.render()

    # --- rendering -------------------------------------------------------

    def render(self) -> None:
        """Rebuild the list from the roster. Caller is responsible for page.update()."""
        players = self.roster.players
        playing = len(self.setup.selected_players(self.roster))
        self.heading.value = f"Players ({playing} of {len(players)} playing)" if players else "Players"
        self.all_button.visible = self.none_button.visible = len(players) > 1
        if players:
            self.player_list.controls = [self._player_row(p) for p in players]
        else:
            self.player_list.controls = [
                ft.Text("No players yet. Add someone above!", size=18, italic=True)
            ]

    def _player_row(self, player: Player) -> ft.Control:
        selected = self.setup.is_selected(player)
        return ft.Card(
            # Players sitting this round out are faded, so it's obvious at a glance.
            opacity=1.0 if selected else 0.45,
            content=ft.ListTile(
                on_click=lambda _, p=player: self._toggle(p),  # whole row is the tap target
                # A display-only tick: a real Checkbox would also handle the tap,
                # toggling twice (once for itself, once for the row).
                leading=ft.Icon(
                    ft.Icons.CHECK_BOX if selected else ft.Icons.CHECK_BOX_OUTLINE_BLANK,
                    color=ft.Colors.PRIMARY,
                    size=32,
                ),
                title=ft.Row(
                    [player_avatar(player), ft.Text(player.name, size=NAME_SIZE, expand=True)],
                    spacing=12,
                ),
                trailing=ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_size=28,
                    tooltip=f"Remove {player.name}",
                    on_click=lambda _, p=player: self._confirm_remove(p),
                ),
            )
        )

    # --- events ----------------------------------------------------------

    async def _handle_add(self, _: ft.Event) -> None:
        try:
            self.roster.add(self.name_field.value)
        except InvalidNameError as err:
            self.name_field.error = str(err)
        else:
            self.name_field.value = ""
            self.name_field.error = None
            self._changed()
        self.page.update()
        # Keep the keyboard up so several names can be typed in a row.
        await self.name_field.focus()

    def _toggle(self, player: Player) -> None:
        self.setup.toggle(player)
        self._changed()
        self.page.update()

    def _select_all(self, _: ft.Event) -> None:
        self.setup.select_all()
        self._changed()
        self.page.update()

    def _select_none(self, _: ft.Event) -> None:
        self.setup.select_none(self.roster)
        self._changed()
        self.page.update()

    def _clear_error(self, _: ft.Event) -> None:
        if self.name_field.error:
            self.name_field.error = None
            self.page.update()

    def _confirm_remove(self, player: Player) -> None:
        def remove(_: ft.Event) -> None:
            self.page.pop_dialog()
            self.roster.remove(player.id)
            self.name_field.error = None  # e.g. a "duplicate" error may no longer apply
            self._changed()
            self.page.update()

        self.page.show_dialog(
            ft.AlertDialog(
                title=ft.Text(f"Remove {player.name}?", size=24),
                actions=[
                    ft.TextButton("Cancel", height=BUTTON_HEIGHT, style=DIALOG_BUTTON_STYLE,
                                  on_click=lambda _: self.page.pop_dialog()),
                    ft.FilledButton("Remove", height=BUTTON_HEIGHT, style=DIALOG_BUTTON_STYLE,
                                    on_click=remove),
                ],
            )
        )

    def _changed(self) -> None:
        self.render()
        if self.on_change:
            self.on_change()
