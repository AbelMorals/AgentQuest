# game.py (Versión Completa y Final)
import pygame
import sys
import os
from config import Config
from render import Render
from robot import Robot
from world import World
from pathfinder import Pathfinder

pygame.init()
# ==============================================================================
# CLASE 6: Juego (Game)
# Responsabilidad: Orquestar todo. Contener el bucle principal, gestionar
# los eventos y decirle a las otras clases cuándo actuar.
# ==============================================================================
class Game:
    def __init__(self):
        # Configuración de la Pantalla
        self.pantalla = pygame.display.set_mode((Config.ANCHO, Config.ALTO), pygame.FULLSCREEN)
        pygame.display.set_caption("AgentQuest v3.0")
        self.reloj = pygame.time.Clock()

        # GESTIÓN DE AUDIO (Inicialización)
        pygame.mixer.init()

        # Ruta de la carpeta de sonidos (asumiendo 'Sonido' singular)
        self.ruta_base_sonidos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Sonido")
        # Canal para efectos de sonido (SFX) para no interferir con la música
        self.canal_sfx = pygame.mixer.Channel(0) 

        # Variables de Juego/Menú
        self.pathfinder = None
        self.mundo = None
        self.robot = None 
        self.modo_desarrollador = False
        self.paso_dev = False
        self.mantener_dev = False
        
        # Inicialización del Renderizador
        tema_default = list(Config.TEMAS.keys())[0]
        self.render = Render(self.pantalla, tema_default) 
        self.tema_elegido = tema_default
        
        # Iniciar el juego en el menú de selección de tema y la música del menú
        self._volver_al_menu_principal()

    # LÓGICA DE AUDIO
    
    def reproducir_sfx(self, nombre_archivo, loop=0):
        """Carga y reproduce un efecto de sonido sin detener la música."""
        try:
            ruta = os.path.join(self.ruta_base_sonidos, nombre_archivo)
            sfx = pygame.mixer.Sound(ruta)
            self.canal_sfx.play(sfx, loop)
            return True
        except Exception as e:
            print(f"Advertencia: No se pudo cargar el SFX '{nombre_archivo}': {e}")
            return False

    def cargar_musica_menu(self):
        """Carga y reproduce la música de fondo para los estados de menú/selección."""
        try:
            pygame.mixer.music.stop() 
            self.canal_sfx.stop() 
            ruta = os.path.join(self.ruta_base_sonidos, Config.MUSICA_MENU)
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Advertencia: No se pudo cargar la música del menú: {e}")

    def cargar_musica_tema(self):
        """Carga y reproduce la música de fondo del tema actualmente elegido."""
        if not self.tema_elegido:
            pygame.mixer.music.stop()
            return
            
        tema = Config.TEMAS[self.tema_elegido]
        nombre_musica = tema.get("musica_fondo")
        
        if nombre_musica:
            try:
                pygame.mixer.music.stop() 
                self.canal_sfx.stop() 
                ruta = os.path.join(self.ruta_base_sonidos, nombre_musica)
                pygame.mixer.music.load(ruta)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Advertencia: No se pudo cargar la música del tema '{self.tema_elegido}': {e}")
        else:
            pygame.mixer.music.stop()
            

    # LÓGICA DE ESTADO Y MENÚ

    def _volver_al_menu_principal(self):
        """Reinicia el juego al estado inicial de selección de tema."""
        self.estado_juego = 'SELECCION'
        self.opciones_menu = list(Config.TEMAS.keys())
        self.opcion_seleccionada = 0
        self.pathfinder = None
        self.mundo = None
        self.robot = None
        self.modo_desarrollador = False
        self.cargar_musica_menu() 
        pygame.display.set_caption("AgentQuest v3.0")

    def reiniciar(self, tema_key):
        """Prepara el mundo, el robot y el renderizador para el tema seleccionado."""
        self.tema_elegido = tema_key
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
                
                # Regresar a SELECCION (Q)
                if evento.key == pygame.K_q and self.estado_juego != 'SELECCION':
                    self._volver_al_menu_principal()
                    continue
                
                if self.estado_juego == 'SELECCION':
                    # Lógica de navegación de SELECCION DE TEMA
                    if evento.key == pygame.K_UP:
                        self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones_menu)
                    elif evento.key == pygame.K_DOWN:
                        self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones_menu)
                    elif evento.key == pygame.K_RETURN:
                        tema_key_elegido = self.opciones_menu[self.opcion_seleccionada]
                        self.reiniciar(tema_key_elegido)
                    continue
                
                # Iniciar la simulación desde el menú (ENTER)
                if evento.key == pygame.K_RETURN and self.estado_juego == 'MENU':
                    self.estado_juego = 'RUNNING'
                    self.cargar_musica_tema()
                    continue

                # Lógica de PAUSA/REANUDAR (SPACE)
                if evento.key == pygame.K_SPACE and self.estado_juego in ['RUNNING', 'PAUSED']:
                    if self.estado_juego == 'RUNNING':
                        self.estado_juego = 'PAUSED'
                        pygame.mixer.music.pause()
                    else:
                        self.estado_juego = 'RUNNING'
                        pygame.mixer.music.unpause()
                    continue

                # Lógica de REINICIO SUAVE (R)
                if evento.key == pygame.K_r and self.tema_elegido and self.estado_juego != 'SELECCION':
                    self.reiniciar(self.tema_elegido) 
                    self.cargar_musica_tema() # Asegura que la música del tema suene en el menú del mundo
                    continue 
                    
                # Lógica de Modo Desarrollador (D y S)
                if evento.key == pygame.K_d and self.robot:
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
            self.mundo.pelotas, self.mundo.rect_estacion, self.mundo.rect_canasta, self.pathfinder,
            modo_desarrollador=self.modo_desarrollador, paso_dev=self.paso_dev, 
            mantener_dev=self.mantener_dev, obstaculos_extra=getattr(self.mundo, 'obstaculos', None)
        )

        self.paso_dev = False

        if nuevo_estado:
            self.estado_juego = nuevo_estado
            
            # Detener la música de fondo y reproducir SFX
            pygame.mixer.music.stop()
            
            if nuevo_estado == 'GAME_OVER': # Éxito: Pelotas entregadas
                self.reproducir_sfx(Config.SONIDO_VICTORIA)
                
            elif nuevo_estado in ['MUERTO', 'GAME_OVER_STUCK']: # Fallo: Batería agotada o Atascado
                tema_assets = Config.TEMAS[self.tema_elegido]
                nombre_gameover = tema_assets.get("sonido_gameover")
                if nombre_gameover:
                    self.reproducir_sfx(nombre_gameover)
        self.robot.animar_movimiento(self.modo_desarrollador)

    def dibujar(self):
        self.render.dibujar(
            self.estado_juego, self.mundo, self.robot, self.modo_desarrollador, 
            self.pathfinder, self.opciones_menu, self.opcion_seleccionada
        )


if __name__ == '__main__':
    juego = Game()
    juego.ejecutar()