"""
input

Description:
"""
import pygame, pygame.freetype

class Input:
    def __init__(self, rect, text=""):
        if isinstance(rect, pygame.Rect):
            self.rect = rect
        else:
            self.rect = pygame.Rect(*rect)
        
        self.text = text
        self.cursor_pos = len(text)
        self.focused = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 0.5

        # Backspace repeat
        self.backspace_held = False
        self.backspace_timer = 0
        self.backspace_initial_delay = 0.5
        self.backspace_repeat_delay = 0.05

        # Arrow keys repeat
        self.left_held = False
        self.right_held = False
        self.arrow_timer = 0
        self.arrow_initial_delay = 0.3
        self.arrow_repeat_delay = 0.05

        # Selection
        self.selection_start = None
        self.selection_end = None

        # Shift tracking
        self.shift_held = False

    def update(self, dt):
        # Cursor blink
        self.cursor_timer += dt
        if self.cursor_timer > self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        # Backspace repeat
        if self.backspace_held:
            self.backspace_timer += dt
            if self.backspace_timer >= self.backspace_repeat_delay:
                if self.selection_start is not None:
                    self.text = self.text[:self.selection_start] + self.text[self.selection_end:]
                    self.cursor_pos = self.selection_start
                    self.selection_start = self.selection_end = None
                elif self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                self.backspace_timer = 0

        # Arrow key repeat
        if self.left_held or self.right_held:
            self.arrow_timer += dt
            if self.arrow_timer >= self.arrow_repeat_delay:
                if self.left_held and self.cursor_pos > 0:
                    self.cursor_pos -= 1
                if self.right_held and self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
                self.arrow_timer = 0

    def handle_event(self, event):
        mods = pygame.key.get_mods()
        ctrl_held = mods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.focused = self.rect.collidepoint(event.pos)

        elif event.type == pygame.KEYDOWN and self.focused:
            # Track shift
            if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.shift_held = True

            # Backspace
            elif event.key == pygame.K_BACKSPACE:
                if self.selection_start is not None:
                    self.text = self.text[:self.selection_start] + self.text[self.selection_end:]
                    self.cursor_pos = self.selection_start
                    self.selection_start = self.selection_end = None
                elif self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                self.backspace_held = True
                self.backspace_timer = -self.backspace_initial_delay

            # Arrow keys
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                self.selection_start = self.selection_end = None
                self.left_held = True
                self.arrow_timer = -self.arrow_initial_delay

            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
                self.selection_start = self.selection_end = None
                self.right_held = True
                self.arrow_timer = -self.arrow_initial_delay

            elif event.key == pygame.K_UP:
                self.cursor_pos = 0
                self.selection_start = self.selection_end = None

            elif event.key == pygame.K_DOWN:
                self.cursor_pos = len(self.text)
                self.selection_start = self.selection_end = None

            # Ctrl+A select all
            elif event.key == pygame.K_a and ctrl_held:
                self.selection_start = 0
                self.selection_end = len(self.text)
                self.cursor_pos = self.selection_end

            # Typing letters/symbols (Shift handled automatically via event.unicode)
            elif event.unicode and event.key != pygame.K_RETURN:
                char = event.unicode
            
                # --- Handle shift manually if pygame didn't give uppercase/symbol ---
                if self.shift_held:
                    if char.isalpha():
                        char = char.upper()
                    else:
                        shift_map = {
                            "1": "!", "2": "@", "3": "#", "4": "$",
                            "5": "%", "6": "^", "7": "&", "8": "*",
                            "9": "(", "0": ")", "-": "_", "=": "+",
                            "[": "{", "]": "}", "\\": "|",
                            ";": ":", "'": "\"",
                            ",": "<", ".": ">", "/": "?"
                        }
                        if char in shift_map:
                            char = shift_map[char]
            
                # --- Insert text ---
                if self.selection_start is not None:
                    self.text = (
                        self.text[:self.selection_start] +
                        char +
                        self.text[self.selection_end:]
                    )
                    self.cursor_pos = self.selection_start + len(char)
                    self.selection_start = self.selection_end = None
                else:
                    self.text = (
                        self.text[:self.cursor_pos] +
                        char +
                        self.text[self.cursor_pos:]
                    )
                    self.cursor_pos += len(char)
        
        # Special Keys
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE:
                self.backspace_held = False
                self.backspace_timer = 0
            elif event.key == pygame.K_LEFT:
                self.left_held = False
                self.arrow_timer = 0
            elif event.key == pygame.K_RIGHT:
                self.right_held = False
                self.arrow_timer = 0
            elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.shift_held = False

    def update_hover(self):
        pass

    def draw(self, screen, font):
        # Draw input box
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        padding = 5
        max_width = self.rect.width - 2 * padding

        # Cursor position in pixels
        cursor_px = font.get_rect(self.text[:self.cursor_pos]).width

        # Horizontal scroll
        scroll_x = 0
        text_width = font.get_rect(self.text).width
        if text_width > max_width:
            if cursor_px > max_width:
                scroll_x = cursor_px - max_width
            elif cursor_px < scroll_x:
                scroll_x = cursor_px

        # Draw selection
        if self.selection_start is not None:
            sel_start_px = font.get_rect(self.text[:self.selection_start]).width
            sel_end_px = font.get_rect(self.text[:self.selection_end]).width
            sel_rect = pygame.Rect(
                self.rect.x + padding - scroll_x + sel_start_px,
                self.rect.y + padding,
                sel_end_px - sel_start_px,
                font.get_sized_height()
            )
            pygame.draw.rect(screen, (173, 216, 230), sel_rect)

        # Draw visible text
        visible_text = ""
        x_offset = 0
        for i, char in enumerate(self.text):
            char_width = font.get_rect(char).width
            char_start = x_offset
            char_end = x_offset + char_width
            if char_end > scroll_x and char_start - scroll_x < max_width:
                visible_text = self.text[i:]
                break
            x_offset += char_width

        # Trim right side
        trimmed_text = ""
        current_width = font.get_rect("").width
        right_limit = scroll_x + max_width
        for c in visible_text:
            w = font.get_rect(c).width
            if current_width + x_offset + w <= right_limit:
                trimmed_text += c
                current_width += w
            else:
                break

        text_x = self.rect.x + padding - scroll_x + x_offset
        text_y = self.rect.y + padding
        old_color = getattr(font, "fgcolor", (0, 0, 0))
        font.fgcolor = (0, 0, 0)
        font.render_to(screen, (text_x, text_y), trimmed_text)
        font.fgcolor = old_color

        # --- Draw cursor ---
        if self.focused and self.cursor_visible:
            cursor_px = font.get_rect(self.text[:self.cursor_pos]).width
            cursor_x = self.rect.x + padding + (cursor_px - scroll_x)
            font_height = font.get_sized_height()
            cursor_y = self.rect.y + (self.rect.height - font_height) // 2

            if cursor_x < self.rect.x + padding:
                cursor_x = self.rect.x + padding
            elif cursor_x > self.rect.right - padding:
                cursor_x = self.rect.right - padding

            pygame.draw.line(
                screen, (0, 0, 0),
                (cursor_x, cursor_y),
                (cursor_x, cursor_y + font_height),
                2
            )
# --------------- TEXT WRAPPING ----------------
def wrap_text(text, max_width_chars):
    words = text.split(" ")
    lines, current_line = [], ""
    for word in words:
        if len(current_line + " " + word) <= max_width_chars:
            current_line = (current_line + " " + word).strip() if current_line else word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

# ---------------- DRAW NODE ----------------
def wrap_text_pixel(text, font, max_width_px):
    words = text.split(" ")
    lines, current_line = [], ""
    for word in words:
        test_line = f"{current_line} {word}".strip() if current_line else word
        width = font.get_rect(test_line).width
        if width <= max_width_px:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines
