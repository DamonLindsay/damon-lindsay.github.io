# core/unit.py

import os
import pygame
from .settings import TILE_SIZE, IMAGES_DIR
from .combat import to_hit_roll, wound_roll, saving_throw

# Team color mapping
TEAM_COLORS = {
    "player": (0, 128, 255),
    "enemy": (200, 50, 50),
}


class Unit:
    def __init__(
            self,
            name,
            ws, bs,
            strength, toughness,
            wounds, attacks,
            movement,
            leadership, save,
            position,
            attack_range=1,
            team="player",
            sprite_file=None,
            abilities=None
    ):
        """
        name:        string
        ws:          Weapon Skill (to-hit in melee)
        bs:          Ballistic Skill (to-hit in shooting)
        strength:    Strength
        toughness:   Toughness
        wounds:      Wounds (number of wounds before removal)
        attacks:     Number of attacks in melee
        movement:    Movement allowance (tiles per turn)
        leadership:  Leadership (morale tests)
        save:        Armor Save (e.g. 3 means 3+ to save)
        position:    (grid_x, grid_y)
        attack_range:tiles for combat range
        team:        "player" or "enemy"
        sprite_file: optional sprite filename in assets/images
        abilities:   list of special rules (strings)
        """
        self.name = name
        self.ws = ws
        self.bs = bs
        self.strength = strength
        self.toughness = toughness
        self.max_wounds = wounds
        self.current_wounds = wounds
        self.attacks = attacks
        self.movement = movement
        self.leadership = leadership
        self.save = save
        self.position = position
        self.attack_range = attack_range
        self.team = team
        self.selected = False
        self.abilities = abilities or []

        # per‐turn flags
        self.has_moved = False
        self.has_attacked = False

        # load sprite if provided
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

    def draw(self, surface, camera_x=0, camera_y=0):
        """
        Draw sprite or circle at world position minus camera offset.
        """
        world_x = self.position[0] * TILE_SIZE
        world_y = self.position[1] * TILE_SIZE
        px = world_x - camera_x + TILE_SIZE // 2
        py = world_y - camera_y + TILE_SIZE // 2

        if self.sprite:
            rect = self.sprite.get_rect(center=(px, py))
            surface.blit(self.sprite, rect)
        else:
            base_color = TEAM_COLORS.get(self.team, (150, 150, 150))
            color = (255, 255, 0) if self.selected else base_color
            radius = TILE_SIZE // 3
            pygame.draw.circle(surface, color, (px, py), radius)

    def is_alive(self):
        return self.current_wounds > 0

    def attack(self, target):
        total_unsaved = 0
        for _ in range(self.attacks):
            if not to_hit_roll(self.ws):          continue
            if not wound_roll(self.strength, target.toughness): continue
            if saving_throw(target.save):         continue
            total_unsaved += 1

        target.current_wounds -= total_unsaved
        self.has_attacked = True
        print(f"{self.name} hits!: unsaved wounds = {total_unsaved}")
