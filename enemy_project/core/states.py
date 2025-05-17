# core/states.py

import pygame
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, STAT_PANEL_WIDTH
from .unit import Unit
from .ai import enemy_turn
from ..ui.battle_ui import BattleUI


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

    from ui.battle_ui import BattleUI

    def draw(self, surface):
        surface.fill((30, 30, 30))
        # turn indicator...
        BattleUI.draw_grid(surface)
        # overlays and unit.draw() calls here...
        BattleUI.draw_stats_panel(surface, self)
