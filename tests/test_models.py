import pytest

from models import MAX_NAME_LENGTH, InvalidNameError, Player, Roster, clean_name


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
