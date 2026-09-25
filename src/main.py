import flet as ft

from models import Roster, RoundSetup
from views.home import HomeView


def main(page: ft.Page) -> None:
    page.title = "Whose Turn?"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.DEEP_PURPLE)
    page.appbar = ft.AppBar(
        title=ft.Text("Whose Turn?", size=24, weight=ft.FontWeight.BOLD),
        center_title=True,
        bgcolor=ft.Colors.PRIMARY_CONTAINER,
    )

    roster = Roster()
    setup = RoundSetup()
    home = HomeView(page, roster, setup)

    # SafeArea keeps content clear of the phone's status bar / notch.
    page.add(ft.SafeArea(home.control, expand=True))


ft.run(main)
