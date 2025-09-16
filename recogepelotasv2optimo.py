import pygame
import sys
import random
import math

# Inicializar Pygame
pygame.init()

# --- CONFIGURACIÓN Y CONSTANTES ---
GRID_SIZE = 30
WIDTH, HEIGHT = 810, 660
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Limpiador v2.0")

# Colores
BLACK = (0, 0, 0); WHITE = (220, 220, 220)
GREEN = (0, 200, 0); DARK_GREEN = (0, 100, 0)
RED = (200, 0, 0); BLUE = (0, 120, 255)
BACKGROUND = (30, 30, 50); BUTTON_COLOR = (80, 80, 100)
BUTTON_HOVER = (110, 110, 130); YELLOW = (255, 220, 0); ORANGE = (255, 150, 0)

# --- PARÁMETROS DEL JUEGO Y ROBOT ---
robot_size = GRID_SIZE
# NUEVO: Velocidad de la animación en píxeles por fotograma
ROBOT_ANIMATION_SPEED = 5
# NUEVO: Pausa que hace el robot en una celda antes de decidir su siguiente movimiento
robot_decision_cooldown = 150
MAX_CHARGE = 500
EMERGENCY_CHARGE = 150
RECHARGE_RATE = MAX_CHARGE / 60 
num_balls = 10

# --- OBJETOS DEL ENTORNO ---
STATION_SIZE = GRID_SIZE * 1
BASKET_SIZE = GRID_SIZE * 1
station_rect = pygame.Rect(GRID_SIZE, GRID_SIZE, STATION_SIZE, STATION_SIZE)
basket_rect = pygame.Rect(WIDTH - BASKET_SIZE - GRID_SIZE, HEIGHT - BASKET_SIZE - GRID_SIZE - 60, BASKET_SIZE, BASKET_SIZE)

# --- VARIABLES DE ESTADO ---
game_state = 'MENU'
robot_vars = {}

# --- FUENTES Y BOTONES ---
font = pygame.font.SysFont("Arial", 22)
big_font = pygame.font.SysFont("Arial Black", 70)
start_button = pygame.Rect(WIDTH/2 - 100, HEIGHT/2, 200, 50)
pause_button = pygame.Rect(10, HEIGHT - 50, 120, 40)
restart_button = pygame.Rect(140, HEIGHT - 50, 120, 40)

# --- FUNCIONES ---
def reset_game():
    """Inicializa o reinicia todas las variables del juego a su estado original."""
    global robot_vars, balls
    robot_rect, balls = generate_initial_positions()
    robot_vars = {
        'rect': robot_rect,
        'charge': MAX_CHARGE,
        'state': 'SEARCHING',
        'is_carrying': False,
        'target_ball': None,
        'collected': 0,
        'last_decision': 0,
        # NUEVO: variables para el movimiento fluido
        'is_moving': False,
        'target_pixel_x': robot_rect.x,
        'target_pixel_y': robot_rect.y,
    }

