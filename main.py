#!/usr/bin/env python3
# main.py - Entry point for Sorting Algorithm Visualizer

"""
Sorting Algorithm Visualizer
============================
A pygame-based visualization of popular sorting algorithms.

Controls:
- SPACE: Start sorting
- R: Scramble/reset the array
- 1: Select Bubble Sort
- 2: Select Quick Sort
- 3: Select Merge Sort
- ESC: Quit

Features:
- Rainbow gradient coloring (HSV spectrum)
- Real-time visualization at 60 FPS
- Frame saving for video rendering
"""

from visualizer import SortingVisualizer


def main():
    """Initialize and run the sorting visualizer."""
    visualizer = SortingVisualizer()
    visualizer.run()


if __name__ == "__main__":
    main()
