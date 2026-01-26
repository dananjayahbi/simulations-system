#!/usr/bin/env python3
# main.py - Entry point for Sorting Algorithm Visualizer

"""
Sorting Algorithm Visualizer
============================
A pygame-based visualization of popular sorting algorithms.

Controls:
- UP/DOWN: Select algorithm in menu
- SPACE: Start sorting
- R: Scramble/reset the array
- +/-: Adjust speed
- M: Return to menu
- 1/2/3: Quick select Bubble/Quick/Merge Sort
- ESC: Quit (or return to menu)

Features:
- Rainbow gradient coloring (HSV spectrum)
- Real-time visualization at 60 FPS
- Speed control (1x to 50x)
- Frame saving for video rendering (saved to frames/ folder)
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from visualizer import SortingVisualizer


def load_runtime_settings():
    """Load settings from control panel if available."""
    settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runtime_settings.py")
    settings = {}
    
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                exec(f.read(), settings)
            # Clean up the settings file after reading
            os.remove(settings_file)
        except Exception:
            pass
    
    return settings


def main():
    """Initialize and run the sorting visualizer."""
    settings = load_runtime_settings()
    visualizer = SortingVisualizer(settings)
    visualizer.run()


if __name__ == "__main__":
    main()
