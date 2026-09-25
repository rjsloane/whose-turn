"""Data model for Whose Turn?  Pure Python: no Flet imports, so it's unit-testable."""

import uuid
from dataclasses import dataclass, field
from enum import Enum

MAX_NAME_LENGTH = 20
MIN_PLAYERS = 2


def _new_id() -> str:
    return uuid.uuid4().hex


@dataclass
class Player:
    """A person who can take part in a round.

    `id` is stable even if the name changes later, so other data (groups, stored
    selections) can refer to players safely.
    """

    name: str
    id: str = field(default_factory=_new_id)
    photo_path: str | None = None  # future: photo copied into app storage
    avatar: str | None = None  # future: built-in avatar key or emoji


class InvalidNameError(ValueError):
    """Raised when a player name can't be used. The message is shown to the user."""


def clean_name(raw: str) -> str:
    """Trim surrounding whitespace and collapse runs of inner whitespace."""
    return " ".join(raw.split())


class Roster:
    """The list of known players, in the order they were added."""

    def __init__(self, players: list[Player] | None = None) -> None:
        self._players: list[Player] = list(players or [])

    @property
    def players(self) -> list[Player]:
        return list(self._players)

    def __len__(self) -> int:
        return len(self._players)

    def validate_name(self, raw: str) -> str:
        """Return the cleaned name, or raise InvalidNameError with a friendly message."""
        name = clean_name(raw)
        if not name:
            raise InvalidNameError("Please type a name first.")
        if len(name) > MAX_NAME_LENGTH:
            raise InvalidNameError(f"That name is too long (max {MAX_NAME_LENGTH} letters).")
        if (existing := self.find_by_name(name)) is not None:
            raise InvalidNameError(f"{existing.name} is already on the list!")
        return name

    def add(self, raw_name: str) -> Player:
        player = Player(name=self.validate_name(raw_name))
        self._players.append(player)
        return player

    def remove(self, player_id: str) -> Player:
        player = self.get(player_id)
        if player is None:
            raise KeyError(player_id)
        self._players.remove(player)
        return player

    def get(self, player_id: str) -> Player | None:
        return next((p for p in self._players if p.id == player_id), None)

    def find_by_name(self, name: str) -> Player | None:
        """Case-insensitive lookup (casefold also handles e.g. German ß)."""
        key = clean_name(name).casefold()
        return next((p for p in self._players if p.name.casefold() == key), None)


class Mode(Enum):
    """What a round picks."""

    ORDER = "order"
    WINNER = "winner"
    LOSER = "loser"


@dataclass
class RoundSetup:
    """Who is taking part in the next round, and what to pick.

    Stores who is *left out* rather than who is in, so everyone is included by
    default, newly added players join automatically, and removed players simply
    stop mattering.
    """

    mode: Mode = Mode.ORDER
    excluded_ids: set[str] = field(default_factory=set)

    def is_selected(self, player: Player) -> bool:
        return player.id not in self.excluded_ids

    def set_selected(self, player: Player, selected: bool) -> None:
        if selected:
            self.excluded_ids.discard(player.id)
        else:
            self.excluded_ids.add(player.id)

    def toggle(self, player: Player) -> None:
        self.set_selected(player, not self.is_selected(player))

    def select_all(self) -> None:
        self.excluded_ids.clear()

    def select_none(self, roster: Roster) -> None:
        self.excluded_ids = {p.id for p in roster.players}

    def selected_players(self, roster: Roster) -> list[Player]:
        return [p for p in roster.players if self.is_selected(p)]

    def can_pick(self, roster: Roster) -> bool:
        return len(self.selected_players(roster)) >= MIN_PLAYERS

    def pick_blocker(self, roster: Roster) -> str | None:
        """Why picking isn't possible yet (friendly text), or None if it is."""
        if len(roster) < MIN_PLAYERS:
            return f"Add at least {MIN_PLAYERS} players to start."
        selected = len(self.selected_players(roster))
        if selected < MIN_PLAYERS:
            short = MIN_PLAYERS - selected
            return f"Tick {short} more player{'s' if short > 1 else ''} to play."
        return None
