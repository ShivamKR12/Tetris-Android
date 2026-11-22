from random import choice, randrange
import pygame
from settings import WIDTH, FIGURES_POS

class Tetromino:
    """Handles the creation, movement, and rotation of the falling piece."""
    def __init__(self):
        self.shape_pos = choice(FIGURES_POS)
        self.blocks = [pygame.Rect(x + WIDTH // 2, y + 1, 1, 1) for x, y in self.shape_pos]
        self.color = (randrange(30, 256), randrange(30, 256), randrange(30, 256))

    def move(self, dx, dy):
        for block in self.blocks:
            block.x += dx
            block.y += dy

    def rotate(self):
        center = self.blocks[0]
        for block in self.blocks:
            x = block.y - center.y
            y = block.x - center.x
            block.x = center.x - x
            block.y = center.y + y
