#!/usr/bin/env python3
"""
Sorting Lightning - Main Simulation
====================================
Advanced sorting visualization with lightning effects, particles, and animations.
"""

import os
import sys
import random
import argparse
import math
from pathlib import Path
from typing import List, Tuple, Optional

# Add shared directory to path for imports
current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent
shared_dir = root_dir / "shared"
sys.path.insert(0, str(shared_dir))

import pygame
from base_simulation import BaseSimulation


class Particle:
    """Particle for visual effects."""
    def __init__(self, x, y, vx, vy, color, lifetime=30, size=3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Gravity
        self.lifetime -= 1
    
    def is_alive(self):
        return self.lifetime > 0
    
    def draw(self, screen):
        alpha = self.lifetime / self.max_lifetime
        size = int(self.size * alpha)
        if size > 0:
            color = tuple(int(c * alpha) for c in self.color[:3])
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)


class LightningBolt:
    """Lightning effect between two points."""
    def __init__(self, start_pos, end_pos, color, segments=8):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.segments = segments
        self.lifetime = 10
        self.points = self._generate_bolt()
    
    def _generate_bolt(self):
        """Generate jagged lightning path."""
        points = [self.start_pos]
        x1, y1 = self.start_pos
        x2, y2 = self.end_pos
        
        for i in range(1, self.segments):
            t = i / self.segments
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            
            # Add random offset perpendicular to line
            offset = random.randint(-15, 15)
            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                nx = -dy / length
                ny = dx / length
                x += nx * offset
                y += ny * offset
            
            points.append((x, y))
        
        points.append(self.end_pos)
        return points
    
    def update(self):
        self.lifetime -= 1
        # Regenerate occasionally for flickering effect
        if random.random() < 0.3:
            self.points = self._generate_bolt()
    
    def is_alive(self):
        return self.lifetime > 0
    
    def draw(self, screen):
        if len(self.points) < 2:
            return
        
        alpha = self.lifetime / 10
        
        # Draw glow (thicker, dimmer lines)
        glow_color = tuple(int(c * 0.3 * alpha) for c in self.color[:3])
        for i in range(len(self.points) - 1):
            pygame.draw.line(screen, glow_color, 
                           (int(self.points[i][0]), int(self.points[i][1])),
                           (int(self.points[i+1][0]), int(self.points[i+1][1])), 5)
        
        # Draw main bolt
        bolt_color = tuple(int(c * alpha) for c in self.color[:3])
        for i in range(len(self.points) - 1):
            pygame.draw.line(screen, bolt_color,
                           (int(self.points[i][0]), int(self.points[i][1])),
                           (int(self.points[i+1][0]), int(self.points[i+1][1])), 2)


class Bar:
    """Animated bar with smooth transitions."""
    def __init__(self, value, index, total_bars, color):
        self.value = value
        self.target_value = value
        self.index = index
        self.target_index = index
        self.color = color
        self.glow_intensity = 0.0
        self.highlight = False
        self.sorted = False
    
    def set_target(self, value, index):
        self.target_value = value
        self.target_index = index
    
    def update(self, lerp_speed=0.3):
        """Smooth interpolation towards target."""
        self.value += (self.target_value - self.value) * lerp_speed
        self.index += (self.target_index - self.index) * lerp_speed
        
        # Update glow
        if self.highlight:
            self.glow_intensity = min(1.0, self.glow_intensity + 0.1)
        else:
            self.glow_intensity = max(0.0, self.glow_intensity - 0.05)


