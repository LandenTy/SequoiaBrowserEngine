"""
main

Description: Simple DOM renderer with interactive elements
"""
import pygame, sys
from dom import parse_html, Node
from render import Button, draw_node
from config import current_page, SCREEN_WIDTH, SCREEN_HEIGHT, fonts

BG_COLOR = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

def load_page(file_path):
    try:
        with open(file_path, "r") as f:
            html_content = f.read()
        dom = parse_html(html_content)
        return dom
    except FileNotFoundError:
        root = Node("document")
        root.add_child(Node("p", text=f"Page not found: {file_path}"))
        return root

dom = load_page(current_page)

# --- Main loop ---
while running:
    dt = clock.tick(60) / 1000
    screen.fill(BG_COLOR)

    # Collect interactive elements during rendering
    interactive_elements = []
    draw_node(dom, 20, screen, fonts, interactive_elements)

    # --- Update elements ---
    for elem in interactive_elements:
        if hasattr(elem, "update_hover"):
            elem.update_hover()
        if hasattr(elem, "update"):
            elem.update(dt)

    # --- Event handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        for elem in interactive_elements:
            if hasattr(elem, "handle_event"):
                elem.handle_event(event)
            if hasattr(elem, "check_click") and event.type == pygame.MOUSEBUTTONDOWN:
                elem.check_click(event.pos)

    # --- Draw all interactive elements ---
    for elem in interactive_elements:
        if hasattr(elem, "draw"):
            elem.draw(screen, fonts.get("p", None))

    pygame.display.flip()

sys.exit()
