"""
NumberInput

Description:
"""
from Input import Input
import pygame
pygame.init()

class NumberInput(Input):
    def handle_event(self, event):
        mods = pygame.key.get_mods()
        ctrl_held = mods & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL)

        # Always allow Ctrl+A (select all)
        if event.type == pygame.KEYDOWN and ctrl_held and event.key == pygame.K_a:
            super().handle_event(event)
            return

        # Allow only digits and navigation/backspace keys
        if event.type == pygame.KEYDOWN and self.focused:
            if event.unicode.isdigit() or event.key in (
                pygame.K_BACKSPACE, pygame.K_LEFT, pygame.K_RIGHT,
                pygame.K_UP, pygame.K_DOWN
            ):
                super().handle_event(event)
        else:
            super().handle_event(event)
