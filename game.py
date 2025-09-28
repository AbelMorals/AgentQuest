import pygame
import sys
from config import Config
from render import Render
from robot import Robot
from world import World
from pathfinder import Pathfinder

# ==============================================================================
# CLASE 6: Juego (Game)
# Responsabilidad: Orquestar todo. Contiene el bucle principal, gestiona
# los eventos y le dice a las otras clases cuándo actuar.
# ==============================================================================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption("Robot Limpiador v2.1")
        self.clock = pygame.time.Clock()
        self.game_state = 'MENU'
        self.renderer = Render(self.screen)
        self.pathfinder = Pathfinder()
        self.developer_mode = False
        self.dev_step_request = False  # para tecla S (paso a paso)
        self.dev_hold = False           # para tecla A (continuo)
        self.reset()

    def reset(self):
        self.world = World()
        self.robot = Robot(self.world.robot_start_pos[0], self.world.robot_start_pos[1])
        self.game_state = 'MENU'
        self.pathfinder.clear()

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
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_RETURN and self.game_state == 'MENU':
                    self.game_state = 'RUNNING'
                if event.key == pygame.K_SPACE and self.game_state in ['RUNNING', 'PAUSED']:
                    self.game_state = 'PAUSED' if self.game_state == 'RUNNING' else 'RUNNING'
                if event.key == pygame.K_r and self.game_state != 'MENU':
                    self.reset()
                if event.key == pygame.K_d and self.game_state == 'RUNNING':
                    self.developer_mode = not self.developer_mode
                if event.key == pygame.K_s and self.developer_mode and self.game_state == 'RUNNING':
                    self.dev_step_request = True  # paso único con S
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.dev_hold = False  # dejar de mantener A
        return True

    def update(self):
        if self.game_state != 'RUNNING':
            return

        # Mantener A = continuo, S = paso único
        keys = pygame.key.get_pressed()
        if self.developer_mode:
            self.dev_hold = keys[pygame.K_a]

        new_game_state = self.robot.update(
            self.world.balls,
            self.world.station_rect,
            self.world.basket_rect,
            self.pathfinder,
            developer_mode=self.developer_mode,
            dev_step_request=self.dev_step_request,
            dev_hold=self.dev_hold
        )

        # paso a paso solo una vez con S
        self.dev_step_request = False

        if new_game_state:
            self.game_state = new_game_state

        # animación normal fuera del modo desarrollador
        self.robot.animate_move(self.developer_mode)

    def render(self):
        self.renderer.draw(self.game_state, self.world, self.robot, self.developer_mode, self.pathfinder)

if __name__ == '__main__':
    game = Game()
    game.run()
