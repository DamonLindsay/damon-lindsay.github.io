# core/states.py

import pygame
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, STAT_PANEL_WIDTH
from .unit import Unit


class State:
    """Base class for all game states."""

    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class MainMenu(State):
    """Main menu with two options: Start PvE, Quit."""

    def __init__(self, game):
        super().__init__(game)
        self.options = ["Start PvE", "Quit"]
        self.selected = 0
        self.font = pygame.font.Font(None, 48)

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif e.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif e.key == pygame.K_RETURN:
                    choice = self.options[self.selected]
                    if choice == "Start PvE":
                        from .states import PvESetup
                        self.game.state = PvESetup(self.game)
                    else:
                        self.game.running = False

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((0, 0, 0))
        for idx, text in enumerate(self.options):
            color = (255, 255, 255) if idx == self.selected else (100, 100, 100)
            label = self.font.render(text, True, color)
            rect = label.get_rect(center=(
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + idx * 60
            ))
            surface.blit(label, rect)


class PvESetup(State):
    """PvE setup: pick mission, your army, enemy faction, and difficulty."""

    def __init__(self, game):
        super().__init__(game)
        self.fields = ["Mission", "Your Army", "Enemy Faction", "Difficulty"]
        self.options = {
            "Mission": ["Purge", "Secure", "Annihilation"],
            "Your Army": ["Space Marines", "Tyranids", "Orks"],
            "Enemy Faction": ["Tyranids", "Orks", "Chaos"],
            "Difficulty": ["Easy", "Medium", "Hard"],
        }
        self.selected_field = 0
        self.selected_option = {f: 0 for f in self.fields}
        self.font = pygame.font.Font(None, 36)

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    self.selected_field = (self.selected_field - 1) % len(self.fields)
                elif e.key == pygame.K_DOWN:
                    self.selected_field = (self.selected_field + 1) % len(self.fields)
                elif e.key == pygame.K_LEFT:
                    f = self.fields[self.selected_field]
                    self.selected_option[f] = (self.selected_option[f] - 1) % len(self.options[f])
                elif e.key == pygame.K_RIGHT:
                    f = self.fields[self.selected_field]
                    self.selected_option[f] = (self.selected_option[f] + 1) % len(self.options[f])
                elif e.key == pygame.K_RETURN:
                    from .states import BattleState
                    self.game.state = BattleState(self.game)
                elif e.key == pygame.K_ESCAPE:
                    from .states import MainMenu
                    self.game.state = MainMenu(self.game)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((0, 0, 0))
        y0 = SCREEN_HEIGHT // 2 - len(self.fields) * 30
        for i, f in enumerate(self.fields):
            sel = (i == self.selected_field)
            color = (255, 255, 255) if sel else (150, 150, 150)
            txt = f"{f}: {self.options[f][self.selected_option[f]]}"
            lbl = self.font.render(txt, True, color)
            rect = lbl.get_rect(center=(SCREEN_WIDTH // 2, y0 + i * 60))
            surface.blit(lbl, rect)
        hint = "↑↓ select field, ←→ cycle, Enter to battle, Esc to menu"
        hlp = self.font.render(hint, True, (100, 100, 100))
        surface.blit(hlp, hlp.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))


class BattleState(State):
    """Battlefield: draws grid, movement highlight, units, and stats panel."""

    def __init__(self, game):
        super().__init__(game)
        self.units = [
            Unit(
                name="Tactical Marine",
                ws=3, bs=3, strength=4, toughness=4,
                wounds=2, attacks=1,
                leadership=7, save=3,
                position=(1, 1),
                team="player",
                sprite_file="tactical_marine.png",
                abilities=["And They Shall Know No Fear"]
            ),
            # …and some enemies
        ]
        self.hover_tile = None  # (x, y) grid coordinates of tile under mouse

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                from .states import MainMenu
                self.game.state = MainMenu(self.game)
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE

                clicked_unit = next((u for u in self.units if u.position == (gx, gy)), None)
                if clicked_unit:
                    for u in self.units:
                        u.selected = False
                    clicked_unit.selected = True
                else:
                    selected = [u for u in self.units if u.selected]
                    if selected:
                        u = selected[0]
                        if not any(o.position == (gx, gy) for o in self.units):
                            dx = abs(gx - u.position[0])
                            dy = abs(gy - u.position[1])
                            if dx + dy <= u.movement:
                                u.position = (gx, gy)
            elif e.type == pygame.MOUSEMOTION:
                mx, my = e.pos
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                    self.hover_tile = (gx, gy)
                else:
                    self.hover_tile = None

    def update(self, dt):
        pass

    def draw(self, surface):
        # Fill background
        surface.fill((30, 30, 30))

        # Draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surface, (50, 50, 50), rect, 1)

        # Highlight movement range
        selected = [u for u in self.units if u.selected]
        if selected:
            u = selected[0]
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 255, 0, 80))
            ux, uy = u.position
            for x in range(GRID_WIDTH):
                for y in range(GRID_HEIGHT):
                    if abs(x - ux) + abs(y - uy) <= u.movement:
                        surface.blit(overlay, (x * TILE_SIZE, y * TILE_SIZE))

        # Draw hover tile
        if self.hover_tile:
            x, y = self.hover_tile
            hover_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, (255, 255, 255), hover_rect, 2)

        # Draw units
        for u in self.units:
            u.draw(surface)

        # Outline hovered unit
        if self.hover_tile:
            hovered = next((u for u in self.units if u.position == self.hover_tile), None)
            if hovered:
                # compute pixel center
                px = self.hover_tile[0] * TILE_SIZE + TILE_SIZE // 2
                py = self.hover_tile[1] * TILE_SIZE + TILE_SIZE // 2
                outline_color = (255, 255, 0)  # subtle yellow
                if hovered.sprite:
                    rect = hovered.sprite.get_rect(center=(px, py))
                    pygame.draw.rect(surface, outline_color, rect, 3)
                else:
                    radius = TILE_SIZE // 3 + 4
                    pygame.draw.circle(surface, outline_color, (px, py), radius, 3)

        # Draw stats panel
        panel_x = SCREEN_WIDTH - STAT_PANEL_WIDTH
        panel = pygame.Rect(panel_x, 0, STAT_PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(surface, (20, 20, 20), panel)
        pygame.draw.line(surface, (100, 100, 100),
                         (panel_x, 0), (panel_x, SCREEN_HEIGHT), 2)

        font = pygame.font.Font(None, 28)
        y_offset = 20

        if selected:
            u = selected[0]

            # Draw unit sprite preview
            if u.sprite:
                preview_size = TILE_SIZE * 1.5
                scaled = pygame.transform.scale(u.sprite, (int(preview_size), int(preview_size)))
                rect = scaled.get_rect(center=(panel_x + STAT_PANEL_WIDTH // 2, y_offset + preview_size // 2))
                surface.blit(scaled, rect)
                y_offset += preview_size + 10

            # Text info
            lines = [
                f"WS: {u.ws}+  BS: {u.bs}+",
                f"S: {u.strength}  T: {u.toughness}",
                f"W: {u.current_wounds}/{u.max_wounds}",
                f"A: {u.attacks}  Ld: {u.leadership}",
                f"Sv: {u.save}+",
            ]
            # then after that, list u.abilities below if any

        else:
            lines = ["No unit selected"]

        for idx, text in enumerate(lines):
            lbl = font.render(text, True, (200, 200, 200))
            surface.blit(lbl, (panel_x + 10, y_offset + idx * 35))
