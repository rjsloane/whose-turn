"""Persistence for the player list.

The app talks to a `PlayerStore`; today that's `KeyValuePlayerStore` backed by
Flet's `SharedPreferences`, but anything with async `get`/`set` works (tests use
an in-memory dict). No Flet import here: main.py hands in the Flet object.
"""

import json
import logging
from typing import Any, Protocol

from models import Player

log = logging.getLogger(__name__)

# SharedPreferences is shared by every Flet app on a device, so namespace our keys.
PLAYERS_KEY = "whose_turn.players"
FORMAT_VERSION = 1


class KeyValueBackend(Protocol):
    async def get(self, key: str) -> Any: ...
    async def set(self, key: str, value: str) -> Any: ...


class PlayerStore(Protocol):
    async def load(self) -> list[Player]: ...
    async def save(self, players: list[Player]) -> None: ...


def players_to_json(players: list[Player]) -> str:
    # A version number lets future releases migrate old data (e.g. adding groups).
    data = {
        "version": FORMAT_VERSION,
        "players": [
            {"id": p.id, "name": p.name, "photo_path": p.photo_path, "avatar": p.avatar}
            for p in players
        ],
    }
    return json.dumps(data, ensure_ascii=False)


def players_from_json(text: str | None) -> list[Player]:
    """Parse stored data. Bad or missing data gives an empty list rather than a crash."""
    if not text:
        return []
    try:
        data = json.loads(text)
        items = data["players"]
    except (ValueError, KeyError, TypeError):
        log.warning("Ignoring unreadable player data")
        return []
    players: list[Player] = []
    for item in items:
        try:
            players.append(
                Player(
                    name=str(item["name"]),
                    id=str(item["id"]),
                    photo_path=item.get("photo_path"),
                    avatar=item.get("avatar"),
                )
            )
        except (KeyError, TypeError, AttributeError):
            log.warning("Skipping unreadable player entry: %r", item)
    return players


class KeyValuePlayerStore:
    def __init__(self, backend: KeyValueBackend, key: str = PLAYERS_KEY) -> None:
        self.backend = backend
        self.key = key
        self._last_saved: str | None = None

    async def load(self) -> list[Player]:
        text = await self.backend.get(self.key)
        self._last_saved = text if isinstance(text, str) else None
        return players_from_json(self._last_saved)

    async def save(self, players: list[Player]) -> None:
        text = players_to_json(players)
        if text == self._last_saved:
            return  # e.g. only ticks changed: nothing to write
        await self.backend.set(self.key, text)
        self._last_saved = text
