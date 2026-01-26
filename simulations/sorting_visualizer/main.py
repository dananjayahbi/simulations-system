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

from visualizer import SortingVisualizer


def main():
    """Initialize and run the sorting visualizer."""
    visualizer = SortingVisualizer()
    visualizer.run()


if __name__ == "__main__":
    main()