# (Las demás funciones auxiliares como generate_initial_positions, is_fully_contained, etc., no cambian)
def generate_initial_positions():
    while True:
        x = random.randrange(0, WIDTH - robot_size, GRID_SIZE)
        y = random.randrange(0, HEIGHT - robot_size - 60, GRID_SIZE)
        robot_r = pygame.Rect(x, y, robot_size, robot_size)
        if not robot_r.colliderect(station_rect) and not robot_r.colliderect(basket_rect): break
    balls_list = []
    obstacles = [station_rect, basket_rect, robot_r]
    while len(balls_list) < num_balls:
        ball_x = random.randrange(0, WIDTH - GRID_SIZE, GRID_SIZE) + GRID_SIZE // 2
        ball_y = random.randrange(0, HEIGHT - GRID_SIZE - 60, GRID_SIZE) + GRID_SIZE // 2
        ball_center = (ball_x, ball_y)
        ball_r = pygame.Rect(ball_x - GRID_SIZE//2, ball_y - GRID_SIZE//2, GRID_SIZE, GRID_SIZE)
        if not any(ball_r.colliderect(obs) for obs in obstacles) and ball_center not in balls_list:
            balls_list.append(ball_center)
            obstacles.append(ball_r)
    return robot_r, balls_list

def is_fully_contained(rect1, rect2):
    return rect1.left >= rect2.left and rect1.right <= rect2.right and rect1.top >= rect2.top and rect1.bottom <= rect2.bottom

def find_nearest_ball(robot_pos, ball_list):
    if not ball_list: return None
    return min(ball_list, key=lambda ball: math.hypot(ball[0] - robot_pos[0], ball[1] - robot_pos[1]))

# --- INICIALIZACIÓN ---
reset_game()
clock = pygame.time.Clock()
running = True

# --- BUCLE PRINCIPAL ---
while running:
    mouse_pos = pygame.mouse.get_pos()
    current_time = pygame.time.get_ticks()

    # MANEJO DE EVENTOS
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == 'MENU' and start_button.collidepoint(mouse_pos): game_state = 'RUNNING'
            elif game_state in ['RUNNING', 'PAUSED'] and pause_button.collidepoint(mouse_pos):
                game_state = 'PAUSED' if game_state == 'RUNNING' else 'RUNNING'
            if game_state in ['RUNNING', 'PAUSED', 'GAME_OVER'] and restart_button.collidepoint(mouse_pos):
                reset_game()
                game_state = 'RUNNING'

    # --- LÓGICA DEL JUEGO (SOLO EN 'RUNNING') ---
    if game_state == 'RUNNING':
        # --- PARTE 1: DECISIÓN DEL MOVIMIENTO (solo si NO se está moviendo) ---
        if not robot_vars['is_moving'] and current_time - robot_vars['last_decision'] > robot_decision_cooldown:
            robot_vars['last_decision'] = current_time
            
            # (La lógica de estados y decisiones es la misma que antes)
            if robot_vars['charge'] <= EMERGENCY_CHARGE and robot_vars['state'] not in ['CHARGING', 'RECHARGING']:
                if robot_vars['is_carrying']:
                    balls.append(robot_vars['rect'].center)
                    robot_vars['is_carrying'] = False
                robot_vars['state'] = 'CHARGING'
            if robot_vars['charge'] <= 0: robot_vars['state'] = 'DEAD'

            target_pos_center = None
            if robot_vars['state'] == 'SEARCHING':
                if not robot_vars['target_ball'] or robot_vars['target_ball'] not in balls:
                    robot_vars['target_ball'] = find_nearest_ball(robot_vars['rect'].center, balls)
                if robot_vars['target_ball']:
                    target_pos_center = robot_vars['target_ball']
                    if robot_vars['rect'].center == target_pos_center:
                        balls.remove(target_pos_center); robot_vars['is_carrying'] = True; robot_vars['state'] = 'COLLECTING'

            elif robot_vars['state'] == 'COLLECTING':
                target_pos_center = basket_rect.center
                if is_fully_contained(robot_vars['rect'], basket_rect):
                    robot_vars['collected'] += 1; robot_vars['is_carrying'] = False
                    if robot_vars['collected'] == num_balls: game_state = 'GAME_OVER'
                    else: robot_vars['state'] = 'SEARCHING' if balls else 'IDLE'

            elif robot_vars['state'] == 'CHARGING':
                target_pos_center = station_rect.center
                if is_fully_contained(robot_vars['rect'], station_rect): robot_vars['state'] = 'RECHARGING'
            
            elif robot_vars['state'] == 'RECHARGING':
                if robot_vars['charge'] < MAX_CHARGE: robot_vars['charge'] += RECHARGE_RATE
                else: robot_vars['charge'] = MAX_CHARGE; robot_vars['state'] = 'SEARCHING' if balls else 'IDLE'

            # Si se decidió un objetivo, calcula la siguiente celda e inicia el movimiento
            if target_pos_center and robot_vars['state'] not in ['RECHARGING', 'DEAD', 'IDLE']:
                dx, dy = target_pos_center[0] - robot_vars['rect'].centerx, target_pos_center[1] - robot_vars['rect'].centery
                if abs(dx) >= GRID_SIZE:
                    robot_vars['target_pixel_x'] += GRID_SIZE if dx > 0 else -GRID_SIZE
                elif abs(dy) >= GRID_SIZE:
                    robot_vars['target_pixel_y'] += GRID_SIZE if dy > 0 else -GRID_SIZE
                
                # Inicia el movimiento si el objetivo cambió
                if robot_vars['target_pixel_x'] != robot_vars['rect'].x or robot_vars['target_pixel_y'] != robot_vars['rect'].y:
                    robot_vars['is_moving'] = True
                    robot_vars['charge'] -= 2 # Consume batería al iniciar el movimiento

        # --- PARTE 2: ANIMACIÓN DEL MOVIMIENTO (cada fotograma, si se está moviendo) ---
        if robot_vars['is_moving']:
            # Mover hacia la coordenada X del objetivo
            if robot_vars['rect'].x != robot_vars['target_pixel_x']:
                direction = 1 if robot_vars['target_pixel_x'] > robot_vars['rect'].x else -1
                robot_vars['rect'].x += ROBOT_ANIMATION_SPEED * direction
                # Si se pasa, corregir y detener en el eje X
                if (direction == 1 and robot_vars['rect'].x >= robot_vars['target_pixel_x']) or \
                   (direction == -1 and robot_vars['rect'].x <= robot_vars['target_pixel_x']):
                    robot_vars['rect'].x = robot_vars['target_pixel_x']

            # Mover hacia la coordenada Y del objetivo
            elif robot_vars['rect'].y != robot_vars['target_pixel_y']:
                direction = 1 if robot_vars['target_pixel_y'] > robot_vars['rect'].y else -1
                robot_vars['rect'].y += ROBOT_ANIMATION_SPEED * direction
                # Si se pasa, corregir y detener en el eje Y
                if (direction == 1 and robot_vars['rect'].y >= robot_vars['target_pixel_y']) or \
                   (direction == -1 and robot_vars['rect'].y <= robot_vars['target_pixel_y']):
                    robot_vars['rect'].y = robot_vars['target_pixel_y']

            # Si ha llegado a la celda objetivo, detener el movimiento
            if robot_vars['rect'].x == robot_vars['target_pixel_x'] and robot_vars['rect'].y == robot_vars['target_pixel_y']:
                robot_vars['is_moving'] = False


    # --- DIBUJADO (siempre se ejecuta) ---
    screen.fill(BACKGROUND)
    # (El código de dibujado de la cuadrícula, objetos, HUD y botones no cambia)
    for x in range(0, WIDTH, GRID_SIZE): pygame.draw.line(screen, (40, 40, 60), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE): pygame.draw.line(screen, (40, 40, 60), (0, y), (WIDTH, y))
    pygame.draw.rect(screen, BLACK, station_rect); pygame.draw.rect(screen, WHITE, station_rect, 2)
    pygame.draw.rect(screen, DARK_GREEN, basket_rect); pygame.draw.rect(screen, WHITE, basket_rect, 2)
    for ball_pos in balls: pygame.draw.circle(screen, RED, ball_pos, GRID_SIZE // 2)
    robot_color = BLUE
    if robot_vars['state'] == 'CHARGING': robot_color = ORANGE
    if robot_vars['state'] == 'DEAD': robot_color = (50, 50, 50)
    pygame.draw.rect(screen, robot_color, robot_vars['rect'])
    if robot_vars['is_carrying']: pygame.draw.circle(screen, YELLOW, robot_vars['rect'].center, GRID_SIZE // 2 - 5)
    bar_width, bar_height = 200, 25
    charge_ratio = max(0, robot_vars['charge'] / MAX_CHARGE)
    current_bar_width = bar_width * charge_ratio
    bar_color = GREEN if charge_ratio > 0.6 else YELLOW if charge_ratio > 0.3 else RED
    pygame.draw.rect(screen, BLACK, (10, 10, bar_width, bar_height))
    pygame.draw.rect(screen, bar_color, (10, 10, current_bar_width, bar_height))
    status_text = font.render(f"Estado: {robot_vars['state']} | Recogidas: {robot_vars['collected']}/{num_balls}", True, WHITE)
    screen.blit(status_text, (220, 12))
    if game_state == 'MENU':
        pygame.draw.rect(screen, BUTTON_COLOR, start_button)
        start_text = font.render("INICIAR", True, WHITE)
        screen.blit(start_text, (start_button.centerx - start_text.get_width()//2, start_button.centery - start_text.get_height()//2))
    else:
        pause_text_str = "REANUDAR" if game_state == 'PAUSED' else "PAUSAR"
        p_color = BUTTON_HOVER if pause_button.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, p_color, pause_button, border_radius=5)
        pause_text = font.render(pause_text_str, True, WHITE)
        screen.blit(pause_text, (pause_button.centerx - pause_text.get_width()//2, pause_button.centery - pause_text.get_height()//2))
        r_color = BUTTON_HOVER if restart_button.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, r_color, restart_button, border_radius=5)
        restart_text = font.render("REINICIAR", True, WHITE)
        screen.blit(restart_text, (restart_button.centerx - restart_text.get_width()//2, restart_button.centery - restart_text.get_height()//2))
    if game_state == 'PAUSED':
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        pause_title = big_font.render("PAUSADO", True, WHITE)
        screen.blit(pause_title, (WIDTH//2 - pause_title.get_width()//2, HEIGHT//2 - pause_title.get_height()//2))
    if game_state == 'GAME_OVER':
        win_text = big_font.render("¡MISIÓN CUMPLIDA!", True, YELLOW)
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - win_text.get_height()//2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()