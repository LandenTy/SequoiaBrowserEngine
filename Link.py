"""
Link

Description:
Represents a clickable hyperlink in the DOM tree.
For this browser, <a href="..."> always points to a local file.
When clicked, the file is opened and its contents can be re-rendered.
"""
import pygame
pygame.init()

class Link:
    def __init__(self, rect, text, href="", callback=None):
        # rect can be tuple or pygame.Rect
        self.rect = pygame.Rect(*rect) if not isinstance(rect, pygame.Rect) else rect
        self.text = text
        self.href = href.strip()
        self.callback = callback or self.open_file  # default to open file

    def draw(self, screen, font):
        """Draws the link text in blue and underlined."""
        font.fgcolor = (0, 0, 255)
        font.render_to(screen, (self.rect.x, self.rect.y), self.text)

        # underline
        text_rect = font.get_rect(self.text)
        underline_y = self.rect.y + text_rect.height - 2
        pygame.draw.line(
            screen,
            (0, 0, 255),
            (self.rect.x, underline_y),
            (self.rect.x + text_rect.width, underline_y),
            1
        )

    def check_click(self, mouse_pos):
        """If the link is clicked, trigger its callback."""
        if self.rect.collidepoint(mouse_pos):
            print(f"Clicked link: '{self.text}' -> {self.href}")
            self.callback()

    def open_file(self):
        """Default behavior: open the file this link points to."""
        if not self.href:
            print("[ERROR] No href set for this link")
            return

        try:
            with open(self.href, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"[DEBUG] Successfully opened file: {self.href}")
            # TODO: parse_html(content) and redraw the screen
        except FileNotFoundError:
            print(f"[ERROR] File not found: {self.href}")
        except Exception as e:
            print(f"[ERROR] Could not open '{self.href}': {e}")
