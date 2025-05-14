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
