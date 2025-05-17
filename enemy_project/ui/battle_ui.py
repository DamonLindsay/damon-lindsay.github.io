# ui/battle_ui.py

import pygame
from enemy_project.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, \
    STAT_PANEL_WIDTH
from enemy_project.core.settings import TILE_SIZE, GRID_WIDTH, GRID_HEIGHT


class BattleUI:
    """
    Encapsulate battlefield drawing: grid and stats panel.
    """

    @staticmethod
    def draw_grid(surface, camera_x=0, camera_y=0):
        """
        Draws the battlefield grid lines offset by the camera.
        """
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    x * TILE_SIZE - camera_x,
                    y * TILE_SIZE - camera_y,
                    TILE_SIZE,
                    TILE_SIZE
                )
                pygame.draw.rect(surface, (50, 50, 50), rect, 1)

    @staticmethod
    def draw_stats_panel(surface, state):
        """
        Draws the right‐hand stats sidebar: background, unit portrait, and stats.
        Chooses hover > selected unit to display.
        """
        panel_x = SCREEN_WIDTH - STAT_PANEL_WIDTH
        padding = 10

        # Panel background & divider
        pygame.draw.rect(surface, (20, 20, 20),
                         (panel_x, 0, STAT_PANEL_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(surface, (100, 100, 100),
                         (panel_x, 0), (panel_x, SCREEN_HEIGHT), 2)

        # Determine which unit to show: hover first, then selected
        hover_u = None
        if state.hover_tile:
            hover_u = next(
                (u for u in state.units if u.position == state.hover_tile),
                None
            )
        sel_u = next((u for u in state.units if u.selected), None)
        u = hover_u or sel_u

        font_name = pygame.font.Font(None, 32)
        font_stat = pygame.font.Font(None, 24)

        if u:
            # 1) Unit Name
            name_lbl = font_name.render(u.name, True, (255, 255, 255))
            name_rect = name_lbl.get_rect(center=(
                panel_x + STAT_PANEL_WIDTH // 2,
                padding + name_lbl.get_height() // 2
            ))
            surface.blit(name_lbl, name_rect)

            # 2) Portrait Slot
            portrait_size = STAT_PANEL_WIDTH - padding * 2
            portrait_rect = pygame.Rect(
                panel_x + padding,
                name_rect.bottom + padding,
                portrait_size,
                portrait_size
            )
            pygame.draw.rect(surface, (40, 40, 40), portrait_rect)
            if u.sprite:
                sprite_scaled = pygame.transform.scale(
                    u.sprite,
                    (portrait_size, portrait_size)
                )
                surface.blit(sprite_scaled, portrait_rect.topleft)

            # 3) Full Stat Lines
            stats = [
                ("Weapon Skill", f"{u.ws}+"),
                ("Ballistic Skill", f"{u.bs}+"),
                ("Strength", str(u.strength)),
                ("Toughness", str(u.toughness)),
                ("Wounds", f"{u.current_wounds}/{u.max_wounds}"),
                ("Attacks", str(u.attacks)),
                ("Leadership", str(u.leadership)),
                ("Save", f"{u.save}+"),
            ]
            lines = [f"{lab}: {val}" for lab, val in stats]

            # Dynamic vertical spacing
            start_y = portrait_rect.bottom + padding
            leftover = SCREEN_HEIGHT - start_y - padding
            spacing = leftover // (len(lines) + 1)
            y = start_y + spacing
            for line in lines:
                lbl = font_stat.render(line, True, (200, 200, 200))
                surface.blit(lbl, (panel_x + padding, y))
                y += spacing

        else:
            # No unit to display
            msg_lbl = font_name.render("No unit selected", True, (200, 200, 200))
            surface.blit(msg_lbl, (panel_x + padding, SCREEN_HEIGHT // 2))
