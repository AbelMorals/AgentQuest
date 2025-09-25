import math
import pygame
from config import Config
from pathfinder import Pathfinder


# ==============================================================================
# CLASE 3: Robot (Lógica)
# Responsabilidad: Toda la "inteligencia" y el estado del robot. Decide
# QUÉ hacer (su objetivo) y gestiona su estado interno (batería, etc.).
# ==============================================================================
class Robot:
    @staticmethod
    def is_fully_contained(rect1, rect2):
        return rect1.left >= rect2.left and rect1.right <= rect2.right and \
               rect1.top >= rect2.top and rect1.bottom <= rect2.bottom

    @staticmethod
    def find_nearest_ball(robot_pos, ball_list):
        if not ball_list: return None
        return min(ball_list, key=lambda ball: abs(ball[0] - robot_pos[0]) + abs(ball[1] - robot_pos[1]))

    def __init__(self, pos_x, pos_y):
        self.rect = pygame.Rect(pos_x, pos_y, Config.GRID_SIZE, Config.GRID_SIZE)
        self.charge = Config.MAX_CHARGE
        self.state = 'SEARCHING'
        self.is_carrying = False
        self.target_ball = None
        self.collected = 0
        self.last_decision = 0
        self.is_moving = False
        self.target_pixel_x = pos_x
        self.target_pixel_y = pos_y
        self.current_path = []
        self.stuck_counter = 0

    def update(self, balls, station_rect, basket_rect):
        if self.charge <= 0 and self.state != 'DEAD':
            self.state = 'DEAD'
        if self.state == 'DEAD':
            return None

        current_time = pygame.time.get_ticks()
        if self.is_moving or current_time - self.last_decision < Config.robot_decision_cooldown:
            return None 

        self.last_decision = current_time

        if self.state == 'RECHARGING':
            if self.charge < Config.MAX_CHARGE:
                self.charge += Config.RECHARGE_RATE
            else:
                self.charge = Config.MAX_CHARGE
                self.state = 'SEARCHING'
            return None

        if not self.current_path:
            self._check_emergency_battery(balls, station_rect, basket_rect)
            
            target_pos = self._get_target_pos(balls, basket_rect, station_rect)
            if target_pos:
                # Define los obstáculos dependiendo del objetivo
                obstacles = set(balls)
                if self.state == 'SEARCHING':
                    # Si busca una pelota, la estación y la canasta también son obstáculos
                    obstacles.add(station_rect.center)
                    obstacles.add(basket_rect.center)
                    if self.target_ball in obstacles:
                        obstacles.remove(self.target_ball)
                
                path = Pathfinder.a_star(self.rect.center, target_pos, obstacles)
                if path is not None:
                    self.current_path = path
                    self.stuck_counter = 0
                else:
                    self.stuck_counter += 1
                    if self.stuck_counter >= Config.MAX_STUCK_TURNS:
                        return 'GAME_OVER_STUCK' 

        if self.current_path:
            next_step = self.current_path.pop(0)
            self.target_pixel_x = next_step[0] - Config.GRID_SIZE // 2
            self.target_pixel_y = next_step[1] - Config.GRID_SIZE // 2
            self.is_moving = True
            self.charge -= Config.CHARGE_PER_MOVE

        if not self.is_moving and not self.current_path:
             return self._handle_arrival(balls, basket_rect, station_rect)

        return None

    def animate_move(self):
        if not self.is_moving or self.state == 'DEAD': return
        
        if self.rect.x != self.target_pixel_x:
            direction = 1 if self.target_pixel_x > self.rect.x else -1
            self.rect.x += Config.ROBOT_ANIMATION_SPEED * direction
            if (direction == 1 and self.rect.x >= self.target_pixel_x) or (direction == -1 and self.rect.x <= self.target_pixel_x):
                self.rect.x = self.target_pixel_x
        elif self.rect.y != self.target_pixel_y:
            direction = 1 if self.target_pixel_y > self.rect.y else -1
            self.rect.y += Config.ROBOT_ANIMATION_SPEED * direction
            if (direction == 1 and self.rect.y >= self.target_pixel_y) or (direction == -1 and self.rect.y <= self.target_pixel_y):
                self.rect.y = self.target_pixel_y
        else:
            self.is_moving = False

    # --- MÉTODO DE DECISIÓN COMPLETAMENTE REHECHO ---
    def _get_target_pos(self, balls, basket_rect, station_rect):
        """Determina el objetivo más óptimo Y ALCANZABLE."""
        if self.state == 'COLLECTING': return basket_rect.center
        if self.state == 'CHARGING': return station_rect.center
        
        if self.state == 'SEARCHING' and balls:
            # Ordena las pelotas de la más cercana a la más lejana
            sorted_balls = sorted(balls, key=lambda ball: abs(ball[0] - self.rect.centerx) + abs(ball[1] - self.rect.centery))
            
            # Busca la primera pelota a la que se pueda trazar un camino
            for ball in sorted_balls:
                obstacles = set(balls) | {station_rect.center, basket_rect.center}
                obstacles.remove(ball)
                
                # Comprueba si existe un camino antes de decidirse
                if Pathfinder.a_star(self.rect.center, ball, obstacles) is not None:
                    self.target_ball = ball
                    return self.target_ball # Devuelve la primera pelota alcanzable
        
        return None # No hay objetivos o ninguno es alcanzable

    def _handle_arrival(self, balls, basket_rect, station_rect):
        if self.state == 'SEARCHING' and not self.is_carrying:
            if self.target_ball and self.rect.collidepoint(self.target_ball):
                 balls.remove(self.target_ball)
                 self.is_carrying = True
                 self.state = 'COLLECTING'
                 self.target_ball = None # Limpia el objetivo anterior
        elif self.state == 'COLLECTING':
             if Robot.is_fully_contained(self.rect, basket_rect):
                self.collected += 1
                self.is_carrying = False
                if self.collected == Config.NUM_BALLS: return 'GAME_OVER'
                else: self.state = 'SEARCHING'
        elif self.state == 'CHARGING':
             if Robot.is_fully_contained(self.rect, station_rect):
                self.state = 'RECHARGING'
        return None
    
    def _check_emergency_battery(self, balls, basket_rect, station_rect):
        if self.charge <= Config.EMERGENCY_CHARGE and self.state not in ['CHARGING', 'RECHARGING']:
            if self.is_carrying:
                balls.append(self.rect.center)
                self.is_carrying = False
            self.state = 'CHARGING'
            self.current_path = []