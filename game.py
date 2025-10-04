import pygame
import sys
from config import Config
from render import Render
from robot import Robot
from world import World
from pathfinder import Pathfinder

pygame.init()
# ==============================================================================
# CLASE 6: Juego (Game)
# Responsabilidad: Orquestar todo. Contiene el bucle principal, gestiona
# los eventos y le dice a las otras clases cuándo actuar.
# ==============================================================================
class Game:
    def __init__(self):
        #pygame.init()
        self.pantalla = pygame.display.set_mode((Config.ANCHO, Config.ALTO), pygame.FULLSCREEN)
        pygame.display.set_caption("AgentQuest v2.2")
        self.reloj = pygame.time.Clock()
        self.estado_juego = 'MENU'
        #self.estado_juego = 'RUNNING'
        self.renderizador = Render(self.pantalla)
        self.pathfinder = Pathfinder()
        self.modo_desarrollador = False
        self.paso_dev = False  # para tecla S (paso a paso)
        self.mantener_dev = False  # para tecla A (continuo)
        self.reiniciar()    

    def reiniciar(self):
        self.mundo = World()
        self.robot = Robot(self.mundo.pos_inicio_robot[0], self.mundo.pos_inicio_robot[1])
        self.estado_juego = 'MENU'
        #self.estado_juego = 'RUNNING'
        self.pathfinder.limpiar()

    def ejecutar(self):
        corriendo = True
        while corriendo:
            corriendo = self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(60)
        pygame.quit()
        sys.exit()

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return False
                if evento.key == pygame.K_RETURN and self.estado_juego == 'MENU':
                    self.estado_juego = 'RUNNING'
                if evento.key == pygame.K_SPACE and self.estado_juego in ['RUNNING', 'PAUSED']:
                    self.estado_juego = 'PAUSED' if self.estado_juego == 'RUNNING' else 'RUNNING'
                if evento.key == pygame.K_r:
                    self.reiniciar()
                if evento.key == pygame.K_d:
                    self.modo_desarrollador = not self.modo_desarrollador
                    self.robot.ruta_actual = []
                    self.robot.esta_busqueda = False
                    self.pathfinder.limpiar()
                    self.robot.sincronizar_posicion_animacion()
                    if self.modo_desarrollador:
                        self.robot.camino_normal.extend([self.robot.rect.center])
                    else:
                        self.robot.camino_dev.extend([self.robot.rect.center])
                if evento.key == pygame.K_s and self.modo_desarrollador and self.estado_juego == 'RUNNING':
                    self.paso_dev = True 
        return True

    def actualizar(self):
        if self.estado_juego != 'RUNNING':
            return

        teclas = pygame.key.get_pressed()
        if self.modo_desarrollador:
            self.mantener_dev = teclas[pygame.K_a]

        nuevo_estado = self.robot.actualizar(
            self.mundo.pelotas,
            self.mundo.rect_estacion,
            self.mundo.rect_canasta,
            self.pathfinder,
            modo_desarrollador=self.modo_desarrollador,
            paso_dev=self.paso_dev,
            mantener_dev=self.mantener_dev,
            obstaculos_extra=getattr(self.mundo, 'obstaculos', None)
        )

        self.paso_dev = False

        if nuevo_estado:
            self.estado_juego = nuevo_estado

        self.robot.animar_movimiento(self.modo_desarrollador)

    def dibujar(self):
        self.renderizador.dibujar(self.estado_juego, self.mundo, self.robot, self.modo_desarrollador, self.pathfinder)

if __name__ == '__main__':
    juego = Game()
    juego.ejecutar()
