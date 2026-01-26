# config.py - Configuration settings for the sorting visualizer
import os

# Get the directory where this config file is located
SIMULATION_DIR = os.path.dirname(os.path.abspath(__file__))

# Window settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
FPS = 60

# Bar settings
NUM_BARS = 200
BAR_WIDTH = WINDOW_WIDTH // NUM_BARS

# Colors
BACKGROUND_COLOR = (20, 20, 20)  # Dark grey

# Frame saving - isolated to this simulation's folder
FRAMES_FOLDER = os.path.join(SIMULATION_DIR, "frames")
SAVE_FRAMES = True

# Speed control settings
DEFAULT_SPEED = 1  # Steps per frame
MIN_SPEED = 1
MAX_SPEED = 50
SPEED_INCREMENT = 1

# Sorting algorithms available
ALGORITHMS = ["Bubble Sort", "Quick Sort", "Merge Sort"]
