# core/combat.py

import random

def roll_d6():
    return random.randint(1, 6)

def to_hit_roll(weapon_skill):
    """Return True if a D6 roll ≥ WS (for melee) or BS (for shooting)."""
    return roll_d6() >= weapon_skill

def wound_roll(strength, toughness):
    """
    Compute the wound threshold:
      - 2+ if S ≥ 2×T
      - 3+ if S > T
      - 4+ if S == T
      - 5+ if S < T
      - 6+ if 2×S ≤ T
    Return True if roll ≥ threshold.
    """
    if strength >= 2 * toughness:
        needed = 2
    elif strength > toughness:
        needed = 3
    elif strength == toughness:
        needed = 4
    elif 2 * strength <= toughness:
        needed = 6
    else:
        needed = 5
    return roll_d6() >= needed

def saving_throw(armour_save):
    """Return True if D6 roll ≥ save value."""
    return roll_d6() >= armour_save
