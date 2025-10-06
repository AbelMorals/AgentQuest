import pygame
import os
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
        self.fuente_pequena = pygame.font.SysFont("Consolas", 10)
        self.fuente_grande = pygame.font.SysFont("Arial Black", 50)
        directorio_actual = os.path.dirname(os.path.abspath(__file__))

        # Mapeo de rectángulos a imágenes fijas para obstáculos
        self.obstaculo_rect_img = {}

        # Cargar imagen del robot
        ruta_imagen = os.path.join(directorio_actual, "Imagenes", "payaso.png")
        self.imagen_robot = pygame.image.load(ruta_imagen).convert_alpha()
        self.imagen_robot = pygame.transform.scale(self.imagen_robot, (Config.TAMANO_CELDA + 2, Config.TAMANO_CELDA + 2))
        
        # Cargar imagen de la pelota
        ruta_pelota = os.path.join(directorio_actual, "Imagenes", "pelota.png")
        self.imagen_pelota = pygame.image.load(ruta_pelota).convert_alpha()
        self.imagen_pelota = pygame.transform.scale(self.imagen_pelota, (Config.TAMANO_CELDA - 5, Config.TAMANO_CELDA - 5))

        # Cargar imagen de la estación
        ruta_estacion = os.path.join(directorio_actual, "Imagenes", "cama.png")
        self.imagen_estacion = pygame.image.load(ruta_estacion).convert_alpha()
        self.imagen_estacion = pygame.transform.scale(self.imagen_estacion, (Config.TAMANO_CELDA, Config.TAMANO_CELDA))

        # Cargar imagen de la canasta
        ruta_canasta = os.path.join(directorio_actual, "Imagenes", "canasta.png")
        self.imagen_canasta = pygame.image.load(ruta_canasta).convert_alpha()
        self.imagen_canasta = pygame.transform.scale(self.imagen_canasta, (Config.TAMANO_CELDA, Config.TAMANO_CELDA))

        # Cargar imagen del césped
        ruta_cesped = os.path.join(directorio_actual, "Imagenes", "cesped.png")
        self.imagen_cesped = pygame.image.load(ruta_cesped).convert()
        self.imagen_cesped = pygame.transform.scale(self.imagen_cesped, (Config.TAMANO_CELDA, Config.TAMANO_CELDA))

        # Diccionario de imágenes de obstáculos por tamaño
        self.imagenes_obstaculos = {
            (1, 1): ["arofuego.png", "arofuego2.png", "globos32.png", "paja.png"],
            (2, 2): ["leon.png", "puesto.png", "puesto2.png", "puesto3.png", "puesto4.png"],
            (2, 3): ["cañon.png", "Fuerza.png", "globos64.png"],
            (3, 2): ["carro.png"],
            (4, 4): ["carpa.png"],
            (10, 1): ["ilera.png", "ilera2.png"],
            (1, 10): ["ilera3.png"]
        }
        self.obstaculo_imgs = {}
        for tam, nombres in self.imagenes_obstaculos.items():
            self.obstaculo_imgs[tam] = []
            for nombre in nombres:
                ruta = os.path.join(directorio_actual, "Imagenes", nombre)
                try:
                    img = pygame.image.load(ruta).convert_alpha()
                    img = pygame.transform.scale(img, (Config.TAMANO_CELDA * tam[0], Config.TAMANO_CELDA * tam[1]))
                    self.obstaculo_imgs[tam].append(img)
                except Exception:
                    pass

    def dibujar(self, estado_juego, mundo, robot, modo_desarrollador, pathfinder):
        if modo_desarrollador:
            self.pantalla.fill(Config.FONDO)
            self._dibujar_cuadricula()
        else:
            self.pantalla.fill(Config.VERDE_OSCURO)
            self._dibujar_fondo_cesped()

        # Dibujar obstáculos con imágenes fijas
        if hasattr(mundo, 'obstaculos'):
            import random
            for rect_obs in mundo.obstaculos:
                ancho = rect_obs.width // Config.TAMANO_CELDA
                alto = rect_obs.height // Config.TAMANO_CELDA
                tam = (ancho, alto)
                imgs = self.obstaculo_imgs.get(tam)
                rect_key = (rect_obs.x, rect_obs.y, rect_obs.width, rect_obs.height)
                if rect_key not in self.obstaculo_rect_img:
                    if imgs:
                        self.obstaculo_rect_img[rect_key] = random.choice(imgs)
                    else:
                        self.obstaculo_rect_img[rect_key] = None
                img = self.obstaculo_rect_img[rect_key]
                if img:
                    self.pantalla.blit(img, rect_obs)
                else:
                    gris = (120, 120, 120)
                    pygame.draw.rect(self.pantalla, gris, rect_obs)

        self.pantalla.blit(self.imagen_estacion, mundo.rect_estacion)
        self.pantalla.blit(self.imagen_canasta, mundo.rect_canasta)
        for pos_pelota in mundo.pelotas:
            x = pos_pelota[0] - Config.TAMANO_CELDA // 2
            y = pos_pelota[1] - Config.TAMANO_CELDA // 2
            self.pantalla.blit(self.imagen_pelota, (x, y))

        if modo_desarrollador:
            self._dibujar_puntajes_astar(pathfinder)

        self._dibujar_robot(robot)
        self._dibujar_hud(robot)
        self._dibujar_overlays(estado_juego)
        pygame.display.flip()

    def _dibujar_puntajes_astar(self, pathfinder):
        if not pathfinder.pos_objetivo: return
        for nodo, puntaje_g in pathfinder.puntaje_g.items():
            puntaje_h = pathfinder.heuristica(nodo, pathfinder.pos_objetivo)
            puntaje_p = puntaje_g + puntaje_h

            px = nodo[0] * Config.TAMANO_CELDA
            py = nodo[1] * Config.TAMANO_CELDA
            tam = Config.TAMANO_CELDA
            color = Config.AMARILLO if nodo in pathfinder.camino_final else Config.BLANCO
            
            texto_g = self.fuente_pequena.render(str(puntaje_g), True, color)
            texto_h = self.fuente_pequena.render(str(puntaje_h), True, color)
            texto_p = self.fuente_pequena.render(str(puntaje_p), True, color)

            self.pantalla.blit(texto_g, (px + 2, py + 2))
            self.pantalla.blit(texto_h, (px + tam - texto_h.get_width() - 2, py + 2))
            self.pantalla.blit(texto_p, (px + (tam // 2) - (texto_p.get_width() // 2), py + tam - texto_p.get_height() - 2))

    def _dibujar_fondo_cesped(self):
        for x in range(0, Config.SCREEN_ANCHO, Config.TAMANO_CELDA):
            for y in range(Config.ALTURA_HUD, Config.SCREEN_ALTO, Config.TAMANO_CELDA):
                self.pantalla.blit(self.imagen_cesped, (x, y))
    
    def _dibujar_cuadricula(self):
        for x in range(0, Config.ANCHO, Config.TAMANO_CELDA):
            pygame.draw.line(self.pantalla, (40, 40, 60), (x, Config.ALTURA_HUD), (x, Config.ALTO))
        for y in range(Config.ALTURA_HUD, Config.ALTO, Config.TAMANO_CELDA):
            pygame.draw.line(self.pantalla, (40, 40, 60), (0, y), (Config.ANCHO, y))

    def _dibujar_robot(self, robot):
        rect = robot.rect
        self.pantalla.blit(self.imagen_robot, rect)
        if robot.lleva_pelota:
            # Calcular la posición de la celda de enfrente
            pos_x = robot.rect.centerx + robot.direccion[0] * Config.TAMANO_CELDA
            pos_y = robot.rect.centery + robot.direccion[1] * Config.TAMANO_CELDA
            
            # Dibujar la pelota en esa posición
            self.pantalla.blit(self.imagen_pelota, self.imagen_pelota.get_rect(center=(pos_x, pos_y)))

    def _dibujar_hud(self, robot):
        pygame.draw.rect(self.pantalla, (10, 10, 20), (0, 0, Config.SCREEN_ANCHO, Config.ALTURA_HUD))
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
            texto_menu = self.fuente_grande.render("PARADISE CIRCUS", True, Config.NEGRO)
            self.pantalla.blit(texto_menu, (Config.ANCHO//2 - texto_menu.get_width()//2, Config.ALTO//2 - 100))
            texto_inicio = self.fuente.render("Presiona ENTER para iniciar", True, Config.NEGRO)
            self.pantalla.blit(texto_inicio, (Config.ANCHO//2 - texto_inicio.get_width()//2, Config.ALTO//2))
        elif estado_juego == 'PAUSED':
            overlay = pygame.Surface((Config.SCREEN_ANCHO, Config.SCREEN_ALTO), pygame.SRCALPHA)
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
        elif estado_juego == 'MUERTO':
            texto_muerto = self.fuente_grande.render("BATERÍA AGOTADA", True, Config.ROJO)
            self.pantalla.blit(texto_muerto, (Config.ANCHO//2 - texto_muerto.get_width()//2, Config.ALTO//2 - texto_muerto.get_height()//2))