class ColorTheme:
    """Color theme definitions."""
    THEMES = {
        'neon': {
            'bg': (10, 10, 20),
            'palette': [(255, 0, 255), (0, 255, 255), (255, 255, 0), (0, 255, 0)],
            'highlight': (255, 255, 255),
            'glow': (200, 100, 255)
        },
        'fire': {
            'bg': (20, 10, 5),
            'palette': [(255, 0, 0), (255, 100, 0), (255, 200, 0), (255, 255, 0)],
            'highlight': (255, 255, 200),
            'glow': (255, 150, 0)
        },
        'ice': {
            'bg': (5, 10, 20),
            'palette': [(0, 100, 255), (0, 200, 255), (100, 200, 255), (200, 230, 255)],
            'highlight': (255, 255, 255),
            'glow': (100, 200, 255)
        },
        'cyberpunk': {
            'bg': (10, 0, 20),
            'palette': [(255, 0, 100), (200, 0, 255), (0, 255, 200), (255, 255, 0)],
            'highlight': (255, 0, 255),
            'glow': (255, 0, 200)
        },
        'rainbow': {
            'bg': (15, 15, 25),
            'palette': [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), 
                       (0, 0, 255), (75, 0, 130), (148, 0, 211)],
            'highlight': (255, 255, 255),
            'glow': (200, 100, 255)
        }
    }
    
    @staticmethod
    def get_color(theme_name, value, max_value):
        """Get color for a value based on theme."""
        theme = ColorTheme.THEMES.get(theme_name, ColorTheme.THEMES['neon'])
        palette = theme['palette']
        
        # Map value to palette
        t = value / max_value
        index = t * (len(palette) - 1)
        i1 = int(index)
        i2 = min(i1 + 1, len(palette) - 1)
        blend = index - i1
        
        c1 = palette[i1]
        c2 = palette[i2]
        
        return tuple(int(c1[i] + (c2[i] - c1[i]) * blend) for i in range(3))


