# core/states.py

import pygame
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, MAP_TILES_X, MAP_TILES_Y, STAT_PANEL_WIDTH, PAN_SPEED, \
    PAN_MARGIN
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
        self.camera_x, self.camera_y = 0, 0
        self.mouse_pos = (0, 0)

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
                    self.game.state = MainMenu(self.game)
                elif e.key == pygame.K_e and self.phase == "player":
                    self.phase = "enemy"
                    self.enemy_processed = False

            elif e.type == pygame.MOUSEMOTION:
                # Always track mouse for camera panning…
                self.mouse_pos = e.pos

                # …and compute hover_tile in world coords
                wx = e.pos[0] + self.camera_x
                wy = e.pos[1] + self.camera_y
                gx, gy = wx // TILE_SIZE, wy // TILE_SIZE
                if 0 <= gx < MAP_TILES_X and 0 <= gy < MAP_TILES_Y:
                    self.hover_tile = (gx, gy)
                else:
                    self.hover_tile = None

            # Only allow clicks during player phase
            elif self.phase == "player" and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                # convert to world coords too
                gx = (mx + self.camera_x) // TILE_SIZE
                gy = (my + self.camera_y) // TILE_SIZE

                clicked = next((u for u in self.units if u.position == (gx, gy)), None)
                selected = next((u for u in self.units if u.selected), None)

                if clicked and clicked.team == "player":
                    # select your own
                    for u in self.units: u.selected = False
                    clicked.selected = True

                elif selected and clicked and clicked.team != "player":
                    # attack in range
                    dist = abs(gx - selected.position[0]) + abs(gy - selected.position[1])
                    if dist <= selected.attack_range and not selected.has_attacked:
                        selected.attack(clicked)
                        if not clicked.is_alive():
                            self.units.remove(clicked)

                elif selected and not clicked:
                    # move in range
                    dist = abs(gx - selected.position[0]) + abs(gy - selected.position[1])
                    occupied = any(u.position == (gx, gy) for u in self.units)
                    if dist <= selected.movement and not occupied and not selected.has_moved:
                        selected.position = (gx, gy)
                        selected.has_moved = True

    def update(self, dt):
        # —— camera panning based on current mouse pos ——
        mx, my = pygame.mouse.get_pos()  # get real‐time mouse coords

        # pan left/right
        if mx < PAN_MARGIN:
            self.camera_x -= PAN_SPEED * dt
        elif mx > SCREEN_WIDTH - PAN_MARGIN:
            self.camera_x += PAN_SPEED * dt

        # pan up/down
        if my < PAN_MARGIN:
            self.camera_y -= PAN_SPEED * dt
        elif my > SCREEN_HEIGHT - PAN_MARGIN:
            self.camera_y += PAN_SPEED * dt

        # clamp camera so it never leaves the map bounds
        max_x = MAP_TILES_X * TILE_SIZE - SCREEN_WIDTH
        max_y = MAP_TILES_Y * TILE_SIZE - SCREEN_HEIGHT
        self.camera_x = max(0, min(self.camera_x, max_x))
        self.camera_y = max(0, min(self.camera_y, max_y))

        # —— enemy AI ——
        if self.phase == "enemy" and not self.enemy_processed:
            enemy_turn(self.units)
            self.enemy_processed = True
            # reset per‐turn flags
            for u in self.units:
                u.has_moved = u.has_attacked = False
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
                if (0 <= new_pos[0] < MAP_TILES_X and
                        0 <= new_pos[1] < MAP_TILES_Y and
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
        # 1) clear & turn label
        surface.fill((30, 30, 30))
        hdr = pygame.font.Font(None, 36)
        txt = "Player Turn" if self.phase == "player" else "Enemy Turn"
        surface.blit(hdr.render(txt, True, (255, 255, 255)), (10, 10))

        # 2) grid with camera
        BattleUI.draw_grid(surface, self.camera_x, self.camera_y)

        # 3) movement highlight (green)
        sel = [u for u in self.units if u.selected]
        if sel:
            u = sel[0]
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 255, 0, 80))
            ux, uy = u.position
            for x in range(MAP_TILES_X):
                for y in range(MAP_TILES_Y):
                    if abs(x - ux) + abs(y - uy) <= u.movement:
                        surface.blit(overlay,
                                     (x * TILE_SIZE - self.camera_x,
                                      y * TILE_SIZE - self.camera_y))

        # 4) attack highlight (red)
        if sel:
            u = sel[0]
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 80))
            ux, uy = u.position
            for x in range(MAP_TILES_X):
                for y in range(MAP_TILES_Y):
                    if abs(x - ux) + abs(y - uy) <= u.attack_range:
                        surface.blit(overlay,
                                     (x * TILE_SIZE - self.camera_x,
                                      y * TILE_SIZE - self.camera_y))

        # 5) hover‐tile highlight (white)
        if self.hover_tile:
            hx, hy = self.hover_tile
            rect = pygame.Rect(
                hx * TILE_SIZE - self.camera_x,
                hy * TILE_SIZE - self.camera_y,
                TILE_SIZE, TILE_SIZE
            )
            pygame.draw.rect(surface, (255, 255, 255), rect, 2)

        # 6) draw units (with camera)
        for u in self.units:
            u.draw(surface, self.camera_x, self.camera_y)

        # 7) outline hovered unit (yellow)
        if self.hover_tile:
            hovered = next((u for u in self.units if u.position == self.hover_tile), None)
            if hovered:
                # screen‐space center
                px = hovered.position[0] * TILE_SIZE - self.camera_x + TILE_SIZE // 2
                py = hovered.position[1] * TILE_SIZE - self.camera_y + TILE_SIZE // 2
                oc = (255, 255, 0)
                if hovered.sprite:
                    rect = hovered.sprite.get_rect(center=(px, py))
                    pygame.draw.rect(surface, oc, rect, 3)
                else:
                    pygame.draw.circle(surface, oc, (px, py), TILE_SIZE // 3 + 4, 3)

        # 8) stats panel (fixed)
        BattleUI.draw_stats_panel(surface, self)
