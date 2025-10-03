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
        self.rect_estacion = pygame.Rect(Config.TAMANO_CELDA, Config.TAMANO_CELDA + Config.ALTURA_HUD, Config.TAMANO_ESTACION, Config.TAMANO_ESTACION)
        self.rect_canasta = pygame.Rect(Config.ANCHO - Config.TAMANO_CANASTA - Config.TAMANO_CELDA, Config.ALTO - Config.TAMANO_CANASTA - Config.TAMANO_CELDA, Config.TAMANO_CANASTA, Config.TAMANO_CANASTA)
        self.pelotas = []
        self.obstaculos = []
        self.pos_inicio_robot = (0, 0)
        self.num_obstaculos = Config.NUM_OBSTACULOS
        self.generar_disposicion()

    def generar_disposicion(self):
        # Crea una disposición aleatoria para los objetos.
        while True:
            x = random.randrange(0, Config.ANCHO, Config.TAMANO_CELDA)
            y = random.randrange(Config.ALTURA_HUD, Config.ALTO, Config.TAMANO_CELDA)
            rect_robot = pygame.Rect(x, y, Config.TAMANO_CELDA, Config.TAMANO_CELDA)
            if not rect_robot.colliderect(self.rect_estacion) and not rect_robot.colliderect(self.rect_canasta):
                self.pos_inicio_robot = (x, y)
                break

        self.pelotas = []
        obstaculos_rects = [self.rect_estacion, self.rect_canasta, rect_robot]

        # Generar obstáculos
        self.obstaculos = []
        obstaculo_tamanos = [
            (1, 1), (2, 2), (3, 2), (2, 3), (4, 4),
            (10, 1), (1, 10)
        ]
        intentos = 0
        while len(self.obstaculos) < self.num_obstaculos and intentos < 1000:
            intentos += 1
            tam = random.choice(obstaculo_tamanos)
            ancho = tam[0] * Config.TAMANO_CELDA
            alto = tam[1] * Config.TAMANO_CELDA
            x = random.randrange(0, Config.ANCHO - ancho, Config.TAMANO_CELDA)
            y = random.randrange(Config.ALTURA_HUD, Config.ALTO - alto, Config.TAMANO_CELDA)
            rect_obs = pygame.Rect(x, y, ancho, alto)
            if not any(rect_obs.colliderect(obs) for obs in obstaculos_rects):
                self.obstaculos.append(rect_obs)
                obstaculos_rects.append(rect_obs)

        # Generar pelotas evitando obstáculos
        while len(self.pelotas) < Config.NUM_PELOTAS:
            pelota_x = random.randrange(0, Config.ANCHO, Config.TAMANO_CELDA) + Config.TAMANO_CELDA // 2
            pelota_y = random.randrange(Config.ALTURA_HUD, Config.ALTO, Config.TAMANO_CELDA) + Config.TAMANO_CELDA // 2
            centro_pelota = (pelota_x, pelota_y)
            rect_pelota = pygame.Rect(pelota_x - Config.TAMANO_CELDA//2, pelota_y - Config.TAMANO_CELDA//2, Config.TAMANO_CELDA, Config.TAMANO_CELDA)
            if not any(rect_pelota.colliderect(obs) for obs in obstaculos_rects) and centro_pelota not in self.pelotas:
                self.pelotas.append(centro_pelota)
                obstaculos_rects.append(rect_pelota)
