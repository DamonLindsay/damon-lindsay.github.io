# ui/battle_ui.py

import pygame


class BattleUI:
    """
    Encapsulate all battlefield‐specific drawing: grid, highlights,
    stats panel, etc. Pull the code out of states.py into clean methods here.
    """

    @staticmethod
    def draw_grid(surface, GRID_WIDTH, GRID_HEIGHT, TILE_SIZE):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surface, (50, 50, 50), rect, 1)

    @staticmethod
    def draw_stats_panel(surface, state):
        # stub: copy your stats‐panel code here, using state.hover_tile
        # and state.units. This keeps your draw() in states.py tidy.
        pass
