import math
import pygame
from config import Config
from pathfinder import Pathfinder


# ==============================================================================
# CLASE 3: Robot (Lógica)
# Responsabilidad: Toda la "inteligencia" y el estado del robot. Decide
# QUÉ hacer (su objetivo) y gestiona su estado interno (batería, etc.).
# ==============================================================================
class Robot:
    @staticmethod
    def esta_contenido(rect1, rect2):
        return rect1.left >= rect2.left and rect1.right <= rect2.right and \
               rect1.top >= rect2.top and rect1.bottom <= rect2.bottom

    def __init__(self, pos_x, pos_y):
        self.rect = pygame.Rect(pos_x, pos_y, Config.TAMANO_CELDA, Config.TAMANO_CELDA)
        self.carga = Config.CARGA_MAXIMA
        self.estado = 'BUSCANDO'
        self.lleva_pelota = False
        self.pelota_objetivo = None
        self.recogidas = 0
        self.ultima_decision = 0
        self.esta_moviendo = False
        self.objetivo_pixel_x = pos_x
        self.objetivo_pixel_y = pos_y
        self.ruta_actual = []
        self.contador_atascado = 0
        self.esta_busqueda = False
        self.dev_desbloqueado = False
        self.camino_normal = []  # Guarda el camino recorrido en modo normal
        self.camino_dev = []     # Guarda el camino recorrido en modo dev

    def actualizar(self, pelotas, rect_estacion, rect_canasta, pathfinder: Pathfinder,
               modo_desarrollador=False, paso_dev=False, mantener_dev=False):
        """Devuelve nuevo estado de juego si aplica (GAME_OVER, GAME_OVER_STUCK...), o None."""
        if self.carga <= 0 and self.estado != 'DEAD':
            self.estado = 'DEAD'
        if self.estado == 'DEAD':
            return None

        # En modo desarrollador avanzamos SOLO si se pide (tecla A) o se mantiene A pulsada.
        if modo_desarrollador:
            if not (mantener_dev or paso_dev):
                return None
        else:
            tiempo_actual = pygame.time.get_ticks()
            if self.esta_moviendo or tiempo_actual - self.ultima_decision < Config.enfriamiento_decision_robot:
                return None
            self.ultima_decision = tiempo_actual

        # RECHARGING
        if self.estado == 'RECHARGING':
            if self.carga < Config.CARGA_MAXIMA:
                self.carga += Config.TASA_RECARGA
            else:
                self.carga = Config.CARGA_MAXIMA
                self.estado = 'BUSCANDO'
            return None

        # 1) Si estamos en una búsqueda A* paso a paso (modo desarrollador)
        if self.esta_busqueda:
            if modo_desarrollador:
                if mantener_dev or paso_dev:
                    resultado = pathfinder.paso()
                    if isinstance(resultado, list):
                        self.ruta_actual = resultado
                        pathfinder.final_path = [(p[0] // Config.TAMANO_CELDA, p[1] // Config.TAMANO_CELDA) for p in resultado]
                        self.esta_busqueda = False
                        self.contador_atascado = 0
                    elif resultado == "NO_PATH":
                        self.esta_busqueda = False
                        self.contador_atascado += 1
                        if self.contador_atascado >= Config.MAX_TURNOS_ATASCADO:
                            return 'GAME_OVER_STUCK'
            else:
                pass
            return None

        # 2) Si no tenemos ruta actual, decidimos objetivo y calculamos ruta (modo normal)
        if not self.ruta_actual:
            self._verificar_bateria_emergencia(pelotas, rect_canasta, rect_estacion, pathfinder)

            objetivo = self._obtener_objetivo(pelotas, rect_canasta, rect_estacion, pathfinder, modo_desarrollador)
            if objetivo:
                obstaculos = set(pelotas) | {rect_estacion.center, rect_canasta.center}
                if self.estado == 'BUSCANDO' and self.pelota_objetivo in obstaculos:
                    obstaculos.discard(self.pelota_objetivo)

                if modo_desarrollador:
                    pathfinder.iniciar_busqueda(self.rect.center, objetivo, obstaculos)
                    self.esta_busqueda = True
                else:
                    ruta = pathfinder.a_estrella(self.rect.center, objetivo, obstaculos)
                    if ruta is not None:
                        self.ruta_actual = ruta
                        pathfinder.final_path = [(p[0] // Config.TAMANO_CELDA, p[1] // Config.TAMANO_CELDA) for p in ruta]
                        self.contador_atascado = 0
                    else:
                        self.contador_atascado += 1
                        if self.contador_atascado >= Config.MAX_TURNOS_ATASCADO:
                            return 'GAME_OVER_STUCK'

        # 3) Si tenemos ruta, avanzamos un paso (modo normal: animación, dev: celda por celda)
        if self.ruta_actual:
            if modo_desarrollador:
                siguiente = self.ruta_actual.pop(0)
                self.rect.x = siguiente[0] - Config.TAMANO_CELDA // 2
                self.rect.y = siguiente[1] - Config.TAMANO_CELDA // 2
                self.carga -= Config.CARGA_POR_MOVIMIENTO
                self.camino_dev.append(self.rect.center)
                # Procesar llegada automáticamente en modo dev
                resultado_llegada = self._manejar_llegada(pelotas, rect_canasta, rect_estacion, pathfinder)
                if resultado_llegada:
                    return resultado_llegada
            else:
                siguiente = self.ruta_actual.pop(0)
                self.objetivo_pixel_x = siguiente[0] - Config.TAMANO_CELDA // 2
                self.objetivo_pixel_y = siguiente[1] - Config.TAMANO_CELDA // 2
                self.esta_moviendo = True
                self.carga -= Config.CARGA_POR_MOVIMIENTO
                self.camino_normal.append((self.objetivo_pixel_x, self.objetivo_pixel_y))

        # 4) Si no está moviéndose y no tiene ruta, comprobamos llegada (lógica de objetivo)
        if not self.esta_moviendo and not self.ruta_actual:
            return self._manejar_llegada(pelotas, rect_canasta, rect_estacion, pathfinder)

        return None

    def animar_movimiento(self, modo_desarrollador=False):
        if modo_desarrollador:
            return 
        
        if not self.esta_moviendo or self.estado == 'DEAD':
            return

        if self.rect.x != self.objetivo_pixel_x:
            direccion = 1 if self.objetivo_pixel_x > self.rect.x else -1
            self.rect.x += Config.VELOCIDAD_ANIMACION_ROBOT * direccion
            if (direccion == 1 and self.rect.x >= self.objetivo_pixel_x) or (direccion == -1 and self.rect.x <= self.objetivo_pixel_x):
                self.rect.x = self.objetivo_pixel_x
        elif self.rect.y != self.objetivo_pixel_y:
            direccion = 1 if self.objetivo_pixel_y > self.rect.y else -1
            self.rect.y += Config.VELOCIDAD_ANIMACION_ROBOT * direccion
            if (direccion == 1 and self.rect.y >= self.objetivo_pixel_y) or (direccion == -1 and self.rect.y <= self.objetivo_pixel_y):
                self.rect.y = self.objetivo_pixel_y
        else:
            self.esta_moviendo = False

    def _obtener_objetivo(self, pelotas, rect_canasta, rect_estacion, pathfinder: Pathfinder, modo_desarrollador=False):
        if self.estado == 'COLLECTING':
            return rect_canasta.center
        if self.estado == 'CHARGING':
            return rect_estacion.center

        if self.estado == 'BUSCANDO' and pelotas:
            pelotas_ordenadas = sorted(pelotas, key=lambda pelota: abs(pelota[0] - self.rect.centerx) + abs(pelota[1] - self.rect.centery))
            if modo_desarrollador:
                self.pelota_objetivo = pelotas_ordenadas[0]
                return self.pelota_objetivo
            else:
                for pelota in pelotas_ordenadas:
                    obstaculos = set(pelotas) | {rect_estacion.center, rect_canasta.center}
                    obstaculos.discard(pelota)
                    if pathfinder.a_estrella(self.rect.center, pelota, obstaculos) is not None:
                        self.pelota_objetivo = pelota
                        return self.pelota_objetivo
        return None

    def _manejar_llegada(self, pelotas, rect_canasta, rect_estacion, pathfinder: Pathfinder):
        tarea_completada = False

        if self.estado == 'BUSCANDO' and not self.lleva_pelota:
            if self.pelota_objetivo and self.rect.collidepoint(self.pelota_objetivo):
                if self.pelota_objetivo in pelotas:
                    pelotas.remove(self.pelota_objetivo)
                self.lleva_pelota = True
                self.estado = 'COLLECTING'
                self.pelota_objetivo = None
                tarea_completada = True

        elif self.estado == 'COLLECTING':
            if Robot.esta_contenido(self.rect, rect_canasta):
                self.recogidas += 1
                self.lleva_pelota = False
                if self.recogidas == Config.NUM_PELOTAS:
                    pathfinder.limpiar()
                    return 'GAME_OVER'
                else:
                    self.estado = 'BUSCANDO'
                    tarea_completada = True
                    pathfinder.limpiar()
                    if self.recogidas == 1:
                        self.dev_desbloqueado = True

        elif self.estado == 'CHARGING':
            if Robot.esta_contenido(self.rect, rect_estacion):
                self.estado = 'RECHARGING'
                tarea_completada = True

        if tarea_completada:
            pathfinder.limpiar()

        return None

    def _verificar_bateria_emergencia(self, pelotas, rect_canasta, rect_estacion, pathfinder: Pathfinder):
        if self.carga <= Config.CARGA_EMERGENCIA and self.estado not in ['CHARGING', 'RECHARGING']:
            if self.lleva_pelota:
                pelotas.append(self.rect.center)
                self.lleva_pelota = False
            self.estado = 'CHARGING'
            self.ruta_actual = []
            self.esta_busqueda = False
            pathfinder.limpiar()