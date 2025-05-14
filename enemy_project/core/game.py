import pygame
from .settings import TITLE, SCREEN_WIDTH, SCREEN_HEIGHT, FPS


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            # cap the framerate
            self.clock.tick(FPS)
        self._quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def _update(self):
        # placeholder for game logic updates
        pass

    def _draw(self):
        self.screen.fill((0, 0, 0))  # clear to black
        pygame.display.flip()  # push to screen

    def _quit(self):
        pygame.quit()
