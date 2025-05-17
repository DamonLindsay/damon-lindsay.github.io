# core/ui.py

import pygame


class Button:
    """
    A clickable button with a text label.
    Call handle_event() from your event loop, and draw() each frame.
    """

    def __init__(
            self,
            rect: tuple[int, int, int, int],
            text: str,
            callback: callable,
            font: pygame.font.Font,
            bg_color: tuple[int, int, int] = (50, 50, 50),
            text_color: tuple[int, int, int] = (255, 255, 255)
    ):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.hovered = False

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.callback()

    def draw(self, surface: pygame.Surface):
        # slightly brighten background on hover
        color = (
            min(self.bg_color[0] + 30, 255),
            min(self.bg_color[1] + 30, 255),
            min(self.bg_color[2] + 30, 255)
        ) if self.hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect)
        # render text centered
        txt_surf = self.font.render(self.text, True, self.text_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)
