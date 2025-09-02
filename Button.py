"""
Button

Description:
"""
import pygame, pygame.freetype, time

class Button:
    def __init__(self, rect, label, callback=None, border_color=(160,160,160)):
        if isinstance(rect, pygame.Rect):
            self.rect = rect
        else:
            self.rect = pygame.Rect(*rect)
        self.label = label
        self.callback = callback
        self.hovered = False
        self.pressed = False
        self.last_pressed_time = 0
        self.flash_duration = 0.03
        self.border_color = border_color

    def update_hover(self):
        mx, my = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mx, my)

    def draw(self, screen, font):
        base_bg = (239,239,239)
        shadow = (180, 180, 180)
        highlight = (229,229,229)
        text_color = (0, 0, 0)

        now = time.time()
        if self.pressed:
            bg = shadow
        elif now - self.last_pressed_time < self.flash_duration:
            bg = shadow
        elif self.hovered:
            bg = highlight
        else:
            bg = base_bg
        
        # Draw rectangle and border
        pygame.draw.rect(screen, bg, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 1)

        # Draw text
        text_rect = font.get_rect(self.label)
        text_x = self.rect.x + (self.rect.width - text_rect.width) // 2
        text_y = self.rect.y + (self.rect.height - text_rect.height) // 2

        old_color = getattr(font, "fgcolor", (0,0,0))
        font.fgcolor = text_color
        font.render_to(screen, (text_x, text_y), self.label)
        font.fgcolor = old_color

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed:
                self.last_pressed_time = time.time()
            self.pressed = False
