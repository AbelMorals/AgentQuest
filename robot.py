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
        self.camino_normal = []
        self.camino_dev = []
        self.direccion = (0, 1) # (x, y) -> Abajo por defecto

    def sincronizar_posicion_animacion(self):
        self.objetivo_pixel_x = self.rect.x
        self.objetivo_pixel_y = self.rect.y
        self.esta_moviendo = False
        
    def actualizar(self, pelotas, rect_estacion, rect_canasta, pathfinder: Pathfinder,
               modo_desarrollador=False, paso_dev=False, mantener_dev=False, obstaculos_extra=None):
        if self.carga <= 0 and self.estado != 'MUERTO': self.estado = 'MUERTO'
        if self.estado == 'MUERTO':
            return None

        # El modo dev no tiene enfriamiento de decisión
        if modo_desarrollador:
            if not (mantener_dev or paso_dev):
                return None
        # En modo normal, si se está animando un movimiento, no toma decisiones nuevas
        elif self.esta_moviendo:
            return None

        if self.estado == 'RECARGANDO':
            if self.carga < Config.CARGA_MAXIMA:
                self.carga += Config.TASA_RECARGA
            else:
                self.carga = Config.CARGA_MAXIMA
                self.estado = 'BUSCANDO'
            return None

        # 1. PRIMERO, si hemos llegado a un destino, procesamos la llegada.
        if not self.esta_moviendo and not self.ruta_actual:
            resultado_llegada = self._manejar_llegada(pelotas, rect_canasta, rect_estacion, pathfinder)
            if resultado_llegada:
                return resultado_llegada

        # 2. SEGUNDO, si después de llegar seguimos sin ruta, buscamos una nueva.
        if not self.ruta_actual:
            tiempo_actual = pygame.time.get_ticks()
            if not modo_desarrollador and tiempo_actual - self.ultima_decision < Config.enfriamiento_decision_robot:
                return None
            
            # Lógica de búsqueda A* para modo desarrollador
            if modo_desarrollador and self.esta_busqueda:
                if mantener_dev or paso_dev:
                    resultado = pathfinder.paso()
                    if isinstance(resultado, list):
                        self.ruta_actual = resultado
                        self.esta_busqueda = False
                        self.contador_atascado = 0
                    elif resultado == "NO_PATH":
                        self.esta_busqueda = False
                        self.contador_atascado += 1
                        if self.contador_atascado >= Config.MAX_TURNOS_ATASCADO:
                            return 'GAME_OVER_STUCK'
                return None
            
            self._verificar_bateria_emergencia(pelotas, rect_canasta, rect_estacion, pathfinder)
            
            obstaculos = set(p for p in pelotas) | {rect_estacion.center, rect_canasta.center}
            if obstaculos_extra:
                for rect_obs in obstaculos_extra:
                    for i in range(rect_obs.left, rect_obs.right, Config.TAMANO_CELDA):
                        for j in range(rect_obs.top, rect_obs.bottom, Config.TAMANO_CELDA):
                            obstaculos.add((i + Config.TAMANO_CELDA // 2, j + Config.TAMANO_CELDA // 2))

            objetivo = self._obtener_objetivo(pelotas, rect_canasta, rect_estacion, obstaculos, pathfinder, modo_desarrollador)

            if objetivo:
                if self.estado == 'BUSCANDO' and self.pelota_objetivo in obstaculos:
                    obstaculos.discard(self.pelota_objetivo)

                if modo_desarrollador:
                    pathfinder.iniciar_busqueda(self.rect.center, objetivo, obstaculos)
                    self.esta_busqueda = True
                else:
                    ruta = pathfinder.a_estrella(self.rect.center, objetivo, obstaculos)
                    if ruta is not None:
                        self.ruta_actual = ruta
                        self.contador_atascado = 0
                        # Reiniciar el timer solo después de una decisión exitosa
                        self.ultima_decision = tiempo_actual
                    else:
                        self.contador_atascado += 1
                        if self.contador_atascado >= Config.MAX_TURNOS_ATASCADO:
                            return 'GAME_OVER_STUCK'

        # 3. TERCERO, si ya tenemos una ruta, avanzamos un paso.
        if self.ruta_actual:
            if modo_desarrollador:
                siguiente = self.ruta_actual.pop(0)
                self.rect.x = siguiente[0] - Config.TAMANO_CELDA // 2
                self.rect.y = siguiente[1] - Config.TAMANO_CELDA // 2
                self.carga -= Config.CARGA_POR_MOVIMIENTO
                self.camino_dev.append(self.rect.center)
                if not self.ruta_actual:
                    resultado_llegada = self._manejar_llegada(pelotas, rect_canasta, rect_estacion, pathfinder)
                    if resultado_llegada:
                        return resultado_llegada
            else: # Modo Normal
                siguiente = self.ruta_actual.pop(0)
                dx = siguiente[0] - self.rect.centerx
                dy = siguiente[1] - self.rect.centery
                if dx != 0 or dy != 0:
                    self.direccion = (dx // abs(dx) if dx != 0 else 0, dy // abs(dy) if dy != 0 else 0)
                    
                self.objetivo_pixel_x = siguiente[0] - Config.TAMANO_CELDA // 2
                self.objetivo_pixel_y = siguiente[1] - Config.TAMANO_CELDA // 2
                self.esta_moviendo = True
                self.carga -= Config.CARGA_POR_MOVIMIENTO
                self.camino_normal.append((self.objetivo_pixel_x, self.objetivo_pixel_y))
        
        return None

    def animar_movimiento(self, modo_desarrollador=False):
        if modo_desarrollador:
            return 
        if not self.esta_moviendo or self.estado == 'MUERTO':
            return

        if self.rect.x != self.objetivo_pixel_x:
            self.rect.x += self.direccion[0] * Config.VELOCIDAD_ANIMACION_ROBOT
            if (self.direccion[0] > 0 and self.rect.x >= self.objetivo_pixel_x) or (self.direccion[0] < 0 and self.rect.x <= self.objetivo_pixel_x):
                self.rect.x = self.objetivo_pixel_x
        elif self.rect.y != self.objetivo_pixel_y:
            self.rect.y += self.direccion[1] * Config.VELOCIDAD_ANIMACION_ROBOT
            if (self.direccion[1] > 0 and self.rect.y >= self.objetivo_pixel_y) or (self.direccion[1] < 0 and self.rect.y <= self.objetivo_pixel_y):
                self.rect.y = self.objetivo_pixel_y
        else:
            self.esta_moviendo = False

    def _encontrar_posicion_entrega(self, rect_objetivo, obstaculos):
        vecinos = [(0, -1), (0, 1), (-1, 0), (1, 0)] # Arriba, Abajo, Izquierda, Derecha
        posiciones_posibles = []
        for dx, dy in vecinos:
            x = rect_objetivo.centerx + dx * Config.TAMANO_CELDA
            y = rect_objetivo.centery + dy * Config.TAMANO_CELDA
            pos = (x, y)
            if pos not in obstaculos:
                posiciones_posibles.append(pos)
        
        if not posiciones_posibles:
            return None 

        # Devuelve la posición más cercana al robot
        posiciones_posibles.sort(key=lambda p: Pathfinder.heuristica(self.rect.center, p))
        return posiciones_posibles[0]
    
    def _obtener_objetivo(self, pelotas, rect_canasta, rect_estacion, obstaculos, pathfinder: Pathfinder, modo_desarrollador=False):
        if self.estado == 'RECOGIDO':
            return self._encontrar_posicion_entrega(rect_canasta, obstaculos)
        if self.estado == 'CARGAR':
            return rect_estacion.center

        if self.estado == 'BUSCANDO' and pelotas:
            mejor_pelota = None
            distancia_minima = math.inf
            for pelota in pelotas:
                distancia = pathfinder.heuristica(self.rect.center, pelota)
                if distancia < distancia_minima:
                    distancia_minima = distancia
                    mejor_pelota = pelota
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
            distancia = Pathfinder.heuristica(self.rect.center, rect_canasta.center)
            if distancia <= Config.TAMANO_CELDA:
                self.recogidas += 1
                self.lleva_pelota = False
                if self.recogidas == Config.NUM_PELOTAS:
                    pathfinder.limpiar()
                    return 'GAME_OVER'
                else:
                    self.estado = 'BUSCANDO'
                    tarea_completada = True
                    pathfinder.limpiar()

        elif self.estado == 'CARGAR':
            if Robot.esta_contenido(self.rect, rect_estacion):
                self.estado = 'RECARGANDO'
                tarea_completada = True

        if tarea_completada:
            # --- PUESTO: Reiniciar el temporizador al completar una tarea ---
            self.ultima_decision = pygame.time.get_ticks()
            pathfinder.limpiar()

        return None

    def _verificar_bateria_emergencia(self, pelotas, rect_canasta, rect_estacion, pathfinder: Pathfinder):
        if self.carga <= Config.CARGA_EMERGENCIA and self.estado not in ['CARGAR', 'RECARGANDO']:
            if self.lleva_pelota:
                pos_detras_x = self.rect.centerx - self.direccion[0] * Config.TAMANO_CELDA
                pos_detras_y = self.rect.centery - self.direccion[1] * Config.TAMANO_CELDA
                pelotas.append((pos_detras_x, pos_detras_y))
                self.lleva_pelota = False
                self.pelota_objetivo = None
            
            self.estado = 'CARGAR'
            self.ruta_actual = []
            self.esta_busqueda = False
            pathfinder.limpiar()