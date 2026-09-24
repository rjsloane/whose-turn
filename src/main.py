import flet as ft


def main(page: ft.Page):
    page.title = "Whose Turn?"

    greeting = ft.Text("Hello, world!", size=30)

    def on_click(e):
        greeting.value = "Hello, kids!"
        page.update()

    page.add(
        greeting,
        ft.Button("Press me", on_click=on_click),
    )


ft.run(main)