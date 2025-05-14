# core/unit.py

import os
import pygame
from .settings import TILE_SIZE, IMAGES_DIR

TEAM_COLORS = {
    "player": (0, 128, 255),  # Blue
    "enemy": (200, 50, 50),  # Red
}


class Unit:
    def __init__(self, name, hp, attack, movement, position, team="player", sprite_file=None):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.movement = movement
        self.position = position
        self.team = team
        self.selected = False

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
        grid_x, grid_y = self.position
        px = grid_x * TILE_SIZE + TILE_SIZE // 2
        py = grid_y * TILE_SIZE + TILE_SIZE // 2

        if self.sprite:
            rect = self.sprite.get_rect(center=(px, py))
            surface.blit(self.sprite, rect)
        else:
            base = TEAM_COLORS.get(self.team, (150, 150, 150))
            color = (255, 255, 0) if self.selected else base
            radius = TILE_SIZE // 3
            pygame.draw.circle(surface, color, (px, py), radius)
