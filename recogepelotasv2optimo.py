import pygame
import sys
import random
import math
import heapq

# Inicializar Pygame
pygame.init()

# --- CONFIGURACIÓN Y CONSTANTES ---
GRID_SIZE = 30
HUD_HEIGHT = 60
WIDTH, HEIGHT = 810, 600 + HUD_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Agente con Búsqueda A* v7.1 - Corregido")

# Colores y Fuentes
BLACK = (0, 0, 0); WHITE = (220, 220, 220); GREEN = (0, 200, 0)
DARK_GREEN = (0, 100, 0); RED = (200, 0, 0); BLUE = (0, 120, 255)
BACKGROUND = (30, 30, 50); YELLOW = (255, 220, 0); ORANGE = (255, 150, 0)
PATH_COLOR = (80, 80, 100)
font = pygame.font.SysFont("Arial", 22)
big_font = pygame.font.SysFont("Arial Black", 70)

# --- PARÁMETROS DEL JUEGO Y ROBOT ---
robot_size = GRID_SIZE
ROBOT_ANIMATION_SPEED = 5
robot_decision_cooldown = 100
MAX_CHARGE = 600; EMERGENCY_CHARGE = 250; CHARGE_PER_MOVE = 2
RECHARGE_RATE = MAX_CHARGE / 10 
num_balls = 100; 
BATTERY_SAFETY_MARGIN = 1.25

# --- OBJETOS DEL ENTORNO ---
STATION_SIZE = GRID_SIZE * 1; 
BASKET_SIZE = GRID_SIZE * 1
station_rect = pygame.Rect(GRID_SIZE, GRID_SIZE + HUD_HEIGHT, STATION_SIZE, STATION_SIZE)
basket_rect = pygame.Rect(WIDTH - BASKET_SIZE - GRID_SIZE, HEIGHT - BASKET_SIZE - GRID_SIZE, BASKET_SIZE, BASKET_SIZE)

# --- VARIABLES DE ESTADO ---
game_state = 'MENU'
robot_vars = {}

