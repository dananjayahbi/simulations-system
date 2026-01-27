#!/usr/bin/env python3
"""
Sorting Circles - Radial Circle-Based Sorting Visualization
============================================================
A beautiful pygame visualization showing sorting algorithms using circles
arranged in a radial pattern, where circle size represents value.

Controls:
- SPACE: Toggle pause/play
- R: Reset to shuffled array
- S: Start/Stop recording frames
- 1: Bubble Sort
- 2: Quick Sort
- 3: Merge Sort
- UP/DOWN: Increase/Decrease speed
- ESC: Exit

Features:
- Circles arranged in radial/circular pattern
- Circle radius represents value magnitude
- HSV gradient coloring for beautiful visuals
- Smooth animation with generator-based algorithms
- Visual highlighting of comparisons and swaps
- Frame saving for video creation
"""

import os
import sys
import random
import math
from pathlib import Path

# Add shared directory to path for imports
current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent
shared_dir = root_dir / "shared"
sys.path.insert(0, str(shared_dir))

import pygame
from base_simulation import BaseSimulation


class SortingCircles(BaseSimulation):
    """Radial circle-based sorting visualization."""
    
    def __init__(self):
        super().__init__(width=1200, height=800, fps=60, title="Sorting Circles")
        
        # Array settings
        self.array_size = 50
        self.array = list(range(1, self.array_size + 1))
        random.shuffle(self.array)
        
        # Visualization settings
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.orbit_radius = 280  # Radius of circle arrangement
        self.max_circle_radius = 40
        self.min_circle_radius = 5
        
        # Sorting state
        self.algorithm_name = "Bubble Sort"
        self.sorting_generator = None
        self.is_sorting = False
        self.comparisons = 0
        self.current_compare = []  # Indices being compared
        self.current_swap = []     # Indices being swapped
        
        # Speed control
        self.speed = 5  # Operations per second
        self.delay_counter = 0
        self.frames_per_operation = 60 // self.speed
        
        # Colors
        self.bg_color = (15, 15, 25)
        self.text_color = (220, 220, 220)
        self.compare_color = (255, 255, 255)
        self.swap_color = (255, 200, 50)
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.ui_font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        # Setup recording folder
        self.frames_folder = str(current_dir / "frames")
    
    def get_circle_color(self, value):
        """Generate HSV gradient color based on value."""
        # Map value to hue (0-360)
        hue = (value / self.array_size) * 360
        # Convert HSV to RGB
        h = hue / 60
        c = 200  # Saturation value
        x = c * (1 - abs(h % 2 - 1))
        
        if h < 1:
            r, g, b = c, x, 0
        elif h < 2:
            r, g, b = x, c, 0
        elif h < 3:
            r, g, b = 0, c, x
        elif h < 4:
            r, g, b = 0, x, c
        elif h < 5:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        # Add brightness
        m = 55
        return (int(r + m), int(g + m), int(b + m))
    
    def get_circle_radius(self, value):
        """Calculate circle radius based on value."""
        normalized = value / self.array_size
        return self.min_circle_radius + normalized * (self.max_circle_radius - self.min_circle_radius)
    
    def get_circle_position(self, index):
        """Calculate position of circle in radial arrangement."""
        angle = (index / self.array_size) * 2 * math.pi - math.pi / 2
        x = self.center_x + self.orbit_radius * math.cos(angle)
        y = self.center_y + self.orbit_radius * math.sin(angle)
        return (int(x), int(y))
    
    def reset_array(self):
        """Reset and shuffle the array."""
        self.array = list(range(1, self.array_size + 1))
        random.shuffle(self.array)
        self.is_sorting = False
        self.sorting_generator = None
        self.comparisons = 0
        self.current_compare = []
        self.current_swap = []
    
    def start_sorting(self, algorithm_name):
        """Start a sorting algorithm."""
        self.algorithm_name = algorithm_name
        self.is_sorting = True
        self.comparisons = 0
        self.current_compare = []
        self.current_swap = []
        
        if algorithm_name == "Bubble Sort":
            self.sorting_generator = self.bubble_sort()
        elif algorithm_name == "Quick Sort":
            self.sorting_generator = self.quick_sort(0, len(self.array) - 1)
        elif algorithm_name == "Merge Sort":
            self.sorting_generator = self.merge_sort(0, len(self.array) - 1)
    
    # ==================== SORTING ALGORITHMS ====================
    
    def bubble_sort(self):
        """Bubble sort generator for smooth animation."""
        n = len(self.array)
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                self.current_compare = [j, j + 1]
                self.comparisons += 1
                yield
                
                if self.array[j] > self.array[j + 1]:
                    self.current_swap = [j, j + 1]
                    self.array[j], self.array[j + 1] = self.array[j + 1], self.array[j]
                    swapped = True
                    yield
                    self.current_swap = []
                
                self.current_compare = []
            
            if not swapped:
                break
        
        self.is_sorting = False
    
    def quick_sort(self, low, high):
        """Quick sort generator for smooth animation."""
        if low < high:
            # Partition
            pivot = self.array[high]
            i = low - 1
            
            for j in range(low, high):
                self.current_compare = [j, high]
                self.comparisons += 1
                yield
                
                if self.array[j] < pivot:
                    i += 1
                    self.current_swap = [i, j]
                    self.array[i], self.array[j] = self.array[j], self.array[i]
                    yield
                    self.current_swap = []
                
                self.current_compare = []
            
            self.current_swap = [i + 1, high]
            self.array[i + 1], self.array[high] = self.array[high], self.array[i + 1]
            yield
            self.current_swap = []
            
            pivot_index = i + 1
            
            # Recursively sort left and right
            yield from self.quick_sort(low, pivot_index - 1)
            yield from self.quick_sort(pivot_index + 1, high)
        
        if low == 0 and high == len(self.array) - 1:
            self.is_sorting = False
    
    def merge_sort(self, left, right):
        """Merge sort generator for smooth animation."""
        if left < right:
            mid = (left + right) // 2
            
            # Sort left half
            yield from self.merge_sort(left, mid)
            # Sort right half
            yield from self.merge_sort(mid + 1, right)
            # Merge
            yield from self.merge(left, mid, right)
        
        if left == 0 and right == len(self.array) - 1:
            self.is_sorting = False
    
    def merge(self, left, mid, right):
        """Merge helper for merge sort."""
        left_arr = self.array[left:mid + 1]
        right_arr = self.array[mid + 1:right + 1]
        
        i = j = 0
        k = left
        
        while i < len(left_arr) and j < len(right_arr):
            self.current_compare = [left + i, mid + 1 + j]
            self.comparisons += 1
            yield
            
            if left_arr[i] <= right_arr[j]:
                self.array[k] = left_arr[i]
                i += 1
            else:
                self.array[k] = right_arr[j]
                j += 1
            
            self.current_swap = [k]
            yield
            self.current_swap = []
            self.current_compare = []
            k += 1
        
        while i < len(left_arr):
            self.array[k] = left_arr[i]
            self.current_swap = [k]
            yield
            self.current_swap = []
            i += 1
            k += 1
        
        while j < len(right_arr):
            self.array[k] = right_arr[j]
            self.current_swap = [k]
            yield
            self.current_swap = []
            j += 1
            k += 1
    
    # ==================== PYGAME METHODS ====================
    
    def handle_events(self):
        """Handle keyboard and window events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
                
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                
                elif event.key == pygame.K_r:
                    self.reset_array()
                
                elif event.key == pygame.K_s:
                    if self.recording:
                        self.stop_recording()
                    else:
                        self.start_recording()
                
                elif event.key == pygame.K_1:
                    self.reset_array()
                    self.start_sorting("Bubble Sort")
                
                elif event.key == pygame.K_2:
                    self.reset_array()
                    self.start_sorting("Quick Sort")
                
                elif event.key == pygame.K_3:
                    self.reset_array()
                    self.start_sorting("Merge Sort")
                
                elif event.key == pygame.K_UP:
                    self.speed = min(60, self.speed + 5)
                    self.frames_per_operation = max(1, 60 // self.speed)
                
                elif event.key == pygame.K_DOWN:
                    self.speed = max(1, self.speed - 5)
                    self.frames_per_operation = 60 // self.speed
    
    def update(self):
        """Update simulation state."""
        if self.is_sorting and self.sorting_generator:
            # Speed control with frame delay
            self.delay_counter += 1
            if self.delay_counter >= self.frames_per_operation:
                self.delay_counter = 0
                try:
                    next(self.sorting_generator)
                except StopIteration:
                    self.is_sorting = False
                    self.sorting_generator = None
    
    def draw(self):
        """Draw the visualization."""
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw circles in radial arrangement
        for i, value in enumerate(self.array):
            pos = self.get_circle_position(i)
            radius = self.get_circle_radius(value)
            color = self.get_circle_color(value)
            
            # Draw main circle
            pygame.draw.circle(self.screen, color, pos, int(radius))
            
            # Highlight comparisons
            if i in self.current_compare:
                pygame.draw.circle(self.screen, self.compare_color, pos, int(radius) + 3, 3)
            
            # Highlight swaps
            if i in self.current_swap:
                pygame.draw.circle(self.screen, self.swap_color, pos, int(radius) + 4, 4)
        
        # Draw center circle for aesthetics
        pygame.draw.circle(self.screen, (30, 30, 50), (self.center_x, self.center_y), 30)
        
        # Draw UI overlay
        self.draw_ui()
    
    def draw_ui(self):
        """Draw UI overlay with information and controls."""
        y_offset = 20
        
        # Title
        title_surface = self.title_font.render(self.algorithm_name, True, self.text_color)
        self.screen.blit(title_surface, (20, y_offset))
        y_offset += 50
        
        # Status
        status = "Sorting..." if self.is_sorting else "Paused" if self.paused else "Ready"
        status_color = (100, 255, 100) if self.is_sorting else (255, 200, 100) if self.paused else self.text_color
        status_surface = self.ui_font.render(f"Status: {status}", True, status_color)
        self.screen.blit(status_surface, (20, y_offset))
        y_offset += 30
        
        # Stats
        speed_text = self.ui_font.render(f"Speed: {self.speed} ops/sec", True, self.text_color)
        self.screen.blit(speed_text, (20, y_offset))
        y_offset += 25
        
        comp_text = self.ui_font.render(f"Comparisons: {self.comparisons}", True, self.text_color)
        self.screen.blit(comp_text, (20, y_offset))
        y_offset += 25
        
        # Recording indicator
        if self.recording:
            rec_text = self.ui_font.render(f"● REC - Frame: {self.frame_count}", True, (255, 50, 50))
            self.screen.blit(rec_text, (20, y_offset))
            y_offset += 30
        
        # Controls help
        y_offset = self.height - 180
        controls_title = self.ui_font.render("Controls:", True, self.text_color)
        self.screen.blit(controls_title, (20, y_offset))
        y_offset += 25
        
        controls = [
            "SPACE - Play/Pause",
            "R - Reset & Shuffle",
            "S - Record Frames",
            "1/2/3 - Bubble/Quick/Merge",
            "UP/DOWN - Speed ±5",
            "ESC - Exit"
        ]
        
        for control in controls:
            text = self.small_font.render(control, True, (180, 180, 180))
            self.screen.blit(text, (20, y_offset))
            y_offset += 20


def main():
    """Main entry point."""
    sim = SortingCircles()
    sim.run()


if __name__ == "__main__":
    main()
