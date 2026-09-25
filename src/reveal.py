"""Timing and "teaser" names for the shuffling moment before a result appears.

Pure Python so it's testable; the results view just plays these frames.
"""

import random
from collections.abc import Sequence

from models import Player

REVEAL_STEPS = 14
FIRST_DELAY = 0.04  # seconds; starts fast...
LAST_DELAY = 0.22  # ...and slows down like a wheel coming to a stop


def reveal_delays(
    steps: int = REVEAL_STEPS, first: float = FIRST_DELAY, last: float = LAST_DELAY
) -> list[float]:
    """Delays that grow from `first` to `last` (ease-out). About 1.3s in total by default."""
    if steps <= 1:
        return [last] * steps
    return [first + (last - first) * (i / (steps - 1)) ** 2 for i in range(steps)]


def teaser_players(
    candidates: Sequence[Player],
    final: Player,
    steps: int = REVEAL_STEPS,
    rng: random.Random | None = None,
) -> list[Player]:
    """Random names to flash before the result.

    With 2+ candidates, no name shows twice in a row and the last teaser isn't
    the final pick, so the result visibly "lands" on a new name.
    """
    rng = rng or random.Random()
    pool = list(candidates)
    if len(pool) < 2:
        return pool[:1] * steps
    # Build backwards from the last frame: each frame then only has to differ
    # from the one after it, which is always possible with 2+ players.
    frames: list[Player] = []
    avoid = final.id
    for _ in range(steps):
        frame = rng.choice([p for p in pool if p.id != avoid])
        frames.append(frame)
        avoid = frame.id
    frames.reverse()
    return frames
