# core/states.py

import pygame
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT


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
                    else:  # Quit
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
                    field = self.fields[self.selected_field]
                    opts = self.options[field]
                    self.selected_option[field] = (self.selected_option[field] - 1) % len(opts)
                elif e.key == pygame.K_RIGHT:
                    field = self.fields[self.selected_field]
                    opts = self.options[field]
                    self.selected_option[field] = (self.selected_option[field] + 1) % len(opts)
                elif e.key == pygame.K_RETURN:
                    # TODO: start the battle with these settings
                    # For now, go back to MainMenu
                    from .states import MainMenu
                    self.game.state = MainMenu(self.game)
                elif e.key == pygame.K_ESCAPE:
                    from .states import MainMenu
                    self.game.state = MainMenu(self.game)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((0, 0, 0))
        y = SCREEN_HEIGHT // 2 - len(self.fields) * 25
        for idx, field in enumerate(self.fields):
            is_sel = (idx == self.selected_field)
            color = (255, 255, 255) if is_sel else (150, 150, 150)
            text = f"{field}: {self.options[field][self.selected_option[field]]}"
            label = self.font.render(text, True, color)
            rect = label.get_rect(center=(SCREEN_WIDTH // 2, y + idx * 60))
            surface.blit(label, rect)
        # hint
        hint = "Use ↑↓ to choose field, ←→ to change, Enter to confirm, Esc to cancel"
        hint_lbl = self.font.render(hint, True, (100, 100, 100))
        hint_rect = hint_lbl.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        surface.blit(hint_lbl, hint_rect)
