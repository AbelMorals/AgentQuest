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
               modo_desarrollador=False, paso_dev=False, mantener_dev=False, obstaculos_extra=None):
        """Devuelve nuevo estado de juego si aplica (GAME_OVER, GAME_OVER_STUCK...), o None."""
        if self.carga <= 0 and self.estado != 'MUERTO':
            self.estado = 'MUERTO'
        if self.estado == 'MUERTO':
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

        # RECARGANDO
        if self.estado == 'RECARGANDO':
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
                # Obstáculos: pelotas, estación, canasta y obstáculos extra
                obstaculos = set(pelotas) | {rect_estacion.center, rect_canasta.center}
                if obstaculos_extra:
                    for rect_obs in obstaculos_extra:
                        # Añade todas las celdas ocupadas por el obstáculo
                        for i in range(rect_obs.left, rect_obs.right, Config.TAMANO_CELDA):
                            for j in range(rect_obs.top, rect_obs.bottom, Config.TAMANO_CELDA):
                                obstaculos.add((i + Config.TAMANO_CELDA // 2, j + Config.TAMANO_CELDA // 2))
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
        
        if not self.esta_moviendo or self.estado == 'MUERTO':
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
        if self.estado == 'RECOGIDO':
            return rect_canasta.center
        if self.estado == 'CARGAR':
            return rect_estacion.center

        if self.estado == 'BUSCANDO' and pelotas:
            mejor_pelota = None
            mejor_ruta = None
            mejor_longitud = math.inf
            for pelota in pelotas:
                obstaculos = set(pelotas) | {rect_estacion.center, rect_canasta.center}
                obstaculos.discard(pelota)
                ruta = pathfinder.a_estrella(self.rect.center, pelota, obstaculos)
                if ruta is not None and len(ruta) < mejor_longitud:
                    mejor_pelota = pelota
                    mejor_ruta = ruta
                    mejor_longitud = len(ruta)
            if mejor_pelota:
                self.pelota_objetivo = mejor_pelota
                return self.pelota_objetivo
        return None

    def _manejar_llegada(self, pelotas, rect_canasta, rect_estacion, pathfinder: Pathfinder):
        tarea_completada = False

        if self.estado == 'BUSCANDO' and not self.lleva_pelota:
            if self.pelota_objetivo and self.rect.collidepoint(self.pelota_objetivo):
                if self.pelota_objetivo in pelotas:
                    pelotas.remove(self.pelota_objetivo)
                self.lleva_pelota = True
                self.estado = 'RECOGIDO'
                self.pelota_objetivo = None
                tarea_completada = True

        elif self.estado == 'RECOGIDO':
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

        elif self.estado == 'CARGAR':
            if Robot.esta_contenido(self.rect, rect_estacion):
                self.estado = 'RECARGANDO'
                tarea_completada = True

        if tarea_completada:
            pathfinder.limpiar()

        return None

    def _verificar_bateria_emergencia(self, pelotas, rect_canasta, rect_estacion, pathfinder: Pathfinder):
        if self.carga <= Config.CARGA_EMERGENCIA and self.estado not in ['CARGAR', 'RECARGANDO']:
            # Si lleva la última pelota, verifica si puede llegar a la canasta
            if self.lleva_pelota and self.recogidas == Config.NUM_PELOTAS - 1:
                # Calcula ruta hasta la canasta
                ruta = pathfinder.a_estrella(self.rect.center, rect_canasta.center, pelotas + [rect_estacion.center])
                if ruta is not None:
                    distancia = len(ruta)
                    bateria_necesaria = distancia * Config.CARGA_POR_MOVIMIENTO
                    if self.carga >= bateria_necesaria * Config.MARGEN_SEGURIDAD_BATERIA:
                        # Puede llegar, no cambia a recargar
                        return
                # No puede llegar, suelta la pelota y va a recargar
                pelotas.append(self.rect.center)
                self.lleva_pelota = False
            elif self.lleva_pelota:
                pelotas.append(self.rect.center)
                self.lleva_pelota = False
            self.estado = 'CARGAR'
            self.ruta_actual = []
            self.esta_busqueda = False
            pathfinder.limpiar()