"""
PasswordInput

Description:
"""
import pygame
from Input import Input

class PasswordInput(Input):
    def __init__(self, rect, text="", mask="*"):
        super().__init__(rect, text)
        self.mask = mask

    def draw(self, screen, font):
        # Temporarily replace text with masked version
        original_text = self.text
        self.text = self.mask * len(self.text)
        super().draw(screen, font)
        self.text = original_text  # Restore actual text
