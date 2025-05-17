# core/states.py

import pygame
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, STAT_PANEL_WIDTH
from .unit import Unit
from .ai import enemy_turn
from enemy_project.ui.battle_ui import BattleUI
from .ui import Button
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT


class State:
    """Base class for all game states."""

    def __init__(self, game):
        self.game = game

    def handle_events(self, events): pass

    def update(self, dt):       pass

    def draw(self, surface):    pass


class MainMenu(State):
    """Main menu using clickable Button components."""

    def __init__(self, game):
        super().__init__(game)

        # Prepare a font and button dimensions
        font = pygame.font.Font(None, 48)
        btn_w, btn_h = 250, 60
        cx = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2 - btn_h - 10

        # Create buttons
        self.buttons = [
            Button(
                rect=(cx - btn_w // 2, start_y, btn_w, btn_h),
                text="Start PvE",
                callback=self._on_start,
                font=font
            ),
            Button(
                rect=(cx - btn_w // 2, start_y + btn_h + 20, btn_w, btn_h),
                text="Quit",
                callback=lambda: setattr(self.game, "running", False),
                font=font
            )
        ]

    def _on_start(self):
        from .states import PvESetup
        self.game.state = PvESetup(self.game)

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.QUIT:
                self.game.running = False
            for btn in self.buttons:
                btn.handle_event(e)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((0, 0, 0))
        for btn in self.buttons:
            btn.draw(surface)


class PvESetup(State):
    """PvE setup screen with clickable Buttons to select options."""

    def __init__(self, game):
        super().__init__(game)

        # Fields and their option lists
        self.fields = ["Mission", "Your Army", "Enemy Faction", "Difficulty"]
        self.options = {
            "Mission": ["Purge", "Secure", "Annihilation"],
            "Your Army": ["Space Marines", "Tyranids", "Orks"],
            "Enemy Faction": ["Tyranids", "Orks", "Chaos"],
            "Difficulty": ["Easy", "Medium", "Hard"],
        }
        # Track selected index per field
        self.selected = {f: 0 for f in self.fields}

        # Layout calculations
        font = pygame.font.Font(None, 36)
        x_center = SCREEN_WIDTH // 2
        y_start = SCREEN_HEIGHT // 4
        row_height = 80
        arrow_size = (40, 40)
        label_offset_x = - (arrow_size[0] + 20)

        # Buttons list
        self.buttons = []

        # Create left/right buttons for each field
        for i, field in enumerate(self.fields):
            y = y_start + i * row_height

            # Left arrow
            self.buttons.append(Button(
                rect=(x_center - 100 + label_offset_x, y, *arrow_size),
                text="<",
                callback=lambda f=field: self._change(f, -1),
                font=font
            ))

            # Right arrow
            self.buttons.append(Button(
                rect=(x_center + 60, y, *arrow_size),
                text=">",
                callback=lambda f=field: self._change(f, +1),
                font=font
            ))

        # Confirm button
        self.buttons.append(Button(
            rect=(x_center - 100, y_start + len(self.fields) * row_height, 200, 60),
            text="Confirm",
            callback=self._on_confirm,
            font=font
        ))

        # Back button
        small_font = pygame.font.Font(None, 24)
        self.buttons.append(Button(
            rect=(10, 10, 100, 40),
            text="Back",
            callback=lambda: setattr(self.game, "state", MainMenu(self.game)),
            font=small_font
        ))

    def _change(self, field, delta):
        opts = self.options[field]
        idx = (self.selected[field] + delta) % len(opts)
        self.selected[field] = idx

    def _on_confirm(self):
        cfg = {
            "mission": self.options["Mission"][self.selected["Mission"]],
            "player_army": self.options["Your Army"][self.selected["Your Army"]],
            "enemy_faction": self.options["Enemy Faction"][self.selected["Enemy Faction"]],
            "difficulty": self.options["Difficulty"][self.selected["Difficulty"]],
        }
        self.game.state = BattleState(self.game, cfg)

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.QUIT:
                self.game.running = False
            for btn in self.buttons:
                btn.handle_event(e)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((0, 0, 0))
        font = pygame.font.Font(None, 36)
        x_center = SCREEN_WIDTH // 2
        y_start = SCREEN_HEIGHT // 4
        row_h = 80
        arrow_gap = 200  # horizontal distance from center to each arrow

        # Draw each field row: left arrow, label, right arrow
        for i, field in enumerate(self.fields):
            y = y_start + i * row_h

            # left/right arrow buttons (created in __init__)
            left_btn = self.buttons[2 * i]
            right_btn = self.buttons[2 * i + 1]

            # reposition and draw arrows
            left_btn.rect.center = (x_center - arrow_gap, y)
            right_btn.rect.center = (x_center + arrow_gap, y)
            left_btn.draw(surface)
            right_btn.draw(surface)

            # draw the label centered between them
            choice = self.options[field][self.selected[field]]
            txt = f"{field}: {choice}"
            lbl = font.render(txt, True, (255, 255, 255))
            lbl_rect = lbl.get_rect(center=(x_center, y))
            surface.blit(lbl, lbl_rect)

        # draw the Confirm and Back buttons (they follow in your buttons list)
        for btn in self.buttons[2 * len(self.fields):]:
            btn.draw(surface)


class BattleState(State):
    """Battlefield: config-driven setup."""

    def __init__(self, game, config):
        super().__init__(game)
        self.config = config
        self.phase = "player"
        self.enemy_processed = True
        self.hover_tile = None
        self.units = []

        # Spawn player army
        if config["player_army"] == "Space Marines":
            self.units.append(Unit(
                name="Tactical Marine", ws=3, bs=3, strength=4, toughness=4,
                wounds=2, attacks=1, movement=5, leadership=7, save=3,
                position=(1, 1), attack_range=1, team="player",
                sprite_file="tactical_marine.png"
            ))
        elif config["player_army"] == "Tyranids":
            self.units.append(Unit(
                name="Hormagaunt", ws=3, bs=0, strength=3, toughness=3,
                wounds=1, attacks=2, movement=6, leadership=5, save=6,
                position=(1, 1), attack_range=1, team="player",
                sprite_file="tyranid.png"
            ))
        elif config["player_army"] == "Orks":
            self.units.append(Unit(
                name="Ork Boy", ws=3, bs=5, strength=4, toughness=4,
                wounds=1, attacks=2, movement=5, leadership=6, save=6,
                position=(1, 1), attack_range=1, team="player",
                sprite_file="ork.png"
            ))

        # Spawn enemy faction
        if config["enemy_faction"] == "Orks":
            self.units.append(Unit(
                name="Enemy Ork", ws=3, bs=5, strength=4, toughness=4,
                wounds=1, attacks=2, movement=5, leadership=6, save=6,
                position=(5, 2), attack_range=1, team="enemy",
                sprite_file="ork.png"
            ))
        elif config["enemy_faction"] == "Tyranids":
            self.units.append(Unit(
                name="Enemy Hormagaunt", ws=3, bs=0, strength=3, toughness=3,
                wounds=1, attacks=2, movement=6, leadership=5, save=6,
                position=(5, 2), attack_range=1, team="enemy",
                sprite_file="tyranid.png"
            ))
        elif config["enemy_faction"] == "Chaos":
            self.units.append(Unit(
                name="Chaos Cultist", ws=4, bs=4, strength=3, toughness=3,
                wounds=1, attacks=1, movement=6, leadership=6, save=6,
                position=(5, 2), attack_range=1, team="enemy",
                sprite_file="cultist.png"
            ))

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.QUIT:
                self.game.running = False

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    from .states import MainMenu
                    self.game.state = MainMenu(self.game)
                elif e.key == pygame.K_e and self.phase == "player":
                    # end player turn
                    self.phase = "enemy"
                    self.enemy_processed = False

            elif e.type == pygame.MOUSEMOTION:
                mx, my = e.pos
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                self.hover_tile = (gx, gy) if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT else None

            # only during player phase:
            elif self.phase == "player" and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE

                clicked = next((u for u in self.units if u.position == (gx, gy)), None)
                selected = next((u for u in self.units if u.selected), None)

                # 1) select your own
                if clicked and clicked.team == "player":
                    for u in self.units:
                        u.selected = False
                    clicked.selected = True

                # 2) attack if in range and not yet attacked
                elif selected and clicked and clicked.team != "player":
                    dist = abs(gx - selected.position[0]) + abs(gy - selected.position[1])
                    if dist <= selected.attack_range and not selected.has_attacked:
                        selected.attack(clicked)
                        if not clicked.is_alive():
                            self.units.remove(clicked)

                # 3) move if in range and not yet moved
                elif selected and not clicked:
                    dist = abs(gx - selected.position[0]) + abs(gy - selected.position[1])
                    occupied = any(u.position == (gx, gy) for u in self.units)
                    if dist <= selected.movement and not occupied and not selected.has_moved:
                        selected.position = (gx, gy)
                        selected.has_moved = True

    def update(self, dt):
        # run enemy AI once when it's enemy phase
        if self.phase == "enemy" and not self.enemy_processed:
            enemy_turn(self.units)
            self.enemy_processed = True

            # reset player flags
            for u in self.units:
                u.has_moved = False
                u.has_attacked = False
            self.phase = "player"

    def _run_enemy_ai(self):
        # For each enemy unit, move toward nearest player, then attack if in range
        player_units = [u for u in self.units if u.team == "player"]
        for enemy in [u for u in self.units if u.team == "enemy"]:
            if not player_units:
                break

            # find nearest player
            target = min(player_units,
                         key=lambda pu: abs(pu.position[0] - enemy.position[0]) +
                                        abs(pu.position[1] - enemy.position[1]))
            ex, ey = enemy.position
            tx, ty = target.position
            dist = abs(tx - ex) + abs(ty - ey)

            # move toward if not in attack range
            if dist > enemy.attack_range:
                # simple step: move one tile along the larger delta
                dx, dy = tx - ex, ty - ey
                step_x = 1 if dx > 0 else -1 if dx < 0 else 0
                step_y = 1 if dy > 0 else -1 if dy < 0 else 0
                # prefer x movement if farther
                if abs(dx) >= abs(dy):
                    new_pos = (ex + step_x, ey)
                else:
                    new_pos = (ex, ey + step_y)

                # ensure tile free
                if (0 <= new_pos[0] < GRID_WIDTH and
                        0 <= new_pos[1] < GRID_HEIGHT and
                        not any(u.position == new_pos for u in self.units)):
                    enemy.position = new_pos
                    dist -= 1  # update distance

            # attack if now in range
            if abs(tx - enemy.position[0]) + abs(ty - enemy.position[1]) <= enemy.attack_range:
                enemy.attack(target)
                if not target.is_alive():
                    self.units.remove(target)
                    player_units.remove(target)

    def draw(self, surface):
        # 1) Clear background
        surface.fill((30, 30, 30))

        # 2) Turn indicator
        font_hdr = pygame.font.Font(None, 36)
        text = "Player Turn" if self.phase == "player" else "Enemy Turn"
        surface.blit(font_hdr.render(text, True, (255, 255, 255)), (10, 10))

        # 3) Grid
        BattleUI.draw_grid(surface)

        # 4) Movement‐range highlight (green)
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

        # 5) Attack‐range highlight (red)
        if sel:
            u = sel[0]
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 80))
            ux, uy = u.position
            for x in range(GRID_WIDTH):
                for y in range(GRID_HEIGHT):
                    if abs(x - ux) + abs(y - uy) <= u.attack_range:
                        surface.blit(overlay, (x * TILE_SIZE, y * TILE_SIZE))

        # 6) Hover‐tile highlight (white border)
        if self.hover_tile:
            hx, hy = self.hover_tile
            pygame.draw.rect(
                surface,
                (255, 255, 255),
                (hx * TILE_SIZE, hy * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                2
            )

        # 7) Draw units
        for u in self.units:
            u.draw(surface)

        # 8) Outline hovered unit (yellow)
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

        # 9) Stats panel
        BattleUI.draw_stats_panel(surface, self)
