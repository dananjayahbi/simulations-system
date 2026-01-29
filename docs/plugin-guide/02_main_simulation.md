# Plugin Development Guide - Part 2: Main Simulation

## 📚 Table of Contents
- [Overview](#overview)
- [Using BaseSimulation](#using-basesimulation)
- [Required Methods](#required-methods)
- [Path Management](#path-management)
- [Complete main.py Template](#complete-mainpy-template)
- [Best Practices](#best-practices)

---

## Overview

The `main.py` file is the heart of your plugin. It contains the pygame-based visualization logic that runs in its own window.

### Key Concepts

1. **Inherit from BaseSimulation**: Always extend the `BaseSimulation` class
2. **Implement Required Methods**: `handle_events()`, `update()`, `draw()`
3. **Use Relative Paths**: Never hardcode paths
4. **Command-Line Arguments**: Support standalone execution
5. **Clean Display**: Minimal UI in the simulation window

---

## Using BaseSimulation

The `BaseSimulation` class provides:
- Pygame initialization
- Main game loop
- Recording infrastructure
- Frame saving logic
- Pause/play functionality

### Importing BaseSimulation

```python
import sys
from pathlib import Path

# Add shared directory to path
current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent
shared_dir = root_dir / "shared"
sys.path.insert(0, str(shared_dir))

from base_simulation import BaseSimulation
```

**⚠️ CRITICAL:** This path setup works for both `simulations/` and `external-addons-dev/` locations.

---

## Required Methods

Your simulation class must implement these three methods:

### 1. `handle_events()`

Processes pygame events (keyboard, mouse, window close).

```python
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
                else:
                    self.start_recording()
```

**Standard Keyboard Controls:**
- `ESC`: Exit simulation
- `SPACE`: Pause/Resume
- `R`: Reset simulation
- `S`: Toggle recording

### 2. `update()`

Updates simulation state each frame (only when not paused).

```python
def update(self):
    """Update simulation state."""
    if self.paused:
        return
    
    # Update your simulation logic here
    # Example:
    for particle in self.particles:
        particle.update()
        
    # Remove dead objects
    self.particles = [p for p in self.particles if p.is_alive()]
```

### 3. `draw()`

Renders the simulation to the screen.

```python
def draw(self):
    """Draw the simulation."""
    # Clear screen
    self.screen.fill(self.bg_color)
    
    # Draw your visualization
    for particle in self.particles:
        particle.draw(self.screen)
    
    # Draw minimal UI
    if self.recording:
        rec_text = self.ui_font.render(f"● REC {self.frame_count}", True, (255, 0, 0))
        self.screen.blit(rec_text, (self.width - 150, 10))
    
    if self.paused:
        pause_text = self.title_font.render("⏸ PAUSED", True, (255, 255, 0))
        text_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(pause_text, text_rect)
```

**UI Guidelines:**
- ❌ NO buttons, sliders, text inputs in simulation window
- ✅ Only minimal status indicators (recording, pause, frame count)
- ✅ Keep UI in top corners or center overlay

---

## Path Management

### ⚠️ CRITICAL: Always Use Relative Paths

**❌ WRONG:**
```python
self.frames_folder = "C:/Users/you/loops/frames"  # Hardcoded path
self.frames_folder = "/home/user/loops/frames"    # Hardcoded path
```

**✅ CORRECT:**
```python
from pathlib import Path

current_dir = Path(__file__).parent
self.frames_folder = str(current_dir / "frames")
```

### Path Template

Use this at the top of your `main.py`:

```python
from pathlib import Path

# Get current directory (works everywhere)
current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent
shared_dir = root_dir / "shared"

# Add shared to Python path for imports
sys.path.insert(0, str(shared_dir))
```

---

## Complete main.py Template

```python
#!/usr/bin/env python3
"""
[Plugin Name] - Main Simulation
================================
Description of your simulation.
"""

import os
import sys
import random
import argparse
from pathlib import Path

# Setup paths
current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent
shared_dir = root_dir / "shared"
sys.path.insert(0, str(shared_dir))

import pygame
from base_simulation import BaseSimulation


class YourSimulation(BaseSimulation):
    """Main simulation class."""
    
    def __init__(self, width=1200, height=800, fps=60, **kwargs):
        """
        Initialize the simulation.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
            fps: Target frames per second
            **kwargs: Additional custom parameters
        """
        super().__init__(
            width=width, 
            height=height, 
            fps=fps, 
            title="Your Plugin Name"
        )
        
        # Custom settings
        self.bg_color = (20, 20, 30)
        self.custom_setting = kwargs.get('custom_setting', 'default')
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.ui_font = pygame.font.SysFont('Arial', 20)
        
        # Setup frames folder
        self.frames_folder = str(current_dir / "frames")
        self.setup_frames_folder(self.frames_folder)
        
        # Initialize simulation state
        self.reset()
    
    def reset(self):
        """Reset simulation to initial state."""
        self.entities = []
        self.frame_count = 0
        # Initialize your data structures here
    
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
    
    def update(self):
        """Update simulation state."""
        if self.paused:
            return
        
        # Update your simulation logic here
        pass
    
    def draw(self):
        """Draw the simulation."""
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw your visualization here
        
        # Draw minimal UI
        if self.recording:
            rec_text = self.ui_font.render(
                f"● REC {self.frame_count}", 
                True, 
                (255, 0, 0)
            )
            self.screen.blit(rec_text, (self.width - 150, 10))
        
        if self.paused:
            pause_text = self.title_font.render("⏸ PAUSED", True, (255, 255, 0))
            text_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
            
            # Semi-transparent background
            bg_surface = pygame.Surface(
                (text_rect.width + 40, text_rect.height + 20), 
                pygame.SRCALPHA
            )
            bg_surface.fill((0, 0, 0, 180))
            self.screen.blit(bg_surface, (text_rect.x - 20, text_rect.y - 10))
            
            self.screen.blit(pause_text, text_rect)


def main():
    """Main entry point for standalone execution."""
    parser = argparse.ArgumentParser(description="Your Plugin Name")
    parser.add_argument('--width', type=int, default=1200, help='Window width')
    parser.add_argument('--height', type=int, default=800, help='Window height')
    parser.add_argument('--fps', type=int, default=60, help='Frames per second')
    parser.add_argument('--record', action='store_true', help='Start recording immediately')
    
    # Add your custom arguments
    parser.add_argument('--custom', type=str, default='default', help='Custom setting')
    
    args = parser.parse_args()
    
    sim = YourSimulation(
        width=args.width,
        height=args.height,
        fps=args.fps,
        custom_setting=args.custom
    )
    
    if args.record:
        sim.start_recording()
    
    sim.run()


if __name__ == "__main__":
    main()
```

---

## Best Practices

### 1. Frame Saving

The `BaseSimulation` class handles frame saving automatically when recording is active. Just make sure to call `super().__init__()` and set up the frames folder:

```python
self.frames_folder = str(current_dir / "frames")
self.setup_frames_folder(self.frames_folder)
```

**Frame Naming Convention:**
- Must be: `frame_XXXXXX.png` (6 digits, zero-padded)
- Example: `frame_000001.png`, `frame_000042.png`, `frame_001337.png`

### 2. Performance Optimization

```python
# ✅ Good: Reuse surfaces
self.background = pygame.Surface((width, height))
self.background.fill(bg_color)

# ❌ Bad: Create new surfaces every frame
def draw(self):
    bg = pygame.Surface((self.width, self.height))  # Slow!
    bg.fill(self.bg_color)
```

### 3. State Management

Keep your simulation state organized:

```python
def __init__(self, ...):
    super().__init__(...)
    
    # Settings (immutable after init)
    self.settings = {
        'speed': 1.0,
        'count': 100,
        'theme': 'dark'
    }
    
    # Dynamic state (changes during simulation)
    self.state = {
        'entities': [],
        'score': 0,
        'time_elapsed': 0
    }
```

### 4. Clean Exit

Always handle graceful shutdown:

```python
def cleanup(self):
    """Cleanup resources before exit."""
    # Close files
    # Stop threads
    # Release resources
    pass

def handle_events(self):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            self.cleanup()
            self.running = False
```

### 5. Error Handling

```python
def update(self):
    """Update simulation state."""
    try:
        # Your update logic
        pass
    except Exception as e:
        print(f"Error in update: {e}")
        # Optionally: self.paused = True
```

---

## Common Patterns

### Pattern 1: Particle System

```python
class Particle:
    def __init__(self, x, y, vx, vy, lifetime=60):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
    
    def is_alive(self):
        return self.lifetime > 0
    
    def draw(self, screen):
        alpha = self.lifetime / self.max_lifetime
        color = (255, int(255 * alpha), 0)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 3)

# In your simulation:
def update(self):
    for particle in self.particles:
        particle.update()
    
    self.particles = [p for p in self.particles if p.is_alive()]
```

### Pattern 2: Smooth Animation

```python
class AnimatedValue:
    def __init__(self, initial=0, speed=0.1):
        self.current = initial
        self.target = initial
        self.speed = speed
    
    def set_target(self, target):
        self.target = target
    
    def update(self):
        self.current += (self.target - self.current) * self.speed
    
    def get(self):
        return self.current

# Usage:
self.scale = AnimatedValue(1.0, 0.05)
self.scale.set_target(1.5)  # Smoothly scale to 1.5

# In update():
self.scale.update()
current_scale = self.scale.get()
```

### Pattern 3: Generator-Based Algorithms

Perfect for step-by-step visualizations:

```python
def bubble_sort(self, array):
    """Generator that yields each step of bubble sort."""
    n = len(array)
    for i in range(n):
        for j in range(n - i - 1):
            # Yield state for comparison
            yield {'action': 'compare', 'indices': [j, j+1]}
            
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]
                # Yield state for swap
                yield {'action': 'swap', 'indices': [j, j+1]}

# In your simulation:
def reset(self):
    self.algorithm_generator = self.bubble_sort(self.array)

def update(self):
    try:
        state = next(self.algorithm_generator)
        # Update visualization based on state
        if state['action'] == 'swap':
            self.highlight_indices = state['indices']
    except StopIteration:
        self.completed = True
```

---

## Testing Your Simulation

### Standalone Testing

```bash
cd your_plugin_directory
python main.py --width 800 --height 600 --fps 30
```

### With Recording

```bash
python main.py --record
```

### With Custom Arguments

```bash
python main.py --custom my_value --width 1920 --height 1080
```

---

## Next Steps

Your simulation is now functional! Next:

- **Part 3: Control Panel** - Create the GUI to configure and launch your simulation
- **Part 4: Video Generation** - Integrate video recording via API
- **Part 5: Common Pitfalls** - Avoid common mistakes

---

## Quick Reference

**Must-Have Elements:**
- [ ] Inherit from `BaseSimulation`
- [ ] Implement `handle_events()`, `update()`, `draw()`
- [ ] Use relative paths for frames folder
- [ ] Support command-line arguments
- [ ] Handle standard keyboard shortcuts (ESC, SPACE, R, S)
- [ ] Display minimal UI only

**Ready for Part 3?** → [Control Panel Development](./03_control_panel.md)
