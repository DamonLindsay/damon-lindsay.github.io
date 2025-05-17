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

# How many tiles fit in our window (derived)
VIEWPORT_TILES_X = SCREEN_WIDTH // TILE_SIZE  # e.g. 20
VIEWPORT_TILES_Y = SCREEN_HEIGHT // TILE_SIZE  # e.g. 11

# Now explicitly set your map dimensions — make these larger than viewport
MAP_TILES_X = 60  # e.g. 60 tiles wide
MAP_TILES_Y = 40  # e.g. 40 tiles tall

# ── UI PANEL ───────────────────────────────────────────────────────────────────

# Width of the right-hand stats panel
STAT_PANEL_WIDTH = 300

# Camera panning
PAN_SPEED = 300  # pixels per second
PAN_MARGIN = 50  # pixels from edge to start panning
