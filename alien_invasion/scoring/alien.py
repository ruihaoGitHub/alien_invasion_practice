import pygame

from pygame.sprite import Sprite


class Alien(Sprite):
    """A class to represent a single alien in the fleet."""

    def __init__(self, ai_game):
        """Initialize the alien and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load the alien image and set its rect attribute.
        self.image = pygame.image.load('images/alien.bmp')
        self.rect = self.image.get_rect()

        # Start each new alien near the top left of the screen.
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store the alien's exact horizontal position.
        self.x = float(self.rect.x)
        self.y = float(self.rect.y) 

        self.dying = False 
        self.drop_speed = 10 # 尸体掉落的速度（比活着的时候下沉快）

    def check_edges(self):
        """Return True if alien is at edge of screen."""
        if self.dying:
            return False

        screen_rect = self.screen.get_rect()
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)

    def update(self):
        """Move the alien."""
        if not self.dying:
            # 1. 如果还活着：正常横向移动
            self.x += (self.settings.alien_speed *
                        self.settings.fleet_direction)
            self.rect.x = self.x
        else:
            # 2. 如果被打中了：垂直坠落
            self.y += self.drop_speed
            self.rect.y = self.y