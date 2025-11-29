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
        self.original_image = pygame.image.load('images/alien.bmp') 
        self.image = self.original_image 
        self.rect = self.image.get_rect()

        # Start each new alien near the top left of the screen.
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store the alien's exact horizontal position.
        self.x = float(self.rect.x)
        self.y = float(self.rect.y) 

        # 每个外星人拥有独立的移动方向
        # 1 表示向右，-1 表示向左
        self.direction = 1

        self.dying = False 
        self.drop_speed = 10 # 被击中外星人掉落的速度（比活着的时候下沉快）
        self.angle = 0 


    def check_edges(self):
        """Return True if alien is at edge of screen."""
        if self.dying:
            return False

        screen_rect = self.screen.get_rect()
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)

    def update(self):
        """Move the alien."""
        if not self.dying:
            # 如果还活着：正常横向移动
            # 在移动前先检查这个外星人是否撞墙
            if self.check_edges():
                # 撞墙了：反转自己的方向
                self.direction *= -1
                # 撞墙了：自己下落
                self.rect.y += self.settings.fleet_drop_speed
                
                # 防止它卡在边缘
                self.x += (self.settings.alien_speed * self.direction)
            else:
                # 没撞墙：按当前方向继续移动
                self.x += (self.settings.alien_speed * self.direction)

            self.rect.x = self.x
            self.y = float(self.rect.y) 
        else:
             # 被打中后：旋转并下落
            self._spin_fall()

    def _spin_fall(self):
        """处理旋转下落"""
        self.angle += 5 # 每次转5度，数字越大转越快
        
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        
        # 计算下落后的新中心位置
        # 先获取当前的中心点
        old_center = self.rect.center
        new_center_y = old_center[1] + self.drop_speed
        
        # 获取旋转后新的 rect，并强制将其中心设置到正确的位置
        self.rect = self.image.get_rect()
        self.rect.center = (old_center[0], new_center_y)
        
        self.y = float(self.rect.y)