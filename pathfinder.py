import heapq
from config import Config

# ==============================================================================
# CLASE 2: Buscador de Caminos (Pathfinder)
# Responsabilidad: Contener el algoritmo de búsqueda A*. Su único trabajo
# es recibir un inicio, un fin y obstáculos, y devolver el mejor camino.
# ==============================================================================
class Pathfinder:
    def __init__(self):
        self.clear()

    def clear(self):
        self.gscore = {}
        self.came_from = {}
        self.oheap = []
        self.close_set = set()
        self.goal_pos = None
        self.obstacle_grid = set()
        self.final_path = set()

    @staticmethod
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def a_star(start_node, goal_node, obstacles):
        start_pos = (start_node[0] // Config.GRID_SIZE, start_node[1] // Config.GRID_SIZE)
        goal_pos = (goal_node[0] // Config.GRID_SIZE, goal_node[1] // Config.GRID_SIZE)

        obstacle_grid = {(obs[0] // Config.GRID_SIZE, obs[1] // Config.GRID_SIZE) for obs in obstacles}

        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        gscore = {start_pos: 0}
        fscore = {start_pos: Pathfinder.heuristic(start_pos, goal_pos)}
        oheap = []
        heapq.heappush(oheap, (fscore[start_pos], start_pos))
        came_from = {}
        close_set = set()

        while oheap:
            current = heapq.heappop(oheap)[1]
            if current == goal_pos:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return [(p[0] * Config.GRID_SIZE + Config.GRID_SIZE // 2,
                         p[1] * Config.GRID_SIZE + Config.GRID_SIZE // 2) for p in path]

            close_set.add(current)
            for dx, dy in neighbors:
                neighbor = current[0] + dx, current[1] + dy
                tentative_g = gscore[current] + 1
                if tentative_g < gscore.get(neighbor, float('inf')):
                    is_valid = (0 <= neighbor[0] < Config.WIDTH // Config.GRID_SIZE and
                                Config.HUD_HEIGHT // Config.GRID_SIZE <= neighbor[1] < Config.HEIGHT // Config.GRID_SIZE and
                                (neighbor not in obstacle_grid or neighbor == goal_pos))
                    if is_valid:
                        came_from[neighbor] = current
                        gscore[neighbor] = tentative_g
                        fscore_val = tentative_g + Pathfinder.heuristic(neighbor, goal_pos)
                        heapq.heappush(oheap, (fscore_val, neighbor))
        return None

    def start_search(self, start_node, goal_node, obstacles):
        self.clear()
        self.goal_pos = (goal_node[0] // Config.GRID_SIZE, goal_node[1] // Config.GRID_SIZE)
        start_pos = (start_node[0] // Config.GRID_SIZE, start_node[1] // Config.GRID_SIZE)
        self.obstacle_grid = {(obs[0] // Config.GRID_SIZE, obs[1] // Config.GRID_SIZE) for obs in obstacles}

        self.gscore = {start_pos: 0}
        fscore = self.heuristic(start_pos, self.goal_pos)
        heapq.heappush(self.oheap, (fscore, start_pos))

    def step(self):
        if not self.oheap:
            return "NO_PATH"

        current = heapq.heappop(self.oheap)[1]
        if current == self.goal_pos:
            path = []
            while current in self.came_from:
                path.append(current)
                current = self.came_from[current]
            path.reverse()
            self.final_path = set(path)  # 🚨 Guardamos la ruta final
            return [(p[0] * Config.GRID_SIZE + Config.GRID_SIZE // 2,
                     p[1] * Config.GRID_SIZE + Config.GRID_SIZE // 2) for p in path]

        self.close_set.add(current)
        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in neighbors:
            neighbor = current[0] + dx, current[1] + dy
            tentative_g = self.gscore[current] + 1
            if tentative_g < self.gscore.get(neighbor, float('inf')):
                is_valid = (0 <= neighbor[0] < Config.WIDTH // Config.GRID_SIZE and
                            Config.HUD_HEIGHT // Config.GRID_SIZE <= neighbor[1] < Config.HEIGHT // Config.GRID_SIZE and
                            (neighbor not in self.obstacle_grid or neighbor == self.goal_pos))
                if is_valid and neighbor not in self.close_set:
                    self.came_from[neighbor] = current
                    self.gscore[neighbor] = tentative_g
                    fscore = tentative_g + self.heuristic(neighbor, self.goal_pos)
                    heapq.heappush(self.oheap, (fscore, neighbor))
        return "SEARCHING"
