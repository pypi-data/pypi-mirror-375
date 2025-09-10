"""Model for representing a chess match between two players."""

import logging
from .player import Player

logger = logging.getLogger(__name__)


class Match:
    """Represents a match between two players."""

    def __init__(self, player_white: Player, player_black: Player, score: list):
        """Initialize a Match instance with two players and their scores.

        Args:
            player_white: The first player.
            player_black: The second player.
            score: A list with two elements [score1, score2].
        """
        self.player_white = player_white
        self.player_black = player_black
        self.score = score  # [score1, score2]
        logger.debug(
            "Creating Match: %s vs %s, score: %s", player_white, player_black, score
        )

    def to_dict(self):
        """Converts the Match object to a dictionary for serialization."""
        logger.debug("Converting Match to dict")
        return {
            "player_white": self.player_white.to_dict(),
            "player_black": self.player_black.to_dict(),
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Match instance from a dictionary."""
        player_white = Player.from_dict(data["player_white"])
        player_black = Player.from_dict(data["player_black"])
        logger.debug("Creating Match from dict: %s", data)
        return cls(
            player_white=player_white,
            player_black=player_black,
            score=data["score"],
        )
