import pygame
import random
from config import Config

# ==============================================================================
# CLASE 4: Mundo (World)
# Responsabilidad: Contener y gestionar todos los objetos del escenario:
# las pelotas, la estación y la canasta.
# ==============================================================================
class World:
    def __init__(self):
        self.station_rect = pygame.Rect(Config.GRID_SIZE, Config.GRID_SIZE + Config.HUD_HEIGHT, Config.STATION_SIZE, Config.STATION_SIZE)
        self.basket_rect = pygame.Rect(Config.WIDTH - Config.BASKET_SIZE - Config.GRID_SIZE, Config.HEIGHT - Config.BASKET_SIZE - Config.GRID_SIZE, Config.BASKET_SIZE, Config.BASKET_SIZE)
        self.balls = []
        self.robot_start_pos = (0, 0)
        self.generate_layout()

    def generate_layout(self):
        # Crea una disposición aleatoria para los objetos.
        while True:
            x = random.randrange(0, Config.WIDTH, Config.GRID_SIZE)
            y = random.randrange(Config.HUD_HEIGHT, Config.HEIGHT, Config.GRID_SIZE)
            robot_r = pygame.Rect(x, y, Config.GRID_SIZE, Config.GRID_SIZE)
            if not robot_r.colliderect(self.station_rect) and not robot_r.colliderect(self.basket_rect):
                self.robot_start_pos = (x, y)
                break

        self.balls = []
        obstacles = [self.station_rect, self.basket_rect, robot_r]
        while len(self.balls) < Config.NUM_BALLS:
            ball_x = random.randrange(0, Config.WIDTH, Config.GRID_SIZE) + Config.GRID_SIZE // 2
            ball_y = random.randrange(Config.HUD_HEIGHT, Config.HEIGHT, Config.GRID_SIZE) + Config.GRID_SIZE // 2
            ball_center = (ball_x, ball_y)
            ball_r = pygame.Rect(ball_x - Config.GRID_SIZE//2, ball_y - Config.GRID_SIZE//2, Config.GRID_SIZE, Config.GRID_SIZE)
            if not any(ball_r.colliderect(obs) for obs in obstacles) and ball_center not in self.balls:
                self.balls.append(ball_center)
                obstacles.append(ball_r)
