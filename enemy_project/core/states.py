# core/states.py

import pygame
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, STAT_PANEL_WIDTH
from .unit import Unit
from .combat import to_hit_roll, wound_roll, saving_throw  # if you need them


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
                    # Prepare setup config
                    cfg = {
                        "mission": self.options["Mission"][self.selected_option["Mission"]],
                        "player_army": self.options["Your Army"][self.selected_option["Your Army"]],
                        "enemy_faction": self.options["Enemy Faction"][self.selected_option["Enemy Faction"]],
                        "difficulty": self.options["Difficulty"][self.selected_option["Difficulty"]],
                    }
                    from .states import BattleState
                    self.game.state = BattleState(self.game, cfg)
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
        if self.phase == "enemy" and not self.enemy_processed:
            self._run_enemy_ai()
            self.enemy_processed = True
            # reset flags for next player phase
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

        # 2) Phase label
        font_hdr = pygame.font.Font(None, 36)
        text = "Player Turn" if self.phase == "player" else "Enemy Turn"
        surface.blit(font_hdr.render(text, True, (255, 255, 255)), (10, 10))

        # 3) Draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(
                    surface,
                    (50, 50, 50),
                    (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                    1
                )

        sel = [u for u in self.units if u.selected]
        # 4) Movement-range highlight (green)
        if sel:
            u = sel[0]
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 255, 0, 80))
            ux, uy = u.position
            for x in range(GRID_WIDTH):
                for y in range(GRID_HEIGHT):
                    if abs(x - ux) + abs(y - uy) <= u.movement:
                        surface.blit(overlay, (x * TILE_SIZE, y * TILE_SIZE))

        # 5) Attack-range highlight (red)
        if sel:
            u = sel[0]
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 80))
            ux, uy = u.position
            for x in range(GRID_WIDTH):
                for y in range(GRID_HEIGHT):
                    if abs(x - ux) + abs(y - uy) <= u.attack_range:
                        surface.blit(overlay, (x * TILE_SIZE, y * TILE_SIZE))

        # 6) Hover-tile highlight (white border)
        if self.hover_tile:
            hx, hy = self.hover_tile
            pygame.draw.rect(
                surface,
                (255, 255, 255),
                (hx * TILE_SIZE, hy * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                2
            )

        # 7) Draw all units
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

        # 9) Stats panel (always drawn)
        panel_x = SCREEN_WIDTH - STAT_PANEL_WIDTH
        padding = 10

        # background + divider
        pygame.draw.rect(surface, (20, 20, 20),
                         (panel_x, 0, STAT_PANEL_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(surface, (100, 100, 100),
                         (panel_x, 0), (panel_x, SCREEN_HEIGHT), 2)

        # pick hover > selected
        hover_u = None
        if self.hover_tile:
            hover_u = next((u for u in self.units
                            if u.position == self.hover_tile), None)
        sel_u = next((u for u in self.units if u.selected), None)
        u = hover_u or sel_u

        font_name = pygame.font.Font(None, 32)
        font_stat = pygame.font.Font(None, 24)

        if u:
            # Name
            name_lbl = font_name.render(u.name, True, (255, 255, 255))
            name_rect = name_lbl.get_rect(center=(
                panel_x + STAT_PANEL_WIDTH // 2,
                padding + name_lbl.get_height() // 2
            ))
            surface.blit(name_lbl, name_rect)

            # Portrait
            portrait_size = STAT_PANEL_WIDTH - padding * 2
            portrait_rect = pygame.Rect(
                panel_x + padding,
                name_rect.bottom + padding,
                portrait_size, portrait_size
            )
            pygame.draw.rect(surface, (40, 40, 40), portrait_rect)
            if u.sprite:
                sprite_scaled = pygame.transform.scale(u.sprite,
                                                       (portrait_size, portrait_size))
                surface.blit(sprite_scaled, portrait_rect.topleft)

            # Full stat names
            stats = [
                ("Weapon Skill", f"{u.ws}+"),
                ("Ballistic Skill", f"{u.bs}+"),
                ("Strength", str(u.strength)),
                ("Toughness", str(u.toughness)),
                ("Wounds", f"{u.current_wounds}/{u.max_wounds}"),
                ("Attacks", str(u.attacks)),
                ("Leadership", str(u.leadership)),
                ("Save", f"{u.save}+"),
            ]
            lines = [f"{lab}: {val}" for lab, val in stats]

            start_y = portrait_rect.bottom + padding
            leftover = SCREEN_HEIGHT - start_y - padding
            spacing = leftover // (len(lines) + 1)
            y = start_y + spacing

            for line in lines:
                lbl = font_stat.render(line, True, (200, 200, 200))
                surface.blit(lbl, (panel_x + padding, y))
                y += spacing

        else:
            # no unit to show
            msg_lbl = font_name.render("No unit selected", True, (200, 200, 200))
            surface.blit(msg_lbl, (panel_x + padding, SCREEN_HEIGHT // 2))
