import os

# Project title
TITLE = "Enemy"

# Window size
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Frame rate cap
FPS = 60

# Asset directories (relative to this file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# ── GRID SETTINGS ──────────────────────────────────────────────────────────────

# Size of each tile in pixels
TILE_SIZE = 64

# Number of tiles horizontally and vertically
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# ── UI PANEL ───────────────────────────────────────────────────────────────────

# Width of the right-hand stats panel
STAT_PANEL_WIDTH = 300

# Camera panning
PAN_SPEED = 300  # pixels per second
PAN_MARGIN = 50  # pixels from edge to start panning
