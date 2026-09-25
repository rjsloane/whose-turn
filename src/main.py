import flet as ft

from models import Roster
from views.players import PlayersView


def main(page: ft.Page) -> None:
    page.title = "Whose Turn?"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.DEEP_PURPLE)
    page.appbar = ft.AppBar(
        title=ft.Text("Whose Turn?", size=24, weight=ft.FontWeight.BOLD),
        center_title=True,
        bgcolor=ft.Colors.PRIMARY_CONTAINER,
    )

    roster = Roster()
    players_view = PlayersView(page, roster)

    # SafeArea keeps content clear of the phone's status bar / notch.
    page.add(ft.SafeArea(players_view.control, expand=True))


ft.run(main)
