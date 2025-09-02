"""
Table

Description:
Renders a basic HTML table using PyGame.
Supports caption, headers, and body rows.
Automatically calculates height based on content.
"""
import pygame

class Table:
    def __init__(self, rect, node, min_cell_height=30):
        """
        rect: pygame.Rect defining the table area
        node: DOM Node representing the <table> element
        min_cell_height: minimum height of a table row
        """
        if isinstance(rect, pygame.Rect):
            self.rect = rect
        else:
            self.rect = pygame.Rect(*rect)

        self.node = node
        self.font = None

        # Colors
        self.border_color = (0, 0, 0)
        self.header_color = (220, 220, 220)
        self.cell_color = (255, 255, 255)
        self.caption_color = (0, 0, 0)

        self.cell_padding = 5
        self.min_cell_height = min_cell_height

        # Parsed data
        self.caption = None
        self.headers = []
        self.rows = []

        self.parse_node()
        self.compute_dimensions()

    def parse_node(self):
        """Extract caption, headers, and row data from DOM node"""
        for child in self.node.children:
            if child.tag == "caption":
                self.caption = child.text
            elif child.tag == "thead":
                for tr in child.children:
                    if tr.tag == "tr":
                        row = [th.text for th in tr.children if th.tag == "th"]
                        if row:
                            self.headers.append(row)
            elif child.tag == "tbody" or child.tag == "tr":
                tr_nodes = [child] if child.tag == "tr" else [tr for tr in child.children if tr.tag == "tr"]
                for tr in tr_nodes:
                    row = [td.text for td in tr.children if td.tag == "td"]
                    if row:
                        self.rows.append(row)

    def compute_dimensions(self):
        """Compute total height and cell sizes based on rows/headers"""
        total_rows = len(self.rows) + (len(self.headers) if self.headers else 0)
        if self.caption:
            total_rows += 1

        self.cols = max([len(r) for r in self.rows] + [len(h) for h in self.headers] if self.headers or self.rows else [0])
        self.cell_width = self.rect.width // max(self.cols, 1)
        self.cell_height = max(self.min_cell_height, self.rect.height // max(total_rows, 1))

        # Update total height
        self.rect.height = self.cell_height * total_rows

    def draw(self, screen, font=None):
        if font:
            self.font = font
        if not self.font:
            raise ValueError("Font must be provided to draw table.")

        x0, y0 = self.rect.x, self.rect.y
        y_offset = y0

        # Draw caption
        if self.caption:
            caption_rect = pygame.Rect(x0, y_offset, self.rect.width, self.cell_height)
            self.font.render_to(screen, (caption_rect.x + self.cell_padding, caption_rect.y + self.cell_padding), self.caption)
            y_offset += self.cell_height

        # Draw headers
        for header_row in self.headers:
            for c, text in enumerate(header_row):
                cell_rect = pygame.Rect(x0 + c * self.cell_width, y_offset, self.cell_width, self.cell_height)
                pygame.draw.rect(screen, self.header_color, cell_rect)
                pygame.draw.rect(screen, self.border_color, cell_rect, 1)
                self.font.render_to(screen, (cell_rect.x + self.cell_padding, cell_rect.y + self.cell_padding), text)
            y_offset += self.cell_height

        # Draw body rows
        for row in self.rows:
            for c, text in enumerate(row):
                cell_rect = pygame.Rect(x0 + c * self.cell_width, y_offset, self.cell_width, self.cell_height)
                pygame.draw.rect(screen, self.cell_color, cell_rect)
                pygame.draw.rect(screen, self.border_color, cell_rect, 1)
                self.font.render_to(screen, (cell_rect.x + self.cell_padding, cell_rect.y + self.cell_padding), text)
            y_offset += self.cell_height

    @property
    def height(self):
        return self.rect.height

    @property
    def width(self):
        return self.rect.width
