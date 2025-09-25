import pygame
import sys
from config import Config
from diseño import Diseño
from robot import Robot
from world import World

# ==============================================================================
# CLASE 6: Juego (Game)
# Responsabilidad: Orquestar todo. Contiene el bucle principal, gestiona
# los eventos y le dice a las otras clases cuándo actuar.
# ==============================================================================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption("Robot Limpiador v2.0")
        self.clock = pygame.time.Clock()
        self.game_state = 'MENU'
        self.renderer = Diseño(self.screen)
        self.reset()

    def reset(self):
        self.world = World()
        self.robot = Robot(self.world.robot_start_pos[0], self.world.robot_start_pos[1])
        self.game_state = 'RUNNING'

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return False
                if event.key == pygame.K_RETURN and self.game_state == 'MENU': self.game_state = 'RUNNING'
                if event.key == pygame.K_SPACE and self.game_state in ['RUNNING', 'PAUSED']:
                    self.game_state = 'PAUSED' if self.game_state == 'RUNNING' else 'RUNNING'
                if event.key == pygame.K_r and self.game_state != 'MENU': self.reset()
        return True

    def update(self):
        if self.game_state == 'RUNNING':
            new_game_state = self.robot.update(self.world.balls, self.world.station_rect, self.world.basket_rect)
            if new_game_state:
                self.game_state = new_game_state
            self.robot.animate_move()

    def render(self):
        self.renderer.draw(self.game_state, self.world, self.robot)

if __name__ == '__main__':
    game = Game()
    game.run()