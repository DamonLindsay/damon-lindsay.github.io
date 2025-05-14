import pygame
from .settings import TITLE, SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from .states import MainMenu


class Game:
    def __init__(self):
        # Initialize Pygame and create the window
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = False

        # Start in the MainMenu state
        self.state = MainMenu(self)

    def run(self):
        self.running = True
        while self.running:
            # Event handling
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False

            # Delta time in seconds
            dt = self.clock.get_time() / 1000.0

            # Delegate to current state
            self.state.handle_events(events)
            self.state.update(dt)
            self.state.draw(self.screen)

            # Flip and tick
            pygame.display.flip()
            self.clock.tick(FPS)

        # Clean up
        pygame.quit()
