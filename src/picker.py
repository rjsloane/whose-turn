"""Picking logic. Pure Python: pass a seeded `random.Random` for repeatable results."""

import random
from collections.abc import Sequence
from dataclasses import dataclass

from models import MIN_PLAYERS, Mode, Player


@dataclass(frozen=True)
class RoundResult:
    """Outcome of one pick.

    `players` is the full turn order for ORDER, or a single player for WINNER/LOSER.
    `candidates` is who took part, so "Pick again" can reuse exactly the same group.
    """

    mode: Mode
    players: tuple[Player, ...]
    candidates: tuple[Player, ...]

    @property
    def chosen(self) -> Player:
        """The first player: who goes first, the winner, or the loser."""
        return self.players[0]


def pick_order(players: Sequence[Player], rng: random.Random | None = None) -> list[Player]:
    """Return a shuffled copy of `players` (the input is left unchanged)."""
    order = list(players)
    (rng or random).shuffle(order)
    return order


def pick_one(players: Sequence[Player], rng: random.Random | None = None) -> Player:
    if not players:
        raise ValueError("Need at least one player to pick from.")
    return (rng or random).choice(list(players))


def pick(mode: Mode, players: Sequence[Player], rng: random.Random | None = None) -> RoundResult:
    if len(players) < MIN_PLAYERS:
        raise ValueError(f"Need at least {MIN_PLAYERS} players, got {len(players)}.")
    # Winner and loser are both "choose one at random"; only the presentation differs.
    chosen = pick_order(players, rng) if mode is Mode.ORDER else [pick_one(players, rng)]
    return RoundResult(mode=mode, players=tuple(chosen), candidates=tuple(players))


def ordinal(n: int) -> str:
    """1 -> '1st', 2 -> '2nd', 11 -> '11th', 22 -> '22nd'."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"
