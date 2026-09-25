"""Small building blocks shared by several screens."""

import flet as ft

from models import Player

AVATAR_COLORS = [
    ft.Colors.RED_300,
    ft.Colors.ORANGE_300,
    ft.Colors.AMBER_400,
    ft.Colors.GREEN_400,
    ft.Colors.TEAL_300,
    ft.Colors.BLUE_300,
    ft.Colors.INDIGO_300,
    ft.Colors.PURPLE_300,
    ft.Colors.PINK_300,
]


def avatar_color(player: Player) -> ft.Colors:
    """A stable colour per player (same id -> same colour on every launch)."""
    return AVATAR_COLORS[sum(map(ord, player.id)) % len(AVATAR_COLORS)]


def player_avatar(player: Player, radius: int = 24) -> ft.CircleAvatar:
    # Placeholder until photos/avatars exist: the player's initial on a colour.
    return ft.CircleAvatar(
        content=ft.Text(player.name[0].upper(), size=radius * 0.85, weight=ft.FontWeight.BOLD),
        bgcolor=avatar_color(player),
        color=ft.Colors.WHITE,
        radius=radius,
    )
