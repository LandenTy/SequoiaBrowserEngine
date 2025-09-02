"""
ColorInput

Description: Simple colour picker widget that lets you drag a cursor
to select a color of RGB. You can also adjust the saturation and hue
of the colour by dragging the bottom slider. You can set the color
picker to an exact colour by typing the RGB colour code into the input
boxes.
"""
import pygame, pygame.freetype, colorsys
from Input import Input

class ColorPicker:
    def __init__(self, rect: pygame.Rect):
        # Position and size
        self.PICKER_X, self.PICKER_Y = rect.x, rect.y
        self.PICKER_SIZE = rect.width  # assume square picker
        self.SLIDER_X, self.SLIDER_Y = self.PICKER_X, self.PICKER_Y + self.PICKER_SIZE + 20
        self.SLIDER_W, self.SLIDER_H = self.PICKER_SIZE, 20
        self.PREVIEW_X, self.PREVIEW_Y = self.PICKER_X + self.PICKER_SIZE + 30, self.PICKER_Y
        self.RGB_X, self.RGB_Y = self.PREVIEW_X, self.PREVIEW_Y + 100

        # Color state
        self.current_hue = 0.0
        self.selected_color = [255, 0, 0]
        self.selected_pos = (self.PICKER_X, self.PICKER_Y)

        # Surfaces
        self.picker_surface = pygame.Surface((self.PICKER_SIZE, self.PICKER_SIZE))
        self.slider_surface = pygame.Surface((self.SLIDER_W, self.SLIDER_H))
        self.font = pygame.freetype.SysFont("Arial", 20)
        self.last_hue = -1

        # Input boxes for RGB
        self.input_boxes = [Input(pygame.Rect(self.RGB_X, self.RGB_Y + i*40, 80, 30), str(c))
                            for i, c in enumerate(self.selected_color)]

        # Drag flags
        self.dragging_picker = False
        self.dragging_slider = False

        # Initial render
        self.render_picker(self.current_hue)
        self.render_slider()
        self.update_inputs_from_color()

    # --- Core functions ---
    def render_picker(self, hue):
        if hue == self.last_hue:
            return
        self.last_hue = hue
        block = 1  # 1x1 pixel blocks
        for y in range(self.PICKER_SIZE):
            v = 1 - y / self.PICKER_SIZE
            for x in range(self.PICKER_SIZE):
                s = x / self.PICKER_SIZE
                r, g, b = colorsys.hsv_to_rgb(hue, s, v)
                pygame.draw.rect(self.picker_surface, (int(r*255), int(g*255), int(b*255)),
                                 pygame.Rect(x, y, block, block))

    def render_slider(self):
        for x in range(self.SLIDER_W):
            h = x / self.SLIDER_W
            r, g, b = colorsys.hsv_to_rgb(h, 1, 1)
            pygame.draw.line(self.slider_surface, (int(r*255), int(g*255), int(b*255)), (x,0),(x,self.SLIDER_H))

    def update_inputs_from_color(self):
        for i, box in enumerate(self.input_boxes):
            box.text = str(self.selected_color[i])
            box.cursor_pos = len(box.text)

    def update_color_from_picker(self, mx, my):
        sx = min(max(mx - self.PICKER_X, 0), self.PICKER_SIZE) / self.PICKER_SIZE
        sy = min(max(my - self.PICKER_Y, 0), self.PICKER_SIZE) / self.PICKER_SIZE
        r, g, b = colorsys.hsv_to_rgb(self.current_hue, sx, 1 - sy)
        self.selected_color = [int(r*255), int(g*255), int(b*255)]
        self.selected_pos = (self.PICKER_X + int(sx*self.PICKER_SIZE), self.PICKER_Y + int(sy*self.PICKER_SIZE))

    def update_cursor_from_inputs(self):
        r, g, b = [c/255 for c in self.selected_color]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        self.current_hue = h
        self.render_picker(self.current_hue)
        self.selected_pos = (self.PICKER_X + int(s*self.PICKER_SIZE), self.PICKER_Y + int((1-v)*self.PICKER_SIZE))

    # --- Public draw method ---
    def draw(self, screen, font=None):
        if font:
            self.font = font
        screen.blit(self.picker_surface, (self.PICKER_X, self.PICKER_Y))
        pygame.draw.circle(screen, (0,0,0), self.selected_pos, 5, 2)
        screen.blit(self.slider_surface, (self.SLIDER_X, self.SLIDER_Y))
        slider_pos = int(self.SLIDER_X + self.current_hue*self.SLIDER_W)
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(slider_pos-2, self.SLIDER_Y, 4, self.SLIDER_H), 2)
        pygame.draw.rect(screen, tuple(self.selected_color), pygame.Rect(self.PREVIEW_X, self.PREVIEW_Y, 60, 60))
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(self.PREVIEW_X, self.PREVIEW_Y, 60, 60), 2)
        for box in self.input_boxes:
            box.draw(screen, self.font)

    # --- Event handling ---
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.PICKER_X <= mx < self.PICKER_X+self.PICKER_SIZE and self.PICKER_Y <= my < self.PICKER_Y+self.PICKER_SIZE:
                self.dragging_picker = True
                self.update_color_from_picker(mx,my)
            elif self.SLIDER_X <= mx < self.SLIDER_X+self.SLIDER_W and self.SLIDER_Y <= my < self.SLIDER_Y+self.SLIDER_H:
                self.dragging_slider = True
                self.current_hue = (mx - self.SLIDER_X)/self.SLIDER_W
                self.render_picker(self.current_hue)
                self.update_color_from_picker(*self.selected_pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_picker = self.dragging_slider = False
        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            if self.dragging_picker:
                self.update_color_from_picker(mx,my)
            elif self.dragging_slider:
                self.current_hue = (mx - self.SLIDER_X)/self.SLIDER_W
                self.render_picker(self.current_hue)
                self.update_color_from_picker(*self.selected_pos)

        for box in self.input_boxes:
            box.handle_event(event)

    # --- Update ---
    def update(self, dt):
        for box in self.input_boxes:
            box.update(dt)
        if any(box.focused for box in self.input_boxes):
            try:
                self.selected_color = [max(0,min(255,int(box.text))) for box in self.input_boxes]
                self.update_cursor_from_inputs()
            except ValueError:
                pass
        self.update_inputs_from_color()