# --- ALGORITMO DE BÚSQUEDA A* (CORREGIDO) ---
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_pathfinding(start_node, goal_node, obstacles):
    start_pos = (start_node[0] // GRID_SIZE, start_node[1] // GRID_SIZE)
    goal_pos = (goal_node[0] // GRID_SIZE, goal_node[1] // GRID_SIZE)
    
    obstacle_grid = {(obs[0] // GRID_SIZE, obs[1] // GRID_SIZE) for obs in obstacles}
    
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    close_set = set()
    came_from = {}
    gscore = {start_pos: 0}
    fscore = {start_pos: heuristic(start_pos, goal_pos)}
    oheap = []

    heapq.heappush(oheap, (fscore[start_pos], start_pos))
    
    while oheap:
        current = heapq.heappop(oheap)[1]

        if current == goal_pos:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            data.reverse()
            return [(pos[0] * GRID_SIZE + GRID_SIZE // 2, pos[1] * GRID_SIZE + GRID_SIZE // 2) for pos in data]

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j            
            tentative_g_score = gscore[current] + 1
            
            if tentative_g_score < gscore.get(neighbor, float('inf')):
                # --- CORRECCIÓN CLAVE ---
                # El vecino es válido si: no está fuera de los límites Y (no es un obstáculo O es el objetivo final)
                is_valid_neighbor = 0 <= neighbor[0] < WIDTH // GRID_SIZE and \
                                  HUD_HEIGHT // GRID_SIZE <= neighbor[1] < HEIGHT // GRID_SIZE and \
                                  (neighbor not in obstacle_grid or neighbor == goal_pos)
                
                if is_valid_neighbor:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal_pos)
                    if neighbor not in oheap:
                        heapq.heappush(oheap, (fscore[neighbor], neighbor))
                        
    return None

# --- FUNCIONES AUXILIARES (reset, etc.) ---
def reset_game():
    global robot_vars, balls
    robot_rect, balls = generate_initial_positions()
    robot_vars = {
        'rect': robot_rect, 'charge': MAX_CHARGE, 'state': 'SEARCHING',
        'is_carrying': False, 'target_ball': None, 'collected': 0,
        'last_decision': 0, 'is_moving': False,
        'target_pixel_x': robot_rect.x, 'target_pixel_y': robot_rect.y,
        'current_path': [],
    }

def generate_initial_positions():
    while True:
        x = random.randrange(0, WIDTH, GRID_SIZE)
        y = random.randrange(HUD_HEIGHT, HEIGHT, GRID_SIZE)
        robot_r = pygame.Rect(x, y, robot_size, robot_size)
        if not robot_r.colliderect(station_rect) and not robot_r.colliderect(basket_rect): break
    balls_list = []
    obstacles = [station_rect, basket_rect, robot_r]
    while len(balls_list) < num_balls:
        ball_x = random.randrange(0, WIDTH, GRID_SIZE) + GRID_SIZE // 2
        ball_y = random.randrange(HUD_HEIGHT, HEIGHT, GRID_SIZE) + GRID_SIZE // 2
        ball_center = (ball_x, ball_y)
        ball_r = pygame.Rect(ball_x - GRID_SIZE//2, ball_y - GRID_SIZE//2, GRID_SIZE, GRID_SIZE)
        if not any(ball_r.colliderect(obs) for obs in obstacles) and ball_center not in balls_list:
            balls_list.append(ball_center)
            obstacles.append(ball_r)
    return robot_r, balls_list

def is_fully_contained(rect1, rect2):
    return rect1.left >= rect2.left and rect1.right <= rect2.right and rect1.top >= rect2.top and rect1.bottom <= rect2.bottom

def calculate_charge_needed(path):
    if not path: return 0
    return len(path) * CHARGE_PER_MOVE

# --- INICIALIZACIÓN ---
reset_game()
clock = pygame.time.Clock()
running = True

# --- BUCLE PRINCIPAL ---
while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            if event.key == pygame.K_RETURN and game_state == 'MENU': game_state = 'RUNNING'
            if event.key == pygame.K_SPACE and game_state in ['RUNNING', 'PAUSED']:
                game_state = 'PAUSED' if game_state == 'RUNNING' else 'RUNNING'
            if event.key == pygame.K_r and game_state != 'MENU':
                reset_game(); game_state = 'RUNNING'

    if game_state == 'RUNNING':
        if not robot_vars['is_moving'] and current_time - robot_vars['last_decision'] > robot_decision_cooldown:
            robot_vars['last_decision'] = current_time
            
            if not robot_vars['current_path']:
                target_pos = None
                obstacles = set(balls)
                
                # (Lógica de batería y estados sin cambios)
                if robot_vars['charge'] <= EMERGENCY_CHARGE and robot_vars['state'] != 'CHARGING':
                     robot_vars['state'] = 'CHARGING'
                if robot_vars['state'] == 'SEARCHING':
                    if balls:
                        target_ball = balls[0]
                        obstacles.remove(target_ball)
                        target_pos = target_ball
                elif robot_vars['state'] == 'COLLECTING':
                    target_pos = basket_rect.center
                elif robot_vars['state'] == 'CHARGING':
                    target_pos = station_rect.center
                
                if target_pos:
                    path = a_star_pathfinding(robot_vars['rect'].center, target_pos, obstacles)
                    if path is not None: # A* devuelve [] si ya está en el destino, lo cual es válido
                        robot_vars['current_path'] = path
                    else:
                        game_state = 'GAME_OVER_STUCK'

            if robot_vars['current_path']:
                next_step = robot_vars['current_path'].pop(0)
                robot_vars['target_pixel_x'], robot_vars['target_pixel_y'] = (next_step[0] - GRID_SIZE // 2, next_step[1] - GRID_SIZE // 2)
                robot_vars['is_moving'] = True
                robot_vars['charge'] -= CHARGE_PER_MOVE

            # Lógica de llegada y cambio de estado
            if not robot_vars['is_moving'] and not robot_vars['current_path']:
                 if robot_vars['state'] == 'SEARCHING' and robot_vars['is_carrying'] == False:
                    # Comprueba si el robot está en la posición de la pelota objetivo
                    if balls and robot_vars['rect'].collidepoint(balls[0]):
                         balls.pop(0)
                         robot_vars['is_carrying'] = True
                         robot_vars['state'] = 'COLLECTING'
                 elif robot_vars['state'] == 'COLLECTING':
                     if is_fully_contained(robot_vars['rect'], basket_rect):
                        robot_vars['collected'] += 1
                        robot_vars['is_carrying'] = False
                        if robot_vars['collected'] == num_balls: game_state = 'GAME_OVER'
                        else: robot_vars['state'] = 'SEARCHING'
                 elif robot_vars['state'] == 'CHARGING':
                     if is_fully_contained(robot_vars['rect'], station_rect):
                        robot_vars['state'] = 'RECHARGING'
                 elif robot_vars['state'] == 'RECHARGING':
                    if robot_vars['charge'] < MAX_CHARGE: robot_vars['charge'] += RECHARGE_RATE
                    else: robot_vars['charge'] = MAX_CHARGE; robot_vars['state'] = 'SEARCHING'

        # --- ANIMACIÓN DEL MOVIMIENTO (CORREGIDA) ---
        if robot_vars['is_moving']:
            # Moverse horizontalmente hasta alinearse
            if robot_vars['rect'].x != robot_vars['target_pixel_x']:
                direction = 1 if robot_vars['target_pixel_x'] > robot_vars['rect'].x else -1
                robot_vars['rect'].x += ROBOT_ANIMATION_SPEED * direction
                if (direction == 1 and robot_vars['rect'].x >= robot_vars['target_pixel_x']) or \
                   (direction == -1 and robot_vars['rect'].x <= robot_vars['target_pixel_x']):
                    robot_vars['rect'].x = robot_vars['target_pixel_x']
            
            # Solo después, moverse verticalmente hasta alinearse
            elif robot_vars['rect'].y != robot_vars['target_pixel_y']:
                direction = 1 if robot_vars['target_pixel_y'] > robot_vars['rect'].y else -1
                robot_vars['rect'].y += ROBOT_ANIMATION_SPEED * direction
                if (direction == 1 and robot_vars['rect'].y >= robot_vars['target_pixel_y']) or \
                   (direction == -1 and robot_vars['rect'].y <= robot_vars['target_pixel_y']):
                    robot_vars['rect'].y = robot_vars['target_pixel_y']
            
            # Si ambos ejes están alineados, el movimiento ha terminado
            else:
                robot_vars['is_moving'] = False
    
    # --- DIBUJADO ---
    screen.fill(BACKGROUND)
    if robot_vars.get('current_path') and game_state == 'RUNNING':
        if robot_vars['current_path']:
             full_path = [robot_vars['rect'].center] + robot_vars['current_path']
             pygame.draw.lines(screen, PATH_COLOR, False, full_path, 2)

    # ... (resto del código de dibujado es igual) ...
    for x in range(0, WIDTH, GRID_SIZE): pygame.draw.line(screen, (40, 40, 60), (x, HUD_HEIGHT), (x, HEIGHT))
    for y in range(HUD_HEIGHT, HEIGHT, GRID_SIZE): pygame.draw.line(screen, (40, 40, 60), (0, y), (WIDTH, y))
    pygame.draw.rect(screen, BLACK, station_rect); pygame.draw.rect(screen, WHITE, station_rect, 2)
    pygame.draw.rect(screen, DARK_GREEN, basket_rect); pygame.draw.rect(screen, WHITE, basket_rect, 2)
    for ball_pos in balls: pygame.draw.circle(screen, RED, ball_pos, GRID_SIZE // 2)
    robot_color = BLUE
    if robot_vars['state'] == 'CHARGING': robot_color = ORANGE
    if robot_vars['state'] == 'DEAD': robot_color = (50, 50, 50)
    pygame.draw.rect(screen, robot_color, robot_vars['rect'])
    if robot_vars['is_carrying']: pygame.draw.circle(screen, YELLOW, robot_vars['rect'].center, GRID_SIZE // 2 - 5)
    pygame.draw.rect(screen, (10, 10, 20), (0, 0, WIDTH, HUD_HEIGHT))
    bar_width, bar_height = 200, 25
    charge_ratio = max(0, robot_vars['charge'] / MAX_CHARGE)
    current_bar_width = bar_width * charge_ratio
    bar_color = GREEN if charge_ratio > 0.6 else YELLOW if charge_ratio > 0.3 else RED
    pygame.draw.rect(screen, BLACK, (10, 15, bar_width, bar_height))
    pygame.draw.rect(screen, bar_color, (10, 15, current_bar_width, bar_height))
    status_text = font.render(f"Estado: {robot_vars['state']} | Recogidas: {robot_vars['collected']}/{num_balls}", True, WHITE)
    screen.blit(status_text, (220, 17))
    if game_state == 'MENU':
        menu_text = big_font.render("ROBOT LIMPIADOR", True, WHITE); screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, HEIGHT//2 - 100))
        start_text = font.render("Presiona ENTER para iniciar", True, WHITE); screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
    if game_state == 'PAUSED':
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 150)); screen.blit(overlay, (0, 0))
        pause_title = big_font.render("PAUSADO", True, WHITE); screen.blit(pause_title, (WIDTH//2 - pause_title.get_width()//2, HEIGHT//2 - pause_title.get_height()//2))
    if game_state == 'GAME_OVER':
        win_text = big_font.render("¡MISIÓN CUMPLIDA!", True, YELLOW); screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - win_text.get_height()//2))
    if game_state == 'GAME_OVER_STUCK':
        stuck_text = big_font.render("SIN RUTA POSIBLE", True, ORANGE); screen.blit(stuck_text, (WIDTH//2 - stuck_text.get_width()//2, HEIGHT//2 - stuck_text.get_height()//2))
        
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()