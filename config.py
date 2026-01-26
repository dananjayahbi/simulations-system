# config.py - Configuration settings for the sorting visualizer

# Window settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
FPS = 60

# Bar settings
NUM_BARS = 200
BAR_WIDTH = WINDOW_WIDTH // NUM_BARS

# Colors
BACKGROUND_COLOR = (20, 20, 20)  # Dark grey

# Frame saving
FRAMES_FOLDER = "frames"
SAVE_FRAMES = True

# Speed control settings
DEFAULT_SPEED = 1  # Steps per frame
MIN_SPEED = 1
MAX_SPEED = 50
SPEED_INCREMENT = 1

# Sorting algorithms available
ALGORITHMS = ["Bubble Sort", "Quick Sort", "Merge Sort"]
