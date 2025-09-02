"""
RadioButton

Description:
"""
import pygame, time
from Button import Button

class RadioButton(Button):
    groups = {}  # class-level dict to track groups

    def __init__(self, rect, label, group=None, selected=False, border_color=(160,160,160)):
        super().__init__(rect, label, callback=None, border_color=border_color)
        self.selected = selected
        self.group = group
        if group:
            if group not in RadioButton.groups:
                RadioButton.groups[group] = []
            RadioButton.groups[group].append(self)

    def draw(self, screen, font):
        # Draw circle
        cx = self.rect.x + self.rect.height // 2
        cy = self.rect.y + self.rect.height // 2
        radius = self.rect.height // 2 - 2

        pygame.draw.circle(screen, (255, 255, 255), (cx, cy), radius)
        pygame.draw.circle(screen, self.border_color, (cx, cy), radius, 1)

        # Draw inner filled circle if selected
        if self.selected:
            pygame.draw.circle(screen, (50, 50, 50), (cx, cy), radius//2)

        # Draw label
        text_rect = font.get_rect(self.label)
        text_x = self.rect.x + self.rect.height + 5
        text_y = self.rect.y + (self.rect.height - text_rect.height) // 2

        old_color = getattr(font, "fgcolor", (0,0,0))
        font.fgcolor = (0,0,0)
        font.render_to(screen, (text_x, text_y), self.label)
        font.fgcolor = old_color

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            if self.rect.collidepoint(mx, my):
                self.select()

    def select(self):
        # Deselect other buttons in the same group
        if self.group:
            for btn in RadioButton.groups[self.group]:
                btn.selected = False
        self.selected = True
