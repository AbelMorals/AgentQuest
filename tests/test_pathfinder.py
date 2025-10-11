import unittest
import sys
import os

# Añadimos la ruta principal del proyecto para que Python encuentre los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathfinder import Pathfinder
from config import Config

class TestPathfinder(unittest.TestCase):

    def test_ruta_directa_sin_obstaculos(self):
        """
        Prueba el escenario más simple: un camino recto sin nada en medio.
        """
        # CORRECCIÓN: Se movió el eje Y para estar dentro del área de juego (debajo del HUD)
        y_pos = Config.ALTURA_HUD + Config.TAMANO_CELDA // 2
        inicio = (Config.TAMANO_CELDA // 2, y_pos)
        fin = (Config.TAMANO_CELDA * 5 + Config.TAMANO_CELDA // 2, y_pos)
        obstaculos = set()

        ruta = Pathfinder.a_estrella(inicio, fin, obstaculos)
        
        self.assertIsNotNone(ruta, "La ruta no debería ser None en un camino despejado")
        self.assertEqual(len(ruta), 5, "La longitud de la ruta directa debe ser 5")
        self.assertEqual(ruta[-1], fin, "El final de la ruta debe ser el destino")
        print("\nPrueba de ruta directa: SUPERADA")

    def test_ruta_rodeando_obstaculo(self):
        """
        Prueba un escenario donde el agente debe rodear un muro simple.
        """
        # CORRECCIÓN: Se movió el eje Y para estar dentro del área de juego
        y_base = Config.ALTURA_HUD
        inicio = (Config.TAMANO_CELDA // 2, y_base + Config.TAMANO_CELDA // 2)
        fin = (Config.TAMANO_CELDA * 5 + Config.TAMANO_CELDA // 2, y_base + Config.TAMANO_CELDA // 2)
        
        # Creamos un muro vertical
        obstaculos = set()
        for i in range(5):
            # Aseguramos que el muro también esté en la zona jugable
            obstaculos.add((Config.TAMANO_CELDA * 2 + Config.TAMANO_CELDA // 2, y_base + Config.TAMANO_CELDA * i + Config.TAMANO_CELDA // 2))

        ruta = Pathfinder.a_estrella(inicio, fin, obstaculos)
        
        self.assertIsNotNone(ruta, "La ruta no debería ser None al rodear un obstáculo")
        self.assertTrue(len(ruta) > 5, "La ruta para rodear un obstáculo debe ser más larga que una línea recta")
        self.assertEqual(ruta[-1], fin, "El final de la ruta debe ser el destino")
        print("Prueba de ruta con obstáculo: SUPERADA")

    def test_sin_ruta_posible(self):
        """
        Prueba un escenario donde el destino está completamente rodeado.
        """
        # CORRECCIÓN: Se movió el eje Y para estar dentro del área de juego
        y_base = Config.ALTURA_HUD
        inicio = (Config.TAMANO_CELDA // 2, y_base + Config.TAMANO_CELDA // 2)
        fin = (Config.TAMANO_CELDA * 5 + Config.TAMANO_CELDA // 2, y_base + Config.TAMANO_CELDA // 2)

        # Rodeamos el destino con obstáculos
        obstaculos = {
            (Config.TAMANO_CELDA * 4 + Config.TAMANO_CELDA // 2, y_base + Config.TAMANO_CELDA // 2),
            (Config.TAMANO_CELDA * 6 + Config.TAMANO_CELDA // 2, y_base + Config.TAMANO_CELDA // 2),
            (Config.TAMANO_CELDA * 5 + Config.TAMANO_CELDA // 2, y_base + Config.TAMANO_CELDA + Config.TAMANO_CELDA // 2),
            (Config.TAMANO_CELDA * 5 + Config.TAMANO_CELDA // 2, y_base) # Muro superior
        }
        
        ruta = Pathfinder.a_estrella(inicio, fin, obstaculos)
        
        self.assertIsNone(ruta, "La ruta debe ser None si el destino está bloqueado")
        print("Prueba sin ruta posible: SUPERADA")

if __name__ == '__main__':
    unittest.main()