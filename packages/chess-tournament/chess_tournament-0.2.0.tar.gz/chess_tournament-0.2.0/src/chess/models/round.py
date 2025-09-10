"""This module defines the Round class for managing chess tournament rounds."""

from datetime import datetime
from .match import Match


class Round:
    """Represents a single round in a chess tournament."""

    def __init__(
        self,
        round_no: int,
        matches: list = None,
        start_time: str = None,
        end_time: str = None,
    ):
        self.round_no = round_no
        self.matches = matches if matches is not None else []
        self.start_time = (
            start_time if start_time is not None else datetime.now().isoformat()
        )
        self.end_time = end_time if end_time is not None else None

    def to_dict(self):
        """Converts the Round object to a dictionary for serialization."""
        return {
            "round_no": self.round_no,
            "matches": [m.to_dict() for m in self.matches],
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a Round instance from a dictionary."""
        matches = [Match.from_dict(m) for m in data["matches"]]
        return cls(
            round_no=data["round_no"],
            matches=matches,
            start_time=data["start_time"],
            end_time=data["end_time"],
        )

    def close(self):
        """Sets the end time of the round to the current time."""
        self.end_time = datetime.now().isoformat()
