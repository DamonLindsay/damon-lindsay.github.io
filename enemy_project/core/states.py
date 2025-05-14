# core/states.py
import pygame

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
                        # TODO: switch to your PvEState
                        pass
                    else:  # Quit
                        self.game.running = False

    def update(self, dt):
        # nothing dynamic yet
        pass

    def draw(self, surface):
        surface.fill((0, 0, 0))
        for idx, text in enumerate(self.options):
            color = (255, 255, 255) if idx == self.selected else (100, 100, 100)
            label = self.font.render(text, True, color)
            rect = label.get_rect(center=(SCREEN_WIDTH // 2,
                                          SCREEN_HEIGHT // 2 + idx * 60))
            surface.blit(label, rect)
