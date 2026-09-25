import random

import pytest

from models import Mode, Player
from picker import ordinal, pick, pick_one, pick_order

PLAYERS = [Player("Ann"), Player("Bob"), Player("Cleo"), Player("Dev")]


def test_pick_order_is_a_permutation_and_leaves_input_alone() -> None:
    original = list(PLAYERS)
    order = pick_order(PLAYERS, random.Random(1))
    assert sorted(p.id for p in order) == sorted(p.id for p in PLAYERS)
    assert PLAYERS == original


def test_pick_order_is_deterministic_with_seed() -> None:
    assert pick_order(PLAYERS, random.Random(42)) == pick_order(PLAYERS, random.Random(42))


def test_pick_order_produces_every_ordering_eventually() -> None:
    rng = random.Random(0)
    seen = {tuple(p.name for p in pick_order(PLAYERS[:3], rng)) for _ in range(500)}
    assert len(seen) == 6  # 3! orderings


def test_pick_one_returns_a_member_and_covers_everyone() -> None:
    rng = random.Random(0)
    seen = {pick_one(PLAYERS, rng).name for _ in range(200)}
    assert seen == {p.name for p in PLAYERS}


def test_pick_one_empty_raises() -> None:
    with pytest.raises(ValueError):
        pick_one([])


@pytest.mark.parametrize("mode", list(Mode))
def test_pick_result_shape(mode: Mode) -> None:
    result = pick(mode, PLAYERS, random.Random(3))
    assert result.mode is mode
    assert result.candidates == tuple(PLAYERS)
    assert result.chosen in PLAYERS
    expected_len = len(PLAYERS) if mode is Mode.ORDER else 1
    assert len(result.players) == expected_len


def test_pick_needs_two_players() -> None:
    with pytest.raises(ValueError):
        pick(Mode.WINNER, PLAYERS[:1])


@pytest.mark.parametrize(
    ("n", "expected"),
    [(1, "1st"), (2, "2nd"), (3, "3rd"), (4, "4th"), (11, "11th"), (12, "12th"),
     (13, "13th"), (21, "21st"), (22, "22nd"), (101, "101st"), (111, "111th")],
)
def test_ordinal(n: int, expected: str) -> None:
    assert ordinal(n) == expected
