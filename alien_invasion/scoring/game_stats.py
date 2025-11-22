import json
from pathlib import Path

class GameStats:
    """Track statistics for Alien Invasion."""

    def __init__(self, ai_game):
        """Initialize statistics."""
        self.settings = ai_game.settings
        self.reset_stats()

        self.game_active = False
        # High score should never be reset.
        self.high_score = self.get_saved_high_score()

    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def get_saved_high_score(self):
        """Get high score from file, if it exists."""
        path = Path('high_score.json')
        try:
            contents = path.read_text()
            return json.loads(contents)
        except FileNotFoundError:
            return 0