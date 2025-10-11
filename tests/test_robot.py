import unittest
import sys
import os
import pygame

# Añadimos la ruta principal del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from robot import Robot
from pathfinder import Pathfinder
from config import Config

class TestRobotLogic(unittest.TestCase):
    
    def setUp(self):
        """
        Esta función se ejecuta antes de cada prueba.
        Crea un robot y un entorno básico para las pruebas.
        """
        pygame.init()
        self.robot = Robot(0, Config.ALTURA_HUD)
        self.pathfinder = Pathfinder()
        self.rect_estacion = pygame.Rect(0, 0, 0, 0) # Simulado
        self.rect_canasta = pygame.Rect(0, 0, 0, 0) # Simulado
        self.pelotas = []

    def test_transicion_a_estado_cargar(self):
        """
        Prueba de Caja Negra: Si la batería es baja, ¿cambia el robot su estado a 'CARGAR'?
        """
        # Forzamos la condición: batería baja
        self.robot.carga = Config.CARGA_EMERGENCIA - 1
        
        # CORRECCIÓN FINAL: Añadimos 'paso_dev=True' para que la función no se detenga prematuramente.
        self.robot.actualizar(
            self.pelotas, 
            self.rect_estacion, 
            self.rect_canasta, 
            self.pathfinder,
            modo_desarrollador=True,
            paso_dev=True  # <-- ¡Esta es la línea clave!
        )
        
        # Verificamos el resultado: el estado debe ser 'CARGAR'
        self.assertEqual(self.robot.estado, 'CARGAR')
        print("\nPrueba de transición a CARGAR: SUPERADA")

    def test_ciclo_recoleccion_completo(self):
        """
        Prueba de Caja Negra: ¿El robot recoge una pelota y cambia su estado a 'RECOGIDO'?
        """
        # Condición inicial: una pelota justo en la posición del robot
        pelota_objetivo = (self.robot.rect.centerx, self.robot.rect.centery)
        self.pelotas.append(pelota_objetivo)
        self.robot.pelota_objetivo = pelota_objetivo
        self.robot.estado = 'BUSCANDO'
        self.robot.lleva_pelota = False
        
        # Ejecutamos el método que se llama al "llegar" a un destino
        self.robot._manejar_llegada(self.pelotas, self.rect_canasta, self.rect_estacion, self.pathfinder)

        # Verificamos los resultados
        self.assertTrue(self.robot.lleva_pelota, "El robot debería llevar la pelota")
        self.assertEqual(self.robot.estado, 'RECOGIDO', "El estado del robot debería ser RECOGIDO")
        self.assertEqual(len(self.pelotas), 0, "La pelota debería haber sido eliminada de la lista del mundo")
        print("Prueba de ciclo de recolección: SUPERADA")


if __name__ == '__main__':
    unittest.main()