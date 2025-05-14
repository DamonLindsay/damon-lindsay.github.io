# core/states.py

import pygame
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT
from .unit import Unit


class State:
    """Base class for all game states."""

    def __init__(self, game):
        self.game = game

    def handle_events(self, events): pass

    def update(self, dt):       pass

    def draw(self, surface):    pass


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
    """Battlefield: draws grid, units, and allows click-to-move within range."""

    def __init__(self, game):
        super().__init__(game)
        # example unit at 1,1
        self.units = [
            Unit("Space Marine", hp=10, attack=3, movement=5, position=(1, 1))
        ]

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                from .states import MainMenu
                self.game.state = MainMenu(self.game)

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE

                # see if we clicked on a unit
                clicked_unit = next((u for u in self.units if u.position == (gx, gy)), None)
                if clicked_unit:
                    # select this unit
                    for u in self.units:
                        u.selected = False
                    clicked_unit.selected = True

                else:
                    # clicked empty tile: if we have exactly one selected unit, try to move it
                    selected = [u for u in self.units if u.selected]
                    if selected:
                        u = selected[0]
                        # ensure tile not occupied
                        occupied = any(o.position == (gx, gy) for o in self.units)
                        if not occupied:
                            dx = abs(gx - u.position[0])
                            dy = abs(gy - u.position[1])
                            if dx + dy <= u.movement:
                                u.position = (gx, gy)
                            # else: ignore or play invalid move sound

    def update(self, dt):
        pass

    def draw(self, surface):
        # background
        surface.fill((30, 30, 30))

        # grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surface, (50, 50, 50), rect, 1)

        # units
        for u in self.units:
            u.draw(surface)

        # stats panel (unchanged)
        from .settings import STAT_PANEL_WIDTH
        panel_x = SCREEN_WIDTH - STAT_PANEL_WIDTH
        panel = pygame.Rect(panel_x, 0, STAT_PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(surface, (20, 20, 20), panel)
        pygame.draw.line(surface, (100, 100, 100),
                         (panel_x, 0), (panel_x, SCREEN_HEIGHT), 2)

        selected = [u for u in self.units if u.selected]
        if selected:
            u = selected[0]
            lines = [
                f"Name:     {u.name}",
                f"HP:       {u.hp}",
                f"Attack:   {u.attack}",
                f"Movement: {u.movement}",
            ]
        else:
            lines = ["No unit selected"]

        font = pygame.font.Font(None, 28)
        for idx, text in enumerate(lines):
            lbl = font.render(text, True, (200, 200, 200))
            surface.blit(lbl, (panel_x + 10, 20 + idx * 35))
