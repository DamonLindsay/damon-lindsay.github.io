# core/states.py

import pygame
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, STAT_PANEL_WIDTH
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
                    if self.options[self.selected] == "Start PvE":
                        from .states import PvESetup
                        self.game.state = PvESetup(self.game)
                    else:
                        self.game.running = False

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
    """PvE setup: pick mission, army, enemy and difficulty."""

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
        hint = "↑↓ select field, ←→ change, Enter to battle, Esc to menu"
        hlp = self.font.render(hint, True, (100, 100, 100))
        surface.blit(hlp, hlp.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))


class BattleState(State):
    """Battlefield: turn phases, grid, highlights, units, and stats."""

    def __init__(self, game):
        super().__init__(game)
        # turn phase: "player" or "enemy"
        self.phase = "player"
        self.units = [
            Unit(
                name="Tactical Marine",
                ws=3, bs=3, strength=4, toughness=4,
                wounds=2, attacks=1, movement=5,
                leadership=7, save=3,
                position=(1, 1),
                attack_range=1,
                team="player",
                sprite_file="tactical_marine.png",
                abilities=["And They Shall Know No Fear"]
            ),
            Unit(
                name="Enemy Ork",
                ws=2, bs=0, strength=3, toughness=4,
                wounds=1, attacks=2, movement=6,
                leadership=6, save=6,
                position=(5, 2),
                attack_range=1,
                team="enemy",
                sprite_file="ork.png"
            ),
        ]
        self.hover_tile = None

    def handle_events(self, events):
        for e in events:
            # quit / back to menu
            if e.type == pygame.QUIT:
                self.game.running = False

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    from .states import MainMenu
                    self.game.state = MainMenu(self.game)

                # end turn on E, only in player phase
                elif e.key == pygame.K_e and self.phase == "player":
                    self.phase = "enemy"
                    # (enemy AI will trigger later)

            # track hover always (for UI)
            elif e.type == pygame.MOUSEMOTION:
                mx, my = e.pos
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                self.hover_tile = (gx, gy) if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT else None

            # only allow clicks in player phase
            elif self.phase == "player" and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE

                clicked = next((u for u in self.units if u.position == (gx, gy)), None)
                selected = [u for u in self.units if u.selected]

                # select your own
                if clicked and clicked.team == "player":
                    for u in self.units: u.selected = False
                    clicked.selected = True

                # attack enemy
                elif selected and clicked and clicked.team != "player":
                    attacker = selected[0]
                    dist = abs(gx - attacker.position[0]) + abs(gy - attacker.position[1])
                    if dist <= attacker.attack_range:
                        attacker.attack(clicked)
                        if not clicked.is_alive():
                            self.units.remove(clicked)

                # move
                elif selected and not clicked:
                    mover = selected[0]
                    dist = abs(gx - mover.position[0]) + abs(gy - mover.position[1])
                    occupied = any(u.position == (gx, gy) for u in self.units)
                    if dist <= mover.movement and not occupied:
                        mover.position = (gx, gy)

    def draw(self, surface):
        # draw phase label
        font_hdr = pygame.font.Font(None, 36)
        text = "Player Turn" if self.phase == "player" else "Enemy Turn"
        lbl = font_hdr.render(text, True, (255, 255, 255))
        surface.blit(lbl, (10, 10))

        # background & grid
        surface.fill((30, 30, 30))
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(
                    surface, (50, 50, 50),
                    (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1
                )

        # movement range highlight
        sel = [u for u in self.units if u.selected]
        if sel:
            u = sel[0]
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 255, 0, 80))
            ux, uy = u.position
            for x in range(GRID_WIDTH):
                for y in range(GRID_HEIGHT):
                    if abs(x - ux) + abs(y - uy) <= u.movement:
                        surface.blit(overlay, (x * TILE_SIZE, y * TILE_SIZE))

        # Attack-range highlight (red)
        if sel:
            u = sel[0]
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 80))
            ux, uy = u.position
            for x in range(GRID_WIDTH):
                for y in range(GRID_HEIGHT):
                    if abs(x - ux) + abs(y - uy) <= u.attack_range:
                        surface.blit(overlay, (x * TILE_SIZE, y * TILE_SIZE))

        # hover tile highlight
        if self.hover_tile:
            x, y = self.hover_tile
            pygame.draw.rect(
                surface, (255, 255, 255),
                (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2
            )

        # draw units
        for u in self.units:
            u.draw(surface)

        # outline hovered unit
        if self.hover_tile:
            hovered = next((u for u in self.units if u.position == self.hover_tile), None)
            if hovered:
                px = self.hover_tile[0] * TILE_SIZE + TILE_SIZE // 2
                py = self.hover_tile[1] * TILE_SIZE + TILE_SIZE // 2
                oc = (255, 255, 0)
                if hovered.sprite:
                    rect = hovered.sprite.get_rect(center=(px, py))
                    pygame.draw.rect(surface, oc, rect, 3)
                else:
                    pygame.draw.circle(surface, oc, (px, py), TILE_SIZE // 3 + 4, 3)

        # stats panel
        panel_x = SCREEN_WIDTH - STAT_PANEL_WIDTH
        pygame.draw.rect(surface, (20, 20, 20),
                         (panel_x, 0, STAT_PANEL_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(surface, (100, 100, 100),
                         (panel_x, 0), (panel_x, SCREEN_HEIGHT), 2)

        font = pygame.font.Font(None, 28)
        yoff = 20
        if sel:
            u = sel[0]
            # sprite preview
            if u.sprite:
                ps = int(TILE_SIZE * 1.5)
                img = pygame.transform.scale(u.sprite, (ps, ps))
                rect = img.get_rect(center=(panel_x + STAT_PANEL_WIDTH // 2, yoff + ps // 2))
                surface.blit(img, rect)
                yoff += ps + 10
            # stat lines
            lines = [
                f"WS: {u.ws}+   BS: {u.bs}+",
                f"S: {u.strength}   T: {u.toughness}",
                f"W: {u.current_wounds}/{u.max_wounds}",
                f"A: {u.attacks}   Ld: {u.leadership}",
                f"Sv: {u.save}+",
            ]
        else:
            lines = ["No unit selected"]

        for i, txt in enumerate(lines):
            lbl = font.render(txt, True, (200, 200, 200))
            surface.blit(lbl, (panel_x + 10, yoff + i * 35))
