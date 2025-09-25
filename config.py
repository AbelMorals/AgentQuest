import math
import heapq

# ==============================================================================
# CLASE 1: Configuración (Config)
# Responsabilidad: Almacenar todas las constantes y parámetros del juego.
# Facilita cambiar la configuración sin tener que buscar en todo el código.
# ==============================================================================
class Config:
    GRID_SIZE = 30
    HUD_HEIGHT = 60
    WIDTH, HEIGHT = 810, 600 + HUD_HEIGHT

    # Colores y Fuentes
    BLACK = (0, 0, 0); WHITE = (220, 220, 220); GREEN = (0, 200, 0)
    DARK_GREEN = (0, 100, 0); RED = (200, 0, 0); BLUE = (0, 120, 255)
    BACKGROUND = (30, 30, 50); YELLOW = (255, 220, 0); ORANGE = (255, 150, 0)
    PATH_COLOR = (80, 80, 100)
    
    # Parámetros del Robot
    ROBOT_ANIMATION_SPEED = 5
    robot_decision_cooldown = 100
    MAX_CHARGE = 600; EMERGENCY_CHARGE = 250; CHARGE_PER_MOVE = 2
    RECHARGE_RATE = MAX_CHARGE / 30 
    BATTERY_SAFETY_MARGIN = 1.25
    MAX_STUCK_TURNS = 5
    
    # Parámetros del Mundo
    NUM_BALLS = 100
    STATION_SIZE = GRID_SIZE * 1; BASKET_SIZE = GRID_SIZE * 1