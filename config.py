"""
config

Description:
"""
import pygame, pygame.freetype
pygame.init()

# === USERDEF ===

current_page = "tables.txt" # Change this to update what page is being viewed by default

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 1110
LINE_HEIGHTS = {"h1": 50, "p": 30, "button": 40}
CHAR_WIDTH = 12
LEFT_MARGIN = 20

fonts = {
    "h1": pygame.freetype.SysFont("Arial", 32),
    "h2": pygame.freetype.SysFont("Arial", 24),
    "h3": pygame.freetype.SysFont("Arial", 19),
    "h4": pygame.freetype.SysFont("Arial", 16),
    "h5": pygame.freetype.SysFont("Arial", 13),
    "h6": pygame.freetype.SysFont("Arial", 11),
    "p": pygame.freetype.SysFont("Arial", 16),
    "a": pygame.freetype.SysFont("Arial", 16),
    "button": pygame.freetype.SysFont("Arial", 14)
}
# ===================
