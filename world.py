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
        self.pos_inicio_robot = (0, 0)
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
        obstaculos = [self.rect_estacion, self.rect_canasta, rect_robot]
        while len(self.pelotas) < Config.NUM_PELOTAS:
            pelota_x = random.randrange(0, Config.ANCHO, Config.TAMANO_CELDA) + Config.TAMANO_CELDA // 2
            pelota_y = random.randrange(Config.ALTURA_HUD, Config.ALTO, Config.TAMANO_CELDA) + Config.TAMANO_CELDA // 2
            centro_pelota = (pelota_x, pelota_y)
            rect_pelota = pygame.Rect(pelota_x - Config.TAMANO_CELDA//2, pelota_y - Config.TAMANO_CELDA//2, Config.TAMANO_CELDA, Config.TAMANO_CELDA)
            if not any(rect_pelota.colliderect(obs) for obs in obstaculos) and centro_pelota not in self.pelotas:
                self.pelotas.append(centro_pelota)
                obstaculos.append(rect_pelota)
