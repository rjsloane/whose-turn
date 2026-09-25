"""Bottom panel: choose what to pick, and the big Pick! button."""

from collections.abc import Callable

import flet as ft

from models import Mode, Roster, RoundSetup

MODE_LABELS: dict[Mode, tuple[str, ft.IconData]] = {
    Mode.ORDER: ("Order", ft.Icons.FORMAT_LIST_NUMBERED),
    Mode.WINNER: ("Winner", ft.Icons.EMOJI_EVENTS),
    Mode.LOSER: ("Loser", ft.Icons.SENTIMENT_DISSATISFIED),
}
MODE_HINTS: dict[Mode, str] = {
    Mode.ORDER: "Shuffle everyone into a turn order",
    Mode.WINNER: "Pick one lucky winner",
    Mode.LOSER: "Pick one unlucky loser",
}


class RoundPanel:
    def __init__(
        self,
        page: ft.Page,
        roster: Roster,
        setup: RoundSetup,
        on_pick: Callable[[], None],
    ) -> None:
        self.page = page
        self.roster = roster
        self.setup = setup
        self.on_pick = on_pick

        self.mode_picker = ft.SegmentedButton(
            segments=[
                ft.Segment(value=mode.value, label=label, icon=icon)
                for mode, (label, icon) in MODE_LABELS.items()
            ],
            selected=[setup.mode.value],
            show_selected_icon=False,  # saves width on narrow phones
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=18)),
            on_change=self._mode_changed,
        )
        self.hint = ft.Text(size=16, text_align=ft.TextAlign.CENTER)
        self.pick_button = ft.FilledButton(
            "Pick!",
            icon=ft.Icons.CASINO,
            height=72,
            expand=True,
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(size=28, weight=ft.FontWeight.BOLD),
                shape=ft.RoundedRectangleBorder(radius=36),
            ),
            on_click=lambda _: self.on_pick(),
        )
        self.control = ft.Column(
            [
                ft.Row([self.mode_picker], alignment=ft.MainAxisAlignment.CENTER),
                self.hint,
                ft.Row([self.pick_button]),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        self.render()

    def render(self) -> None:
        """Sync controls to state. Caller is responsible for page.update()."""
        self.mode_picker.selected = [self.setup.mode.value]
        blocker = self.setup.pick_blocker(self.roster)
        self.pick_button.disabled = blocker is not None
        # When picking isn't possible, the hint explains why instead.
        self.hint.value = blocker or MODE_HINTS[self.setup.mode]
        self.hint.color = ft.Colors.ERROR if blocker else None

    def _mode_changed(self, _: ft.Event) -> None:
        self.setup.mode = Mode(self.mode_picker.selected[0])
        self.render()
        self.page.update()
