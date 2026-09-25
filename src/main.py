import flet as ft

from app import WhoseTurnApp
from storage import KeyValuePlayerStore


async def main(page: ft.Page) -> None:
    page.title = "Whose Turn?"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.DEEP_PURPLE)

    # SharedPreferences is Flet 1.0's local key-value storage (Android SharedPreferences
    # on the phone). Creating it inside main registers it with this page.
    store = KeyValuePlayerStore(ft.SharedPreferences())
    await WhoseTurnApp(page, store).start()


ft.run(main)
