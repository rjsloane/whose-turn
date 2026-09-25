import random

import pytest

from models import Player
from reveal import reveal_delays, teaser_players

ANN, BOB, CLEO = Player("Ann"), Player("Bob"), Player("Cleo")


def test_delays_slow_down_and_stay_quick() -> None:
    delays = reveal_delays()
    assert delays == sorted(delays)
    assert delays[0] < delays[-1]
    assert 0.8 <= sum(delays) <= 2.0  # quick enough for impatient kids


@pytest.mark.parametrize("steps", [0, 1])
def test_delays_edge_cases(steps: int) -> None:
    assert len(reveal_delays(steps)) == steps


@pytest.mark.parametrize("seed", range(20))
def test_teasers_no_repeats_and_dont_end_on_final(seed: int) -> None:
    frames = teaser_players([ANN, BOB], final=BOB, steps=10, rng=random.Random(seed))
    assert len(frames) == 10
    assert all(a.id != b.id for a, b in zip(frames, frames[1:]))
    assert frames[-1] is not BOB


def test_teasers_use_everyone_eventually() -> None:
    frames = teaser_players([ANN, BOB, CLEO], final=ANN, steps=50, rng=random.Random(0))
    assert {p.name for p in frames} == {"Ann", "Bob", "Cleo"}


def test_teasers_single_candidate() -> None:
    assert teaser_players([ANN], final=ANN, steps=3) == [ANN, ANN, ANN]
