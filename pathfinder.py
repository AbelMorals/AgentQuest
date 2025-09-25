import heapq
from config import Config

# ==============================================================================
# CLASE 2: Buscador de Caminos (Pathfinder)
# Responsabilidad: Contener el algoritmo de búsqueda A*. Su único trabajo
# es recibir un inicio, un fin y obstáculos, y devolver el mejor camino.
# ==============================================================================
class Pathfinder:
    @staticmethod
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def a_star(start_node, goal_node, obstacles):
        start_pos = (start_node[0] // Config.GRID_SIZE, start_node[1] // Config.GRID_SIZE)
        goal_pos = (goal_node[0] // Config.GRID_SIZE, goal_node[1] // Config.GRID_SIZE)
        
        obstacle_grid = {(obs[0] // Config.GRID_SIZE, obs[1] // Config.GRID_SIZE) for obs in obstacles}
        
        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        close_set = set(); came_from = {}
        gscore = {start_pos: 0}
        fscore = {start_pos: Pathfinder.heuristic(start_pos, goal_pos)}
        oheap = []
        heapq.heappush(oheap, (fscore[start_pos], start_pos))
        
        while oheap:
            current = heapq.heappop(oheap)[1]
            if current == goal_pos:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return [(pos[0] * Config.GRID_SIZE + Config.GRID_SIZE // 2, pos[1] * Config.GRID_SIZE + Config.GRID_SIZE // 2) for pos in path]

            close_set.add(current)
            for i, j in neighbors:
                neighbor = current[0] + i, current[1] + j            
                tentative_g_score = gscore[current] + 1
                if tentative_g_score < gscore.get(neighbor, float('inf')):
                    is_valid = 0 <= neighbor[0] < Config.WIDTH // Config.GRID_SIZE and \
                               Config.HUD_HEIGHT // Config.GRID_SIZE <= neighbor[1] < Config.HEIGHT // Config.GRID_SIZE and \
                               (neighbor not in obstacle_grid or neighbor == goal_pos)
                    if is_valid:
                        came_from[neighbor] = current
                        gscore[neighbor] = tentative_g_score
                        fscore[neighbor] = tentative_g_score + Pathfinder.heuristic(neighbor, goal_pos)
                        if neighbor not in oheap:
                            heapq.heappush(oheap, (fscore[neighbor], neighbor))
        return None