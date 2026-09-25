import asyncio
import json
from typing import Any

from models import Player
from storage import KeyValuePlayerStore, players_from_json, players_to_json


class FakeBackend:
    def __init__(self, data: dict[str, Any] | None = None) -> None:
        self.data = dict(data or {})
        self.writes = 0

    async def get(self, key: str) -> Any:
        return self.data.get(key)

    async def set(self, key: str, value: str) -> bool:
        self.data[key] = value
        self.writes += 1
        return True


def test_json_round_trip_keeps_all_fields() -> None:
    players = [Player("Ann"), Player("Zoë", photo_path="/data/p.jpg", avatar="🦊")]
    assert players_from_json(players_to_json(players)) == players


def test_json_has_version() -> None:
    assert json.loads(players_to_json([]))["version"] == 1


def test_from_json_tolerates_bad_data() -> None:
    assert players_from_json(None) == []
    assert players_from_json("") == []
    assert players_from_json("not json") == []
    assert players_from_json('{"nope": 1}') == []
    assert players_from_json('[1, 2]') == []
    good = players_to_json([Player("Ann", id="a")])
    mixed = good.replace('"players": [', '"players": [{"id": "x"}, 5, ')
    assert players_from_json(mixed) == [Player("Ann", id="a")]


def test_store_save_and_load() -> None:
    backend = FakeBackend()
    players = [Player("Ann"), Player("Bob")]

    async def run() -> list[Player]:
        await KeyValuePlayerStore(backend).save(players)
        return await KeyValuePlayerStore(backend).load()  # fresh store, like a relaunch

    assert asyncio.run(run()) == players


def test_store_load_empty() -> None:
    assert asyncio.run(KeyValuePlayerStore(FakeBackend()).load()) == []


def test_store_skips_unchanged_writes() -> None:
    backend = FakeBackend()
    store = KeyValuePlayerStore(backend)
    players = [Player("Ann")]

    async def run() -> None:
        await store.load()
        await store.save(players)
        await store.save(players)
        await store.save(players + [Player("Bob")])

    asyncio.run(run())
    assert backend.writes == 2
