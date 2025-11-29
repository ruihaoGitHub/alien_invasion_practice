import json
from pathlib import Path
import sys
import math
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet, SuperBullet
from alien import Alien
from particle import Particle


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        #加载音效
        self.bullet_sound = pygame.mixer.Sound('sounds/laserLarge_000.ogg')
        self.alien_sound = pygame.mixer.Sound('sounds/explosionCrunch_000.ogg')
        # Create an instance to store game statistics,
        #   and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.super_bullets = pygame.sprite.Group()#引入超级子弹编组
        self.aliens = pygame.sprite.Group()
        self.particles = pygame.sprite.Group() # 粒子编组

        self._create_fleet()

        # Start Alien Invasion in an inactive state.
        self.game_active = False

        # Make the Play button.
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self.particles.update() # 更新所有火花的位置和生命

            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._close_game()
                
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _close_game(self):
        """Save high score and exit."""
        #用python自带的模块存储最高分
        path = Path('high_score.json')
        contents = json.dumps(self.stats.high_score)
        path.write_text(contents)
        
        sys.exit()

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()

            # Reset the game statistics.
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            self._close_game()
            #sys.exit()
        
        # Z 键发射大招
        elif event.key == pygame.K_z:
            self._fire_super_bullet()

        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            self.bullet_sound.play()#音效

    def _fire_super_bullet(self):
        """创建一颗超级子弹，并将其加入到编组 super_bullets 中"""
        # 屏幕上只能同时存在1颗超级子弹
        if len(self.super_bullets) < 1: 
            new_bullet = SuperBullet(self)
            self.super_bullets.add(new_bullet)

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()
        self.super_bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        for bullet in self.super_bullets.copy():
            if bullet.rect.bottom <= 0:
                self.super_bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, False)

        if collisions:
            self.alien_sound.play()#sound effect
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                for alien in aliens:
                    alien.dying = True #把被射中的alien设为dying，不立马清除
            self.sb.prep_score()
            self.sb.check_high_score()

        # --- 超级子弹逻辑 (范围伤害) ---
        # 1. 检测超级子弹是否撞到了外星人
        super_collisions = pygame.sprite.groupcollide(
                self.super_bullets, self.aliens, True, False)

        if super_collisions:
            # super_collisions 是一个字典，key是子弹，value是被击中的外星人列表
            for bullet, hit_aliens in super_collisions.items():
                self.alien_sound.play()
                # 以子弹消失的位置为爆炸中心
                blast_center = bullet.rect.center
                
                # 生成爆炸特效！
                # 循环生成 50 个小火花，加入到 particles 编组中
                for _ in range(50):
                    new_particle = Particle(self, blast_center)
                    self.particles.add(new_particle)

                # 遍历所有活着的外星人，检查距离
                for alien in self.aliens.sprites():
                    if alien.dying: continue # 已经死的不管

                    # 计算外星人中心到爆炸中心的距离 (勾股定理)
                    distance = math.hypot(
                        alien.rect.centerx - blast_center[0],
                        alien.rect.centery - blast_center[1]
                    )
                    
                    # 如果距离小于爆炸半径，销毁外星人
                    if distance < self.settings.blast_radius:
                        alien.dying = True
                        self.stats.score += self.settings.alien_points
            
            self.sb.prep_score()
            self.sb.check_high_score()

        alive_aliens = [alien for alien in self.aliens if not alien.dying]
        if not alive_aliens:
            self.bullets.empty()
            self.super_bullets.empty() # 清空超级子弹
            self.aliens.empty() # 把剩下的尸体也清掉，直接进下一关
            self._create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Pause.
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions."""
        # 不再检查整个舰队的边缘
        self.aliens.update()

        #清理掉出屏幕下方的挂掉的外星人
        for alien in self.aliens.copy():
            if alien.dying and alien.rect.top >= self.settings.screen_height:
                self.aliens.remove(alien)

        alive_aliens_group = pygame.sprite.Group([a for a in self.aliens if not a.dying])
        
        if pygame.sprite.spritecollideany(self.ship, alive_aliens_group):
            self._ship_hit()
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            # 只有活着的到了底部才算输
            if not alien.dying and alien.rect.bottom >= self.settings.screen_height:
                self._ship_hit()
                break

    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and keep adding aliens until there's no room left.
        # Spacing between aliens is one alien width and one alien height.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            # Finished a row; reset x value, and increment y value.
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
            alien.y = float(alien.rect.y) 
            
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        
        # 绘制所有超级子弹
        for bullet in self.super_bullets.sprites():
            bullet.draw_bullet()

        self.ship.blitme()
        self.aliens.draw(self.screen)
        
        # 绘制火花特效
        for particle in self.particles.sprites():
            particle.draw_particle()

        # Draw the score information.
        self.sb.show_score()

        # Draw the play button if the game is inactive.
        if not self.game_active:
            self.play_button.draw_button()

        pygame.display.flip()


if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()