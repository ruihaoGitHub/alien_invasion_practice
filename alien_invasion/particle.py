import pygame
from pygame.sprite import Sprite
import random

class Particle(Sprite):
    """表示爆炸中一颗小火花的类"""
    def __init__(self, ai_game, center_pos):
        super().__init__()
        self.screen = ai_game.screen
        
        # 随机设置火花的颜色（红、橙、黄、白），模拟火焰
        colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (255, 255, 255)]
        self.color = random.choice(colors)
        
        # 随机大小 (2到5像素)
        size = random.randint(2, 5)
        self.rect = pygame.Rect(0, 0, size, size)
        
        # 设置火花产生的初始位置（即爆炸中心）
        self.rect.center = center_pos
        
        # 为了精确控制位置，使用浮点数
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        
        # 随机生成向四周飞散的速度
        # random.uniform(-5, 5) 表示在 -5 到 5 之间随机取小数
        self.x_speed = random.uniform(-5, 5)
        self.y_speed = random.uniform(-5, 5)
        
        # 生命值：火花存在多少帧后消失
        self.life = random.randint(30, 50) 

    def update(self):
        """更新火花位置"""
        self.x += self.x_speed
        self.y += self.y_speed
        
        self.rect.x = self.x
        self.rect.y = self.y
        
        # 生命值递减
        self.life -= 1
        
        # 如果生命值耗尽，从编组中删除自己
        if self.life <= 0:
            self.kill()

    def draw_particle(self):
        """绘制火花"""
        pygame.draw.rect(self.screen, self.color, self.rect)
