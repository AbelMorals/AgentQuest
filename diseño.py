import pygame
from config import Config

# ==============================================================================
# CLASE 5: Renderizador (Renderer/Diseño)
# Responsabilidad: Todo lo relacionado con dibujar en pantalla. No toma
# decisiones, solo dibuja lo que le dicen las otras clases.
# ==============================================================================
class Diseño:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 22)
        self.big_font = pygame.font.SysFont("Arial Black", 70)

    def draw(self, game_state, world, robot):
        """Método principal que orquesta todo el dibujado."""
        self.screen.fill(Config.BACKGROUND)
        
        # Dibuja el mundo del juego
        self._draw_grid()
        pygame.draw.rect(self.screen, Config.BLACK, world.station_rect); pygame.draw.rect(self.screen, Config.WHITE, world.station_rect, 2)
        pygame.draw.rect(self.screen, Config.DARK_GREEN, world.basket_rect); pygame.draw.rect(self.screen, Config.WHITE, world.basket_rect, 2)
        for ball_pos in world.balls: pygame.draw.circle(self.screen, Config.RED, ball_pos, Config.GRID_SIZE // 2)

        # Dibuja el robot y su ruta
        self._draw_robot(robot)
        if robot.current_path and game_state == 'RUNNING':
             full_path = [robot.rect.center] + robot.current_path
             pygame.draw.lines(self.screen, Config.PATH_COLOR, False, full_path, 2)

        # Dibuja la interfaz y superposiciones
        self._draw_hud(robot)
        self._draw_overlays(game_state)
        
        pygame.display.flip()

    def _draw_grid(self):
        for x in range(0, Config.WIDTH, Config.GRID_SIZE): pygame.draw.line(self.screen, (40, 40, 60), (x, Config.HUD_HEIGHT), (x, Config.HEIGHT))
        for y in range(Config.HUD_HEIGHT, Config.HEIGHT, Config.GRID_SIZE): pygame.draw.line(self.screen, (40, 40, 60), (0, y), (Config.WIDTH, y))

    def _draw_robot(self, robot):
        robot_color = Config.BLUE
        if robot.state == 'CHARGING': robot_color = Config.ORANGE
        if robot.state == 'DEAD': robot_color = (50, 50, 50)
        pygame.draw.rect(self.screen, robot_color, robot.rect)
        if robot.is_carrying: pygame.draw.circle(self.screen, Config.YELLOW, robot.rect.center, Config.GRID_SIZE // 2 - 5)

    def _draw_hud(self, robot):
        pygame.draw.rect(self.screen, (10, 10, 20), (0, 0, Config.WIDTH, Config.HUD_HEIGHT))
        bar_width, bar_height = 200, 25
        charge_ratio = max(0, robot.charge / Config.MAX_CHARGE)
        current_bar_width = bar_width * charge_ratio
        bar_color = Config.GREEN if charge_ratio > 0.6 else Config.YELLOW if charge_ratio > 0.3 else Config.RED
        pygame.draw.rect(self.screen, Config.BLACK, (10, 15, bar_width, bar_height))
        pygame.draw.rect(self.screen, bar_color, (10, 15, current_bar_width, bar_height))
        status_text = self.font.render(f"Estado: {robot.state} | Recogidas: {robot.collected}/{Config.NUM_BALLS}", True, Config.WHITE)
        self.screen.blit(status_text, (220, 17))
    
    def _draw_overlays(self, game_state):
        if game_state == 'MENU':
            menu_text = self.big_font.render("ROBOT LIMPIADOR", True, Config.WHITE); self.screen.blit(menu_text, (Config.WIDTH//2 - menu_text.get_width()//2, Config.HEIGHT//2 - 100))
            start_text = self.font.render("Presiona ENTER para iniciar", True, Config.WHITE); self.screen.blit(start_text, (Config.WIDTH//2 - start_text.get_width()//2, Config.HEIGHT//2))
        elif game_state == 'PAUSED':
            overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 150)); self.screen.blit(overlay, (0, 0))
            pause_title = self.big_font.render("PAUSADO", True, Config.WHITE); self.screen.blit(pause_title, (Config.WIDTH//2 - pause_title.get_width()//2, Config.HEIGHT//2 - pause_title.get_height()//2))
        elif game_state == 'GAME_OVER':
            win_text = self.big_font.render("¡MISIÓN CUMPLIDA!", True, Config.YELLOW); self.screen.blit(win_text, (Config.WIDTH//2 - win_text.get_width()//2, Config.HEIGHT//2 - win_text.get_height()//2))
        elif game_state == 'GAME_OVER_STUCK':
            stuck_text = self.big_font.render("SIN RUTA POSIBLE", True, Config.ORANGE); self.screen.blit(stuck_text, (Config.WIDTH//2 - stuck_text.get_width()//2, Config.HEIGHT//2 - stuck_text.get_height()//2))
