import pygame
import os
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
    SCREEN_ANCHO = SCREEN_ANCHO
    SCREEN_ALTO = SCREEN_ALTO
    ANCHO = (SCREEN_ANCHO // TAMANO_CELDA) * TAMANO_CELDA
    ALTO = (SCREEN_ALTO // TAMANO_CELDA) * TAMANO_CELDA
    
    # --- Configuración de Imagen de Fondo ---
    IMAGEN_FONDO_MENU_SELECCION = "wwa.jpg"
    
    # --- Configuración de Audio General ---
    MUSICA_MENU = "menu-music.mp3" # Asume que está en Sonidos/Comunes
    
    TEMAS = {
        "PC": {
            "titulo": "Paradise Circus",
            "carpeta": "CircoAssets",
            "robot": "payaso.png",
            "pelota": "pelota.png",
            "estacion": "cama.png",
            "canasta": "canasta.png",
            "fondo": "cesped.png",
            "musica_fondo": "circus-music.mp3", # NUEVO: Música del tema
            "obstaculos": {
                (1, 1): ["arofuego.png", "arofuego2.png", "globos32.png", "paja.png"],
                (2, 2): ["leon.png", "puesto.png", "puesto2.png", "puesto3.png", "puesto4.png"],
                (2, 3): ["cañon.png", "Fuerza.png", "globos64.png"],
                (3, 2): ["carro.png"],
                (4, 4): ["carpa.png"],
                (10, 1): ["ilera.png", "ilera2.png"],
                (1, 10): ["ilera3.png"]
            }
        },
        "KA": {
            "titulo": "Knight's Adventure",
            "carpeta": "CaballeroAssets",
            "robot": "caballero.png",
            "pelota": "monedas.png",
            "estacion": "cama.png",
            "canasta": "cofre.png",
            "fondo": "cesped.png",
            "musica_fondo": "medieval-music.mp3", # NUEVO: Música del tema
            "obstaculos": {
                (1, 1): ["aramadura.png", "escudo.png"],
                (2, 2): ["roca.png", "casa2.png"],
                (2, 3): ["leña.png","pino.png"],
                (3, 2): ["casa.png","casa1.png"],
                (4, 4): ["roca.png"],
                (10, 1): ["cerco.png"],
                (1, 10): ["cercaV.png"]
            }
        },
        "CS": {
            "titulo": "Cuauhcalli, The Temple of the Sun",
            "carpeta": "GuerreroAssets",
            "robot": "guerrero.png",
            "pelota": "totem.png",
            "estacion": "casa.png",
            "canasta": "cofre.png",
            "fondo": "cesped.png",
            "musica_fondo": "azteca-music.mp3", # NUEVO: Música del tema
            "obstaculos": {
                (1, 1): ["arco.png", "escudo.png", "jarra.png"],
                (2, 2): ["pared.png", "estatua1.png", "estatua3.png", "estatua4.png"],
                (2, 3): ["enemigo.png", "palmera.png"],
                (3, 2): ["estatua2.png"],
                (4, 4): ["piramide.png"],
                (10, 1): ["rio.png","sembradio.png"],
                (1, 10): ["rioVertical.png"]
            }
        }
    }

    POS_X_CENTRADA = (SCREEN_ANCHO - ANCHO) // 2
    POS_Y_CENTRADA = (SCREEN_ALTO - ALTO) // 2
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{POS_X_CENTRADA},{POS_Y_CENTRADA}"

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