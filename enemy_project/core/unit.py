# core/unit.py

import os
import pygame
from .settings import TILE_SIZE, IMAGES_DIR


class Unit:
    def __init__(self, name, hp, attack, movement, position, sprite_file=None):
        """
        name:        string
        hp:          int
        attack:      int
        movement:    int (tiles per turn)
        position:    (grid_x, grid_y)
        sprite_file: filename in assets/images (e.g. "space_marine.png")
        """
        self.name = name
        self.hp = hp
        self.attack = attack
        self.movement = movement
        self.position = position
        self.selected = False

        # Try loading sprite if provided
        if sprite_file:
            path = os.path.join(IMAGES_DIR, sprite_file)
            try:
                img = pygame.image.load(path).convert_alpha()
                self.sprite = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            except pygame.error:
                print(f"Warning: could not load sprite at {path}")
                self.sprite = None
        else:
            self.sprite = None

    def draw(self, surface):
        """
        Draws the unit. If sprite exists, blit it;
        otherwise draw a colored circle.
        """
        grid_x, grid_y = self.position
        px = grid_x * TILE_SIZE + TILE_SIZE // 2
        py = grid_y * TILE_SIZE + TILE_SIZE // 2

        if self.sprite:
            # Center the sprite
            rect = self.sprite.get_rect(center=(px, py))
            surface.blit(self.sprite, rect)
        else:
            # Fallback: circle
            color = (0, 0, 255) if not self.selected else (255, 255, 0)
            radius = TILE_SIZE // 3
            pygame.draw.circle(surface, color, (px, py), radius)
