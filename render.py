import pygame
from config import Config

# ==============================================================================
# CLASE 5: Renderizador (Renderer/Diseño)
# Responsabilidad: Todo lo relacionado con dibujar en pantalla. No toma
# decisiones, solo dibuja lo que le dicen las otras clases.
# ==============================================================================
class Render:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        pygame.font.init()
        self.fuente = pygame.font.SysFont("Arial", 22)
        self.fuente_pequena = pygame.font.SysFont("Consolas", 12)
        self.fuente_grande = pygame.font.SysFont("Arial Black", 70)

    def dibujar(self, estado_juego, mundo, robot, modo_desarrollador, pathfinder):
        self.pantalla.fill(Config.FONDO)
        self._dibujar_celda()

        pygame.draw.rect(self.pantalla, Config.NEGRO, mundo.rect_estacion); pygame.draw.rect(self.pantalla, Config.BLANCO, mundo.rect_estacion, 2)
        pygame.draw.rect(self.pantalla, Config.VERDE_OSCURO, mundo.rect_canasta); pygame.draw.rect(self.pantalla, Config.BLANCO, mundo.rect_canasta, 2)
        for pos_pelota in mundo.pelotas:
            pygame.draw.circle(self.pantalla, Config.ROJO, pos_pelota, Config.TAMANO_CELDA // 2)

        if modo_desarrollador:
            self._dibujar_puntajes_astar(pathfinder)

        self._dibujar_robot(robot)
        self._dibujar_hud(robot)
        self._dibujar_overlays(estado_juego)
        pygame.display.flip()

    def _dibujar_puntajes_astar(self, pathfinder):
        if not pathfinder.puntaje_g or not pathfinder.pos_objetivo:
            return

        for nodo, puntaje_g in pathfinder.puntaje_g.items():
            puntaje_h = pathfinder.heuristica(nodo, pathfinder.pos_objetivo)
            puntaje_p = puntaje_g + puntaje_h

            px = nodo[0] * Config.TAMANO_CELDA
            py = nodo[1] * Config.TAMANO_CELDA

            color = Config.AMARILLO if nodo in pathfinder.camino_final else Config.BLANCO

            texto_h = self.fuente_pequena.render(f"H:{puntaje_h}", True, color)
            texto_p = self.fuente_pequena.render(f"P:{puntaje_p}", True, color)

            self.pantalla.blit(texto_h, (px + 3, py + 4))
            self.pantalla.blit(texto_p, (px + 3, py + 18))

    def _dibujar_celda(self):
        for x in range(0, Config.ANCHO, Config.TAMANO_CELDA):
            pygame.draw.line(self.pantalla, (40, 40, 60), (x, Config.ALTURA_HUD), (x, Config.ALTO))
        for y in range(Config.ALTURA_HUD, Config.ALTO, Config.TAMANO_CELDA):
            pygame.draw.line(self.pantalla, (40, 40, 60), (0, y), (Config.ANCHO, y))

    def _dibujar_robot(self, robot):
        color_robot = Config.AZUL
        if robot.estado == 'CHARGING': color_robot = Config.NARANJA
        if robot.estado == 'DEAD': color_robot = (50, 50, 50)
        pygame.draw.rect(self.pantalla, color_robot, robot.rect)
        if robot.lleva_pelota:
            pygame.draw.circle(self.pantalla, Config.AMARILLO, robot.rect.center, Config.TAMANO_CELDA // 2 - 5)

    def _dibujar_hud(self, robot):
        pygame.draw.rect(self.pantalla, (10, 10, 20), (0, 0, Config.ANCHO, Config.ALTURA_HUD))
        ancho_barra, alto_barra = 200, 25
        proporcion_carga = max(0, robot.carga / Config.CARGA_MAXIMA)
        ancho_barra_actual = ancho_barra * proporcion_carga
        color_barra = Config.VERDE if proporcion_carga > 0.6 else Config.AMARILLO if proporcion_carga > 0.3 else Config.ROJO
        pygame.draw.rect(self.pantalla, Config.NEGRO, (10, 15, ancho_barra, alto_barra))
        pygame.draw.rect(self.pantalla, color_barra, (10, 15, ancho_barra_actual, alto_barra))
        texto_estado = self.fuente.render(f"Estado: {robot.estado} | Recogidas: {robot.recogidas}/{Config.NUM_PELOTAS}", True, Config.BLANCO)
        self.pantalla.blit(texto_estado, (220, 17))
        

    def _dibujar_overlays(self, estado_juego):
        if estado_juego == 'MENU':
            texto_menu = self.fuente_grande.render("ROBOT LIMPIADOR", True, Config.BLANCO)
            self.pantalla.blit(texto_menu, (Config.ANCHO//2 - texto_menu.get_width()//2, Config.ALTO//2 - 100))
            texto_inicio = self.fuente.render("Presiona ENTER para iniciar", True, Config.BLANCO)
            self.pantalla.blit(texto_inicio, (Config.ANCHO//2 - texto_inicio.get_width()//2, Config.ALTO//2))
        elif estado_juego == 'PAUSED':
            overlay = pygame.Surface((Config.ANCHO, Config.ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.pantalla.blit(overlay, (0, 0))
            titulo_pausa = self.fuente_grande.render("PAUSADO", True, Config.BLANCO)
            self.pantalla.blit(titulo_pausa, (Config.ANCHO//2 - titulo_pausa.get_width()//2, Config.ALTO//2 - titulo_pausa.get_height()//2))
        elif estado_juego == 'GAME_OVER':
            texto_ganar = self.fuente_grande.render("¡MISIÓN CUMPLIDA!", True, Config.AMARILLO)
            self.pantalla.blit(texto_ganar, (Config.ANCHO//2 - texto_ganar.get_width()//2, Config.ALTO//2 - texto_ganar.get_height()//2))
        elif estado_juego == 'GAME_OVER_STUCK':
            texto_atascado = self.fuente_grande.render("SIN RUTA POSIBLE", True, Config.NARANJA)
            self.pantalla.blit(texto_atascado, (Config.ANCHO//2 - texto_atascado.get_width()//2, Config.ALTO//2 - texto_atascado.get_height()//2))
        elif estado_juego == 'DEAD':
            texto_muerto = self.fuente_grande.render("BATERÍA AGOTADA", True, Config.ROJO)
            self.pantalla.blit(texto_muerto, (Config.ANCHO//2 - texto_muerto.get_width()//2, Config.ALTO//2 - texto_muerto.get_height()//2))
