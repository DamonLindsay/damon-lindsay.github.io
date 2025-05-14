# core/unit.py

import pygame
from .settings import TILE_SIZE


class Unit:
    def __init__(self, name, hp, attack, movement, position):
        """
        name: string
        hp: int
        attack: int
        movement: int (tiles per turn)
        position: (grid_x, grid_y)
        """
        self.name = name
        self.hp = hp
        self.attack = attack
        self.movement = movement
        self.position = position
        self.selected = False

    def draw(self, surface):
        """
        Draws the unit as a circle centred in its tile.
        Blue = unselected; Yellow = selected.
        """
        grid_x, grid_y = self.position
        pixel_x = grid_x * TILE_SIZE + TILE_SIZE // 2
        pixel_y = grid_y * TILE_SIZE + TILE_SIZE // 2
        color = (0, 0, 255) if not self.selected else (255, 255, 0)
        radius = TILE_SIZE // 3
        pygame.draw.circle(surface, color, (pixel_x, pixel_y), radius)
