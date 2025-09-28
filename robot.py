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
        self.is_pathfinding = False
        self.dev_unlocked = False

    def update(self, balls, station_rect, basket_rect, pathfinder: Pathfinder,
               developer_mode=False, dev_step_request=False, dev_hold=False):
        """Devuelve nuevo estado de juego si aplica (GAME_OVER, GAME_OVER_STUCK...), o None."""
        if self.charge <= 0 and self.state != 'DEAD':
            self.state = 'DEAD'
        if self.state == 'DEAD':
            return None

        # En modo desarrollador avanzamos SOLO si se pide (tecla A) o se mantiene A pulsada.
        if developer_mode:
            if not (dev_hold or dev_step_request):
                # no hacemos pasos automáticos en modo desarrollador si el usuario no lo pide
                return None
        else:
            # en modo normal respetamos cooldown y si está moviéndose no tomamos nueva decisión
            current_time = pygame.time.get_ticks()
            if self.is_moving or current_time - self.last_decision < Config.robot_decision_cooldown:
                return None
            self.last_decision = current_time

        # RECHARGING
        if self.state == 'RECHARGING':
            if self.charge < Config.MAX_CHARGE:
                self.charge += Config.RECHARGE_RATE
            else:
                self.charge = Config.MAX_CHARGE
                self.state = 'SEARCHING'
            return None

        # 1) Si estamos en una búsqueda A* paso a paso (modo desarrollador)
        if self.is_pathfinding:
            # en modo desarrollador: avanzamos un paso si el usuario lo pidió (o mantiene A)
            if developer_mode:
                if dev_hold or dev_step_request:
                    result = pathfinder.step()
                    if isinstance(result, list):
                        self.current_path = result
                        pathfinder.final_path = [(p[0] // Config.GRID_SIZE, p[1] // Config.GRID_SIZE) for p in result]
                        self.is_pathfinding = False
                        self.stuck_counter = 0
                    elif result == "NO_PATH":
                        self.is_pathfinding = False
                        self.stuck_counter += 1
                        if self.stuck_counter >= Config.MAX_STUCK_TURNS:
                            return 'GAME_OVER_STUCK'
                    # si es "SEARCHING", simplemente mostramos la pizarra y esperamos más pasos
            else:
                # no debería entrar aquí en modo normal (no usamos step en modo normal)
                pass
            return None  # en modo desarrollador sólo procesamos la búsqueda con pasos

        # 2) Si no tenemos ruta actual, decidimos objetivo y calculamos ruta (modo normal)
        if not self.current_path:
            self._check_emergency_battery(balls, basket_rect, station_rect, pathfinder)

            target_pos = self._get_target_pos(balls, basket_rect, station_rect, pathfinder, developer_mode)
            if target_pos:
                # construir conjunto de obstáculos como centros de celda (tu código usa centros)
                obstacles = set(balls) | {station_rect.center, basket_rect.center}
                if self.state == 'SEARCHING' and self.target_ball in obstacles:
                    obstacles.discard(self.target_ball)

                if developer_mode:
                    # en modo desarrollador inicializamos la búsqueda paso a paso
                    pathfinder.start_search(self.rect.center, target_pos, obstacles)
                    self.is_pathfinding = True
                else:
                    # en modo normal calculamos el camino completo de una
                    path = pathfinder.a_star(self.rect.center, target_pos, obstacles)
                    if path is not None:
                        self.current_path = path
                        pathfinder.final_path = [(p[0] // Config.GRID_SIZE, p[1] // Config.GRID_SIZE) for p in path]
                        self.stuck_counter = 0
                    else:
                        self.stuck_counter += 1
                        if self.stuck_counter >= Config.MAX_STUCK_TURNS:
                            return 'GAME_OVER_STUCK'

        # 3) Si tenemos ruta, avanzamos un paso (modo normal: animación, dev: celda por celda)
        if self.current_path:
            if developer_mode:
                # Avanza una celda completa cada vez que presionas A
                next_step = self.current_path.pop(0)
                self.rect.x = next_step[0] - Config.GRID_SIZE // 2
                self.rect.y = next_step[1] - Config.GRID_SIZE // 2
                self.charge -= Config.CHARGE_PER_MOVE
            else:
                # Modo normal: animación pixel por pixel
                next_step = self.current_path.pop(0)
                self.target_pixel_x = next_step[0] - Config.GRID_SIZE // 2
                self.target_pixel_y = next_step[1] - Config.GRID_SIZE // 2
                self.is_moving = True
                self.charge -= Config.CHARGE_PER_MOVE

        # 4) Si no está moviéndose y no tiene ruta, comprobamos llegada (lógica de objetivo)
        if not self.is_moving and not self.current_path:
            return self._handle_arrival(balls, basket_rect, station_rect, pathfinder)

        return None

    def animate_move(self, developer_mode=False):
        if developer_mode:
            return 
        
        if not self.is_moving or self.state == 'DEAD':
            return

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

    def _get_target_pos(self, balls, basket_rect, station_rect, pathfinder: Pathfinder, developer_mode=False):
        """Determina objetivo. En modo desarrollador selecciona una pelota alcanzable
        pero NO ejecuta a_star de forma completa (permitimos que el usuario vea el paso a paso)."""
        if self.state == 'COLLECTING':
            return basket_rect.center
        if self.state == 'CHARGING':
            return station_rect.center

        if self.state == 'SEARCHING' and balls:
            sorted_balls = sorted(balls, key=lambda ball: abs(ball[0] - self.rect.centerx) + abs(ball[1] - self.rect.centery))
            if developer_mode:
                # elegimos la pelota más cercana y dejamos que el A* paso a paso determine si es alcanzable
                self.target_ball = sorted_balls[0]
                return self.target_ball
            else:
                # en modo normal probamos si existe camino completo antes de decidir
                for ball in sorted_balls:
                    obstacles = set(balls) | {station_rect.center, basket_rect.center}
                    obstacles.discard(ball)
                    if pathfinder.a_star(self.rect.center, ball, obstacles) is not None:
                        self.target_ball = ball
                        return self.target_ball
        return None

    def _handle_arrival(self, balls, basket_rect, station_rect, pathfinder: Pathfinder):
        """Gestiona acciones cuando el robot llega a destino. Si completa una tarea
           principal, limpia la pizarra (pathfinder.clear)."""
        task_completed = False

        if self.state == 'SEARCHING' and not self.is_carrying:
            if self.target_ball and self.rect.collidepoint(self.target_ball):
                if self.target_ball in balls:
                    balls.remove(self.target_ball)
                self.is_carrying = True
                self.state = 'COLLECTING'
                self.target_ball = None
                task_completed = True

        elif self.state == 'COLLECTING':
            if Robot.is_fully_contained(self.rect, basket_rect):
                self.collected += 1
                self.is_carrying = False
                if self.collected == Config.NUM_BALLS:
                    pathfinder.clear()
                    return 'GAME_OVER'
                else:
                    self.state = 'SEARCHING'
                    task_completed = True
                    pathfinder.clear()
                    if self.collected == 1:
                        self.dev_unlocked = True

        elif self.state == 'CHARGING':
            if Robot.is_fully_contained(self.rect, station_rect):
                self.state = 'RECHARGING'
                task_completed = True

        if task_completed:
            # La pizarra de cálculos solo se borra cuando alcanzamos un objetivo principal
            pathfinder.clear()

        return None

    def _check_emergency_battery(self, balls, basket_rect, station_rect, pathfinder: Pathfinder):
        if self.charge <= Config.EMERGENCY_CHARGE and self.state not in ['CHARGING', 'RECHARGING']:
            if self.is_carrying:
                # suelta la bola en la celda actual
                balls.append(self.rect.center)
                self.is_carrying = False
            self.state = 'CHARGING'
            self.current_path = []
            self.is_pathfinding = False
            pathfinder.clear()