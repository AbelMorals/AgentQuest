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
        self.pantalla = pygame.display.set_mode((Config.ANCHO, Config.ALTO), pygame.FULLSCREEN)
        pygame.display.set_caption("AgentQuest v3.0")
        self.reloj = pygame.time.Clock()
        self.estado_juego = 'SELECCION' 
        self.opciones_menu = list(Config.TEMAS.keys())[0]
        self.opcion_seleccionada = 0
        self.render = Render(self.pantalla, self.opciones_menu)
        self.pathfinder = None
        self.mundo = None
        self.robot = None 
        self.modo_desarrollador = False
        self.paso_dev = False  # para tecla S (paso a paso)
        self.mantener_dev = False  # para tecla A (continuo) 
        self._volver_al_menu_principal()

    def _volver_al_menu_principal(self):
        """ Reinicia el juego al estado inicial de selección de tema. """
        self.estado_juego = 'SELECCION'
        self.opciones_menu = list(Config.TEMAS.keys())
        self.opcion_seleccionada = 0
        self.renderizador = None
        self.pathfinder = None
        self.mundo = None
        self.robot = None
        self.modo_desarrollador = False
        self.paso_dev = False
        self.mantener_dev = False
        pygame.display.set_caption("AgentQuest v3.0")

    def reiniciar(self, tema_key):
        pygame.display.set_caption(Config.TEMAS[tema_key]["titulo"])
        self.render = Render(self.pantalla, tema_key)
        self.pathfinder = Pathfinder()
        self.mundo = World()
        self.robot = Robot(self.mundo.pos_inicio_robot[0], self.mundo.pos_inicio_robot[1])
        self.estado_juego = 'MENU'

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
                
                if evento.key == pygame.K_q and self.estado_juego != 'SELECCION':
                    self._volver_al_menu_principal()
                    continue
                if self.estado_juego == 'SELECCION':
                    if evento.key == pygame.K_UP:
                        self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones_menu)
                    elif evento.key == pygame.K_DOWN:
                        self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones_menu)
                    elif evento.key == pygame.K_RETURN:
                        tema_key_elegido = self.opciones_menu[self.opcion_seleccionada]
                        self.reiniciar(tema_key_elegido)
                    continue
                if evento.key == pygame.K_RETURN and self.estado_juego == 'MENU':
                    self.estado_juego = 'RUNNING'
                if evento.key == pygame.K_SPACE and self.estado_juego in ['RUNNING', 'PAUSED']:
                    self.estado_juego = 'PAUSED' if self.estado_juego == 'RUNNING' else 'RUNNING'
                if evento.key == pygame.K_r:
                    tema_actual_key = self.opciones_menu[self.opcion_seleccionada]
                    self.reiniciar(tema_actual_key)
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
        # if not self.render:
        #     self.pantalla.fill(Config.NEGRO)
        #     Render.dibujar_menu_seleccion(self.pantalla, self.opciones_menu, self.opcion_seleccionada)
        #     pygame.display.flip()
        #     return
            
        self.render.dibujar(
            self.estado_juego, 
            self.mundo, 
            self.robot, 
            self.modo_desarrollador, 
            self.pathfinder, 
            self.opciones_menu, 
            self.opcion_seleccionada
        )
if __name__ == '__main__':
    juego = Game()
    juego.ejecutar()
