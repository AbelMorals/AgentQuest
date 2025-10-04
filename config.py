import pygame
# ==============================================================================
# CLASE 1: Configuración (Config)
# Responsabilidad: Almacenar todas las constantes y parámetros del juego.
# Facilita cambiar la configuración sin tener que buscar en todo el código.
# ==============================================================================
pygame.init()
info_display = pygame.display.Info()
SCREEN_ANCHO, SCREEN_ALTO = info_display.current_w, info_display.current_h
pygame.quit()

class Config:
    TAMANO_CELDA = 30
    ALTURA_HUD = 60
    ANCHO = (SCREEN_ANCHO // TAMANO_CELDA) * TAMANO_CELDA
    ALTO = (SCREEN_ALTO // TAMANO_CELDA) * TAMANO_CELDA
    #ANCHO, ALTO = 810, 600 + ALTURA_HUD

    # Colores y Fuentes
    NEGRO = (0, 0, 0); BLANCO = (220, 220, 220); VERDE = (0, 200, 0)
    VERDE_OSCURO = (0, 100, 0); ROJO = (200, 0, 0); AZUL = (0, 120, 255)
    FONDO = (30, 30, 50); AMARILLO = (255, 220, 0); NARANJA = (255, 150, 0)
    COLOR_CAMINO = (80, 80, 100); CAFE = (139, 69, 19)
    
    # Parámetros del Robot
    VELOCIDAD_ANIMACION_ROBOT = 6
    enfriamiento_decision_robot = 500 #en ms
    CARGA_MAXIMA = 500; CARGA_EMERGENCIA = 150; CARGA_POR_MOVIMIENTO = 1.5
    TASA_RECARGA = CARGA_MAXIMA / 30 
    MARGEN_SEGURIDAD_BATERIA = 1.25
    MAX_TURNOS_ATASCADO = 1
    
    # Parámetros del Mundo
    NUM_PELOTAS = 10
    NUM_OBSTACULOS = 30
    TAMANO_ESTACION = TAMANO_CELDA * 1; TAMANO_CANASTA = TAMANO_CELDA * 1