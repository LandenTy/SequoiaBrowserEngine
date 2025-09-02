"""
Slider

Description:
"""
import pygame

class Slider:
    def __init__(self, rect, min_val=0, max_val=100, value=0):
        if isinstance(rect, pygame.Rect):
            self.rect = rect
        else:
            self.rect = pygame.Rect(*rect)

        self.min_val = min_val
        self.max_val = max_val
        self.value = max(min_val, min(max_val, value))

        self.track_height = 6
        self.handle_radius = 10
        self.dragging = False
        self.update_handle_pos()

    def update_handle_pos(self):
        fraction = (self.value - self.min_val) / (self.max_val - self.min_val)
        self.handle_x = self.rect.x + int(fraction * self.rect.width)
        self.handle_y = self.rect.y + self.rect.height // 2

    def draw(self, screen, font=None):
        # Always redraw the track background
        track_rect = pygame.Rect(
            self.rect.x, 
            self.rect.y + self.rect.height//2 - self.track_height//2, 
            self.rect.width, 
            self.track_height
        )
        pygame.draw.rect(screen, (200, 200, 200), track_rect)  # Track
    
        # Draw the filled portion
        fill_rect = pygame.Rect(
            self.rect.x, 
            track_rect.y, 
            self.handle_x - self.rect.x, 
            self.track_height
        )
        pygame.draw.rect(screen, (100, 149, 237), fill_rect)  # Fill
    
        # Draw the handle (topmost)
        pygame.draw.circle(screen, (50, 50, 50), (self.handle_x, self.handle_y), self.handle_radius)
        pygame.draw.circle(screen, (230, 230, 230), (self.handle_x, self.handle_y), self.handle_radius-3)

    def handle_event(self, event):
        mx, my = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if (mx - self.handle_x)**2 + (my - self.handle_y)**2 <= self.handle_radius**2:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.handle_x = max(self.rect.x, min(mx, self.rect.x + self.rect.width))
            fraction = (self.handle_x - self.rect.x) / self.rect.width
            self.value = self.min_val + fraction * (self.max_val - self.min_val)
