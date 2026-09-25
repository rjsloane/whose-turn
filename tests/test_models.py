import pytest

from models import MAX_NAME_LENGTH, InvalidNameError, Mode, Player, Roster, RoundSetup, clean_name


def test_player_ids_are_unique_and_optional_fields_default_to_none() -> None:
    a, b = Player("Ann"), Player("Ann")
    assert a.id != b.id
    assert a.photo_path is None and a.avatar is None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("  Ann ", "Ann"), ("Mary   Jane", "Mary Jane"), ("\tBob\n", "Bob"), ("   ", "")],
)
def test_clean_name(raw: str, expected: str) -> None:
    assert clean_name(raw) == expected


def test_add_trims_and_keeps_insertion_order() -> None:
    roster = Roster()
    roster.add("  Ann ")
    roster.add("Bob")
    assert [p.name for p in roster.players] == ["Ann", "Bob"]
    assert len(roster) == 2


@pytest.mark.parametrize("raw", ["", "   ", "\t\n"])
def test_add_rejects_blank(raw: str) -> None:
    roster = Roster()
    with pytest.raises(InvalidNameError, match="type a name"):
        roster.add(raw)
    assert len(roster) == 0


@pytest.mark.parametrize("dupe", ["ann", "ANN", "  Ann  ", "aNn"])
def test_add_rejects_case_insensitive_duplicates(dupe: str) -> None:
    roster = Roster()
    roster.add("Ann")
    with pytest.raises(InvalidNameError, match="Ann is already"):
        roster.add(dupe)
    assert len(roster) == 1


def test_add_rejects_too_long() -> None:
    roster = Roster()
    with pytest.raises(InvalidNameError, match="too long"):
        roster.add("x" * (MAX_NAME_LENGTH + 1))
    roster.add("x" * MAX_NAME_LENGTH)


def test_remove() -> None:
    roster = Roster()
    ann = roster.add("Ann")
    bob = roster.add("Bob")
    assert roster.remove(ann.id) is ann
    assert roster.players == [bob]
    # Name is free again after removal.
    roster.add("ann")


def test_remove_unknown_raises() -> None:
    with pytest.raises(KeyError):
        Roster().remove("nope")


def test_players_returns_copy() -> None:
    roster = Roster()
    roster.add("Ann")
    roster.players.clear()
    assert len(roster) == 1


def test_find_by_name() -> None:
    roster = Roster([Player("Ann")])
    assert roster.find_by_name(" ANN ") is not None
    assert roster.find_by_name("Bob") is None


# --- RoundSetup ---------------------------------------------------------------


def _roster(*names: str) -> Roster:
    roster = Roster()
    for name in names:
        roster.add(name)
    return roster


def test_round_setup_defaults() -> None:
    setup = RoundSetup()
    assert setup.mode is Mode.ORDER
    roster = _roster("Ann", "Bob")
    assert setup.selected_players(roster) == roster.players


def test_new_players_are_selected_automatically() -> None:
    roster = _roster("Ann", "Bob")
    setup = RoundSetup()
    setup.toggle(roster.players[0])
    cleo = roster.add("Cleo")
    assert [p.name for p in setup.selected_players(roster)] == ["Bob", "Cleo"]
    assert setup.is_selected(cleo)


def test_toggle_and_set_selected() -> None:
    roster = _roster("Ann")
    ann = roster.players[0]
    setup = RoundSetup()
    setup.toggle(ann)
    assert not setup.is_selected(ann)
    setup.toggle(ann)
    assert setup.is_selected(ann)
    setup.set_selected(ann, False)
    setup.set_selected(ann, False)
    assert not setup.is_selected(ann)


def test_select_all_and_none() -> None:
    roster = _roster("Ann", "Bob", "Cleo")
    setup = RoundSetup()
    setup.select_none(roster)
    assert setup.selected_players(roster) == []
    setup.select_all()
    assert len(setup.selected_players(roster)) == 3


def test_removed_player_no_longer_counts() -> None:
    roster = _roster("Ann", "Bob", "Cleo")
    setup = RoundSetup()
    roster.remove(roster.players[0].id)
    assert [p.name for p in setup.selected_players(roster)] == ["Bob", "Cleo"]


@pytest.mark.parametrize(
    ("names", "deselect", "can_pick", "blocker"),
    [
        ((), 0, False, "Add at least 2 players"),
        (("Ann",), 0, False, "Add at least 2 players"),
        (("Ann", "Bob"), 0, True, None),
        (("Ann", "Bob"), 1, False, "Tick 1 more player to play."),
        (("Ann", "Bob", "Cleo"), 3, False, "Tick 2 more players to play."),
        (("Ann", "Bob", "Cleo"), 1, True, None),
    ],
)
def test_can_pick_and_blocker(
    names: tuple[str, ...], deselect: int, can_pick: bool, blocker: str | None
) -> None:
    roster = _roster(*names)
    setup = RoundSetup()
    for player in roster.players[:deselect]:
        setup.toggle(player)
    assert setup.can_pick(roster) is can_pick
    message = setup.pick_blocker(roster)
    if blocker is None:
        assert message is None
    else:
        assert message is not None and message.startswith(blocker)
