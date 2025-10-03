import heapq
from config import Config

# ==============================================================================
# CLASE 2: Buscador de Caminos (Pathfinder)
# Responsabilidad: Contener el algoritmo de búsqueda A*. Su único trabajo
# es recibir un inicio, un fin y obstáculos, y devolver el mejor camino.
# ==============================================================================
class Pathfinder:
    def __init__(self):
        self.limpiar()

    def limpiar(self):
        self.puntaje_g = {}
        self.viene_de = {}
        self.lista_abierta = []
        self.lista_cerrada = set()
        self.pos_objetivo = None
        self.celdas_obstaculos = set()
        self.camino_final = set()

    @staticmethod
    def heuristica(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def a_estrella(nodo_inicio, nodo_objetivo, obstaculos):
        pos_inicio = (nodo_inicio[0] // Config.TAMANO_CELDA, nodo_inicio[1] // Config.TAMANO_CELDA)
        pos_objetivo = (nodo_objetivo[0] // Config.TAMANO_CELDA, nodo_objetivo[1] // Config.TAMANO_CELDA)

        celdas_obstaculos = {(obs[0] // Config.TAMANO_CELDA, obs[1] // Config.TAMANO_CELDA) for obs in obstaculos}

        vecinos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        puntaje_g = {pos_inicio: 0}
        puntaje_h = {pos_inicio: Pathfinder.heuristica(pos_inicio, pos_objetivo)}
        lista_abierta = []
        heapq.heappush(lista_abierta, (puntaje_h[pos_inicio], pos_inicio))
        viene_de = {}
        lista_cerrada = set()

        while lista_abierta:
            actual = heapq.heappop(lista_abierta)[1]
            if actual == pos_objetivo:
                camino = []
                while actual in viene_de:
                    camino.append(actual)
                    actual = viene_de[actual]
                camino.reverse()
                return [(p[0] * Config.TAMANO_CELDA + Config.TAMANO_CELDA // 2,
                         p[1] * Config.TAMANO_CELDA + Config.TAMANO_CELDA // 2) for p in camino]

            lista_cerrada.add(actual)
            for dx, dy in vecinos:
                vecino = actual[0] + dx, actual[1] + dy
                g_tentativo = puntaje_g[actual] + 1
                if g_tentativo < puntaje_g.get(vecino, float('inf')):
                    es_valido = (0 <= vecino[0] < Config.ANCHO // Config.TAMANO_CELDA and
                                 Config.ALTURA_HUD // Config.TAMANO_CELDA <= vecino[1] < Config.ALTO // Config.TAMANO_CELDA and
                                 (vecino not in celdas_obstaculos or vecino == pos_objetivo))
                    if es_valido:
                        viene_de[vecino] = actual
                        puntaje_g[vecino] = g_tentativo
                        puntaje_f = g_tentativo + Pathfinder.heuristica(vecino, pos_objetivo)
                        heapq.heappush(lista_abierta, (puntaje_f, vecino))
        return None

    def iniciar_busqueda(self, nodo_inicio, nodo_objetivo, obstaculos):
        self.limpiar()
        self.pos_objetivo = (nodo_objetivo[0] // Config.TAMANO_CELDA, nodo_objetivo[1] // Config.TAMANO_CELDA)
        pos_inicio = (nodo_inicio[0] // Config.TAMANO_CELDA, nodo_inicio[1] // Config.TAMANO_CELDA)
        self.celdas_obstaculos = {(obs[0] // Config.TAMANO_CELDA, obs[1] // Config.TAMANO_CELDA) for obs in obstaculos}

        self.puntaje_g = {pos_inicio: 0}
        puntaje_h = self.heuristica(pos_inicio, self.pos_objetivo)
        heapq.heappush(self.lista_abierta, (puntaje_h, pos_inicio))

    def paso(self):
        if not self.lista_abierta:
            return "SIN_CAMINO"

        actual = heapq.heappop(self.lista_abierta)[1]
        if actual == self.pos_objetivo:
            camino = []
            while actual in self.viene_de:
                camino.append(actual)
                actual = self.viene_de[actual]
            camino.reverse()
            self.camino_final = set(camino)
            return [(p[0] * Config.TAMANO_CELDA + Config.TAMANO_CELDA // 2,
                     p[1] * Config.TAMANO_CELDA + Config.TAMANO_CELDA // 2) for p in camino]

        self.lista_cerrada.add(actual)
        vecinos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in vecinos:
            vecino = actual[0] + dx, actual[1] + dy
            g_tentativo = self.puntaje_g[actual] + 1
            if g_tentativo < self.puntaje_g.get(vecino, float('inf')):
                es_valido = (0 <= vecino[0] < Config.ANCHO // Config.TAMANO_CELDA and
                            Config.ALTURA_HUD // Config.TAMANO_CELDA <= vecino[1] < Config.ALTO // Config.TAMANO_CELDA and
                            (vecino not in self.celdas_obstaculos or vecino == self.pos_objetivo))
                if es_valido and vecino not in self.lista_cerrada:
                    self.viene_de[vecino] = actual
                    self.puntaje_g[vecino] = g_tentativo
                    puntaje_h = g_tentativo + self.heuristica(vecino, self.pos_objetivo)
                    heapq.heappush(self.lista_abierta, (puntaje_h, vecino))
        return "SEARCHING"
