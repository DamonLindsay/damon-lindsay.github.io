# core/ai.py

from .unit import Unit
from .settings import GRID_WIDTH, GRID_HEIGHT
from .combat import to_hit_roll, wound_roll, saving_throw


def move_toward(attacker: Unit, target: Unit, units: list[Unit]):
    """
    Move attacker one tile toward target if that tile is free.
    """
    ex, ey = attacker.position
    tx, ty = target.position
    dx, dy = tx - ex, ty - ey

    # decide step direction
    step_x = 1 if dx > 0 else -1 if dx < 0 else 0
    step_y = 1 if dy > 0 else -1 if dy < 0 else 0

    # prioritise larger delta
    if abs(dx) >= abs(dy):
        new_pos = (ex + step_x, ey)
    else:
        new_pos = (ex, ey + step_y)

    # check bounds & occupancy
    if 0 <= new_pos[0] < GRID_WIDTH and 0 <= new_pos[1] < GRID_HEIGHT:
        if not any(u.position == new_pos for u in units):
            attacker.position = new_pos


def enemy_turn(units: list[Unit]):
    """
    Perform the entire enemy phase:
    1) For each enemy unit, move toward nearest player unit.
    2) If in attack_range, attack that unit.
    Removes dead models from `units` list.
    """
    # collect lists
    player_units = [u for u in units if u.team == "player"]
    enemy_units = [u for u in units if u.team == "enemy"]

    for enemy in enemy_units:
        if not player_units:
            return

        # find nearest player
        target = min(
            player_units,
            key=lambda pu: abs(pu.position[0] - enemy.position[0]) +
                           abs(pu.position[1] - enemy.position[1])
        )

        # move phase
        dist = abs(enemy.position[0] - target.position[0]) + abs(enemy.position[1] - target.position[1])
        if dist > enemy.attack_range:
            move_toward(enemy, target, units)
            dist -= 1  # update distance after move

        # attack phase
        if dist <= enemy.attack_range:
            enemy.attack(target)
            if not target.is_alive():
                units.remove(target)
                player_units.remove(target)
