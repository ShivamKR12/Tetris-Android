import os
import sys

# Grid & Display Dimensions
WIDTH, HEIGHT = 10, 20
TILE = 45
GAME_RESOLUTION = WIDTH * TILE, HEIGHT * TILE
RESOLUTION = 750, 940
FPS = 60

# Tetromino Shape Offsets
FIGURES_POS = [
    [(-1, 0), (-2, 0), (0, 0), (1, 0)],
    [(0, -1), (-1, -1), (-1, 0), (0, 0)],
    [(-1, 0), (-1, 1), (0, 0), (0, -1)],
    [(0, 0), (-1, 0), (0, 1), (-1, -1)],
    [(0, 0), (0, -1), (0, 1), (-1, -1)],
    [(0, 0), (0, -1), (0, 1), (1, -1)],
    [(0, 0), (0, -1), (0, 1), (-1, 0)]
]

SCORES_TABLE = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and Buildozer / Android."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)
