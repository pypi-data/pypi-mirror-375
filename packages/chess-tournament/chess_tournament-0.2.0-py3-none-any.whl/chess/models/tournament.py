"""Tournament model."""

from datetime import date
from chess.models.round import Round
from .player import Player


class Tournament:
    """Represents a chess tournament."""

    def __init__(
        self,
        name: str,
        location: str,
        start_date: date,
        end_date: date,
        number_of_rounds=4,
        rounds=None,
        players=None,
        description="",
        current_round=0,
    ):
        self.name = name
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.number_of_rounds = number_of_rounds
        self.current_round = current_round
        self.players = players if players is not None else []
        self.rounds = rounds if rounds is not None else []
        self.description = description

    def to_dict(self) -> dict:
        """Converts the Tournament object to a dictionary for serialization."""
        return {
            "name": self.name,
            "location": self.location,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "number_of_rounds": self.number_of_rounds,
            "current_round": self.current_round,
            "players": [p.to_dict() for p in self.players],
            "rounds": [r.to_dict() for r in self.rounds],
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Tournament instance from a dictionary."""
        rounds = [Round.from_dict(r) for r in data["rounds"]]
        players = [Player.from_dict(p) for p in data["players"]]
        return cls(
            name=data["name"],
            location=data["location"],
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"]),
            number_of_rounds=data.get("number_of_rounds", 4),
            rounds=rounds,
            players=players,
            description=data.get("description", ""),
            current_round=data.get("current_round", 0),
        )