class SortingLightning(BaseSimulation):
    """Advanced sorting visualization with effects."""
    
    def __init__(self, width=1400, height=900, fps=60, 
                 algorithm='bubble', bar_count=100, speed=1, 
                 theme='neon', effects_enabled=True):
        super().__init__(width=width, height=height, fps=fps, 
                        title="⚡ Sorting Lightning")
        
        # Settings
        self.algorithm = algorithm
        self.bar_count = bar_count
        self.speed = speed
        self.theme_name = theme
        self.effects_enabled = effects_enabled
        
        # Animation
        self.bars: List[Bar] = []
        self.particles: List[Particle] = []
        self.lightning_bolts: List[LightningBolt] = []
        
        # Algorithm state
        self.array = []
        self.generator = None
        self.comparing_indices = []
        self.sorted_indices = set()
        self.completed = False
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.ui_font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Stats
        self.comparisons = 0
        self.swaps = 0
        self.start_time = 0
        
        # Setup
        self.frames_folder = str(current_dir / "frames")
        self.setup_frames_folder(self.frames_folder)
        self.reset()
    
    def reset(self):
        """Reset simulation to initial state."""
        # Generate random array
        self.array = list(range(1, self.bar_count + 1))
        random.shuffle(self.array)
        
        # Create bar objects
        self.bars = []
        max_value = self.bar_count
        for i, value in enumerate(self.array):
            color = ColorTheme.get_color(self.theme_name, value, max_value)
            bar = Bar(value, i, self.bar_count, color)
            self.bars.append(bar)
        
        # Reset state
        self.generator = self._get_sorting_generator()
        self.comparing_indices = []
        self.sorted_indices = set()
        self.completed = False
        self.particles.clear()
        self.lightning_bolts.clear()
        
        # Reset stats
        self.comparisons = 0
        self.swaps = 0
        self.start_time = pygame.time.get_ticks()
    
    def _get_sorting_generator(self):
        """Get generator for selected algorithm."""
        if self.algorithm == 'bubble':
            return self._bubble_sort()
        elif self.algorithm == 'quick':
            return self._quick_sort(0, len(self.array) - 1)
        elif self.algorithm == 'merge':
            return self._merge_sort(0, len(self.array) - 1)
        elif self.algorithm == 'insertion':
            return self._insertion_sort()
        elif self.algorithm == 'selection':
            return self._selection_sort()
        else:
            return self._bubble_sort()
    
    def _bubble_sort(self):
        """Bubble sort generator."""
        n = len(self.array)
        for i in range(n):
            swapped = False
            for j in range(n - i - 1):
                self.comparisons += 1
                yield [j, j + 1], []
                if self.array[j] > self.array[j + 1]:
                    self.array[j], self.array[j + 1] = self.array[j + 1], self.array[j]
                    self.swaps += 1
                    yield [j, j + 1], [j, j + 1]
                    swapped = True
            if not swapped:
                break
            self.sorted_indices.add(n - i - 1)
        
        for i in range(n):
            self.sorted_indices.add(i)
            yield [], []
    
    def _insertion_sort(self):
        """Insertion sort generator."""
        for i in range(1, len(self.array)):
            key = self.array[i]
            j = i - 1
            while j >= 0:
                self.comparisons += 1
                yield [j, j + 1], []
                if self.array[j] > key:
                    self.array[j + 1] = self.array[j]
                    self.swaps += 1
                    yield [j, j + 1], [j, j + 1]
                    j -= 1
                else:
                    break
            self.array[j + 1] = key
        
        for i in range(len(self.array)):
            self.sorted_indices.add(i)
            yield [], []
    
    def _selection_sort(self):
        """Selection sort generator."""
        n = len(self.array)
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                self.comparisons += 1
                yield [min_idx, j], []
                if self.array[j] < self.array[min_idx]:
                    min_idx = j
            
            if min_idx != i:
                self.array[i], self.array[min_idx] = self.array[min_idx], self.array[i]
                self.swaps += 1
                yield [i, min_idx], [i, min_idx]
            
            self.sorted_indices.add(i)
        
        yield [], []
    
    def _quick_sort(self, low, high):
        """Quick sort generator."""
        if low < high:
            pivot_idx = yield from self._partition(low, high)
            yield from self._quick_sort(low, pivot_idx - 1)
            yield from self._quick_sort(pivot_idx + 1, high)
        
        if low == 0 and high == len(self.array) - 1:
            for i in range(len(self.array)):
                self.sorted_indices.add(i)
                yield [], []
    
    def _partition(self, low, high):
        """Partition for quick sort."""
        pivot = self.array[high]
        i = low - 1
        
        for j in range(low, high):
            self.comparisons += 1
            yield [j, high], []
            if self.array[j] < pivot:
                i += 1
                if i != j:
                    self.array[i], self.array[j] = self.array[j], self.array[i]
                    self.swaps += 1
                    yield [i, j], [i, j]
        
        if i + 1 != high:
            self.array[i + 1], self.array[high] = self.array[high], self.array[i + 1]
            self.swaps += 1
            yield [i + 1, high], [i + 1, high]
        
        return i + 1
    
    def _merge_sort(self, left, right):
        """Merge sort generator."""
        if left < right:
            mid = (left + right) // 2
            yield from self._merge_sort(left, mid)
            yield from self._merge_sort(mid + 1, right)
            yield from self._merge(left, mid, right)
        
        if left == 0 and right == len(self.array) - 1:
            for i in range(len(self.array)):
                self.sorted_indices.add(i)
                yield [], []
    
    def _merge(self, left, mid, right):
        """Merge for merge sort."""
        left_arr = self.array[left:mid + 1]
        right_arr = self.array[mid + 1:right + 1]
        
        i = j = 0
        k = left
        
        while i < len(left_arr) and j < len(right_arr):
            self.comparisons += 1
            yield [left + i, mid + 1 + j], []
            if left_arr[i] <= right_arr[j]:
                self.array[k] = left_arr[i]
                i += 1
            else:
                self.array[k] = right_arr[j]
                j += 1
            self.swaps += 1
            yield [k], [k]
            k += 1
        
        while i < len(left_arr):
            self.array[k] = left_arr[i]
            i += 1
            k += 1
            yield [k - 1], [k - 1]
        
        while j < len(right_arr):
            self.array[k] = right_arr[j]
            j += 1
            k += 1
            yield [k - 1], [k - 1]
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                
                elif event.key == pygame.K_r:
                    self.reset()
                
                elif event.key == pygame.K_s:
                    if self.recording:
                        self.stop_recording()
                        print(f"Recording stopped. {self.frame_count} frames saved.")
                    else:
                        self.start_recording()
                        print("Recording started...")
                
                # Theme switching
                elif event.key == pygame.K_1:
                    self.theme_name = 'neon'
                    self.reset()
                elif event.key == pygame.K_2:
                    self.theme_name = 'fire'
                    self.reset()
                elif event.key == pygame.K_3:
                    self.theme_name = 'ice'
                    self.reset()
                elif event.key == pygame.K_4:
                    self.theme_name = 'cyberpunk'
                    self.reset()
                elif event.key == pygame.K_5:
                    self.theme_name = 'rainbow'
                    self.reset()
                
                # Effects toggle
                elif event.key == pygame.K_e:
                    self.effects_enabled = not self.effects_enabled
    
    def update(self):
        """Update simulation state."""
        if self.completed or not self.generator:
            return
        
        # Clear highlights
        for bar in self.bars:
            bar.highlight = False
        
        # Advance algorithm
        try:
            for _ in range(self.speed):
                comparing, swapping = next(self.generator)
                self.comparing_indices = comparing
                
                # Update bar targets
                for i, bar in enumerate(self.bars):
                    bar.set_target(self.array[i], i)
                    bar.sorted = i in self.sorted_indices
                
                # Highlight comparing bars
                for idx in comparing:
                    if idx < len(self.bars):
                        self.bars[idx].highlight = True
                
                # Create effects for swaps
                if self.effects_enabled and swapping:
                    self._create_swap_effects(swapping)
        
        except StopIteration:
            self.completed = True
            if self.effects_enabled:
                self._create_completion_effects()
        
        # Update bars
        for bar in self.bars:
            bar.update(lerp_speed=0.3)
        
        # Update particles
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
        
        # Update lightning
        self.lightning_bolts = [b for b in self.lightning_bolts if b.is_alive()]
        for bolt in self.lightning_bolts:
            bolt.update()
    
    def _create_swap_effects(self, indices):
        """Create visual effects for swaps."""
        if len(indices) < 2:
            return
        
        theme = ColorTheme.THEMES[self.theme_name]
        glow_color = theme['glow']
        
        for i in range(len(indices) - 1):
            idx1, idx2 = indices[i], indices[i + 1]
            if idx1 >= len(self.bars) or idx2 >= len(self.bars):
                continue
            
            bar1, bar2 = self.bars[idx1], self.bars[idx2]
            
            # Calculate positions
            bar_width = self.width / self.bar_count
            x1 = idx1 * bar_width + bar_width / 2
            x2 = idx2 * bar_width + bar_width / 2
            y1 = self.height - (bar1.value / self.bar_count) * (self.height - 100)
            y2 = self.height - (bar2.value / self.bar_count) * (self.height - 100)
            
            # Create lightning bolt
            bolt = LightningBolt((x1, y1), (x2, y2), glow_color)
            self.lightning_bolts.append(bolt)
            
            # Create particles
            for _ in range(5):
                vx = random.uniform(-2, 2)
                vy = random.uniform(-5, -2)
                particle = Particle(x1, y1, vx, vy, glow_color, lifetime=30, size=4)
                self.particles.append(particle)
                
                particle = Particle(x2, y2, vx, vy, glow_color, lifetime=30, size=4)
                self.particles.append(particle)
    
    def _create_completion_effects(self):
        """Create celebration effects when sorting completes."""
        theme = ColorTheme.THEMES[self.theme_name]
        
        for i in range(self.bar_count):
            bar = self.bars[i]
            bar_width = self.width / self.bar_count
            x = i * bar_width + bar_width / 2
            y = self.height - (bar.value / self.bar_count) * (self.height - 100)
            
            # Create burst of particles
            for _ in range(10):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 6)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                color = ColorTheme.get_color(self.theme_name, bar.value, self.bar_count)
                particle = Particle(x, y, vx, vy, color, lifetime=60, size=5)
                self.particles.append(particle)
    
    def draw(self):
        """Draw the simulation."""
        # Background
        theme = ColorTheme.THEMES[self.theme_name]
        self.screen.fill(theme['bg'])
        
        # Draw bars
        bar_width = self.width / self.bar_count
        
        for i, bar in enumerate(self.bars):
            x = bar.index * bar_width
            height = (bar.value / self.bar_count) * (self.height - 100)
            y = self.height - height
            
            color = bar.color
            
            # Sorted bars get a highlight
            if bar.sorted:
                color = tuple(min(255, c + 50) for c in color)
            
            # Draw glow for highlighted bars
            if bar.glow_intensity > 0 and self.effects_enabled:
                glow_color = theme['glow']
                glow_alpha = int(bar.glow_intensity * 100)
                glow_rect = pygame.Rect(x - 2, y - 2, bar_width + 4, height + 4)
                
                # Draw multiple glow layers
                for j in range(3):
                    offset = j * 2
                    alpha = glow_alpha // (j + 1)
                    glow_surface = pygame.Surface((bar_width + offset * 2, height + offset * 2), 
                                                 pygame.SRCALPHA)
                    glow_color_alpha = (*glow_color, alpha)
                    pygame.draw.rect(glow_surface, glow_color_alpha, 
                                   glow_surface.get_rect(), border_radius=3)
                    self.screen.blit(glow_surface, (x - offset, y - offset))
            
            # Draw bar
            bar_rect = pygame.Rect(x, y, bar_width - 1, height)
            pygame.draw.rect(self.screen, color, bar_rect, border_radius=2)
            
            # Highlight border for comparing bars
            if bar.highlight:
                pygame.draw.rect(self.screen, theme['highlight'], bar_rect, 2, border_radius=2)
        
        # Draw lightning bolts
        for bolt in self.lightning_bolts:
            bolt.draw(self.screen)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw UI
        self._draw_ui()
    
    def _draw_ui(self):
        """Draw UI elements."""
        theme = ColorTheme.THEMES[self.theme_name]
        
        # Title
        title_text = f"⚡ {self.algorithm.upper()} SORT"
        title_surface = self.title_font.render(title_text, True, theme['highlight'])
        self.screen.blit(title_surface, (20, 20))
        
        # Stats
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
        stats = [
            f"Comparisons: {self.comparisons}",
            f"Swaps: {self.swaps}",
            f"Time: {elapsed:.1f}s",
            f"Theme: {self.theme_name.title()}",
            f"Effects: {'ON' if self.effects_enabled else 'OFF'}"
        ]
        
        y_offset = 80
        for stat in stats:
            stat_surface = self.ui_font.render(stat, True, (200, 200, 200))
            self.screen.blit(stat_surface, (20, y_offset))
            y_offset += 30
        
        # Controls
        controls = [
            "SPACE: Pause | R: Reset | S: Record",
            "1-5: Themes | E: Toggle Effects | ESC: Exit"
        ]
        
        y_offset = self.height - 60
        for control in controls:
            control_surface = self.small_font.render(control, True, (150, 150, 150))
            self.screen.blit(control_surface, (20, y_offset))
            y_offset += 25
        
        # Recording indicator
        if self.recording:
            rec_text = self.ui_font.render(f"● REC {self.frame_count}", True, (255, 0, 0))
            self.screen.blit(rec_text, (self.width - 150, 20))
        
        # Pause indicator
        if self.paused:
            pause_text = self.title_font.render("⏸ PAUSED", True, (255, 255, 0))
            text_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
            
            # Draw semi-transparent background
            bg_surface = pygame.Surface((text_rect.width + 40, text_rect.height + 20), 
                                       pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            self.screen.blit(bg_surface, (text_rect.x - 20, text_rect.y - 10))
            
            self.screen.blit(pause_text, text_rect)
        
        # Completion message
        if self.completed:
            complete_text = self.title_font.render("✓ SORTED!", True, (0, 255, 0))
            text_rect = complete_text.get_rect(center=(self.width // 2, 50))
            
            # Draw semi-transparent background
            bg_surface = pygame.Surface((text_rect.width + 40, text_rect.height + 20), 
                                       pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            self.screen.blit(bg_surface, (text_rect.x - 20, text_rect.y - 10))
            
            self.screen.blit(complete_text, text_rect)


def main():
    """Main entry point for standalone execution."""
    parser = argparse.ArgumentParser(description="Sorting Lightning Visualization")
    parser.add_argument('--width', type=int, default=1400, help='Window width')
    parser.add_argument('--height', type=int, default=900, help='Window height')
    parser.add_argument('--fps', type=int, default=60, help='Frames per second')
    parser.add_argument('--algorithm', type=str, default='bubble', 
                       choices=['bubble', 'quick', 'merge', 'insertion', 'selection'],
                       help='Sorting algorithm')
    parser.add_argument('--bars', type=int, default=100, help='Number of bars')
    parser.add_argument('--speed', type=int, default=1, help='Speed multiplier')
    parser.add_argument('--theme', type=str, default='neon',
                       choices=['neon', 'fire', 'ice', 'cyberpunk', 'rainbow'],
                       help='Visual theme')
    parser.add_argument('--no-effects', action='store_true', help='Disable effects')
    parser.add_argument('--record', action='store_true', help='Start recording immediately')
    
    args = parser.parse_args()
    
    sim = SortingLightning(
        width=args.width,
        height=args.height,
        fps=args.fps,
        algorithm=args.algorithm,
        bar_count=args.bars,
        speed=args.speed,
        theme=args.theme,
        effects_enabled=not args.no_effects
    )
    
    if args.record:
        sim.start_recording()
    
    sim.run()


if __name__ == "__main__":
    main()
