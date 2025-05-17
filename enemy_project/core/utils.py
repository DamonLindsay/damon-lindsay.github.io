# core/utils.py

import os
import json
from .settings import BASE_DIR


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    """Return the Manhattan distance between two grid coordinates."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min_val and max_val."""
    return max(min_val, min(max_val, value))


def load_json(path_parts: list[str]) -> dict:
    """
    Load a JSON file. path_parts is a list of path segments relative to BASE_DIR.
    E.g. ['data','factions','space_marines.json'].
    """
    path = os.path.join(BASE_DIR, *path_parts)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
