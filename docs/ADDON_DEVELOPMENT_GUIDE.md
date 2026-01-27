# Loops Add-on Development Guide

## Introduction

This guide explains how to create, package, and distribute simulation add-ons for the Loops Visualization System. Whether you're an AI agent generating simulations or a developer creating custom visualizations, this document provides everything needed to build compatible add-ons.

---

## Quick Start

### Minimal Add-on Structure

```
my_simulation/
├── simulation.json     ← Required: Metadata
├── main.py             ← Required: Entry point
└── __init__.py         ← Required: Package init
```

### Example simulation.json

```json
{
    "id": "my_simulation",
    "name": "My Simulation",
    "description": "A brief description of what this simulation does",
    "icon": "🎨",
    "color": "#6366f1",
    "version": "1.0.0",
    "author": "Your Name",
    "min_loops_version": "1.0.0",
    "tags": ["visualization", "demo"],
    "requires_pygame": true
}
```

### Example main.py

```python
#!/usr/bin/env python3
"""
My Simulation - Entry point
"""

import pygame
import sys
from pathlib import Path

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from shared.base_simulation import BaseSimulation

class MySimulation(BaseSimulation):
    """My custom simulation."""
    
    def __init__(self):
        super().__init__(
            width=1200,
            height=800,
            title="My Simulation",
            fps=60
        )
        # Initialize your simulation state here
        
    def update(self):
        """Update simulation state each frame."""
        pass
        
    def draw(self):
        """Draw the current frame."""
        self.screen.fill((0, 0, 0))
        # Draw your simulation here
        
    def handle_event(self, event):
        """Handle pygame events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False

def main():
    sim = MySimulation()
    sim.run()

if __name__ == "__main__":
    main()
```

---

## Complete Add-on Structure

### Full Directory Layout

```
simulation_name/
│
├── simulation.json          ← REQUIRED: Metadata & configuration
├── main.py                  ← REQUIRED: Main entry point
├── __init__.py              ← REQUIRED: Package initializer
│
├── control_panel.py         ← OPTIONAL: Tkinter-based control panel GUI
├── config.py                ← OPTIONAL: Configuration constants
├── requirements.txt         ← OPTIONAL: Additional Python dependencies
├── README.md                ← OPTIONAL: Documentation
│
├── modules/                 ← OPTIONAL: Additional Python modules
│   ├── __init__.py
│   ├── renderer.py
│   └── physics.py
│
└── assets/                  ← OPTIONAL: Static resources
    ├── images/
    │   └── sprite.png
    ├── sounds/
    │   └── effect.wav
    └── data/
        └── config.yaml
```

---

## Required Files

### 1. simulation.json

The metadata file that describes your add-on:

```json
{
    "id": "unique_simulation_id",
    "name": "Human Readable Name",
    "description": "Detailed description of the simulation",
    "icon": "🎮",
    "color": "#4CAF50",
    "version": "1.0.0",
    "author": "Author Name",
    "license": "MIT",
    "homepage": "https://github.com/user/repo",
    "min_loops_version": "1.0.0",
    "tags": ["category1", "category2"],
    "requires_pygame": true,
    "entry_point": "main.py",
    "control_panel": "control_panel.py",
    "dependencies": []
}
```

#### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Unique identifier (lowercase, underscores) |
| `name` | string | ✓ | Display name |
| `description` | string | ✓ | Brief description |
| `icon` | string | ✓ | Emoji icon for display |
| `color` | string | ✓ | Hex color for UI accent |
| `version` | string | ✓ | Semantic version (x.y.z) |
| `author` | string | ✓ | Author name or organization |
| `license` | string | | License type (MIT, GPL, etc.) |
| `homepage` | string | | Project URL |
| `min_loops_version` | string | | Minimum Loops version required |
| `tags` | array | | Categories/keywords |
| `requires_pygame` | boolean | | Whether pygame is needed |
| `entry_point` | string | | Main file (default: main.py) |
| `control_panel` | string | | Control panel file if exists |
| `dependencies` | array | | List of pip packages |

### 2. main.py

The main entry point that runs the simulation:

```python
#!/usr/bin/env python3
"""
Simulation Name - Main Entry Point
===================================
Description of what this simulation does.
"""

import pygame
import sys
import os
from pathlib import Path

# Setup path for shared imports
SIMULATION_DIR = Path(__file__).resolve().parent
BASE_DIR = SIMULATION_DIR.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import base simulation class
from shared.base_simulation import BaseSimulation

class SimulationName(BaseSimulation):
    """Main simulation class."""
    
    def __init__(self, width=1200, height=800, **kwargs):
        super().__init__(
            width=width,
            height=height,
            title="Simulation Title",
            fps=60,
            **kwargs
        )
        
        # Frames directory for saving
        self.frames_dir = SIMULATION_DIR / "frames"
        self.frames_dir.mkdir(exist_ok=True)
        
        # Simulation state
        self.frame_count = 0
        self.is_saving = False
        
        # Initialize your simulation components
        self._init_components()
        
    def _init_components(self):
        """Initialize simulation components."""
        pass
        
    def update(self):
        """Update simulation state (called every frame)."""
        self.frame_count += 1
        
    def draw(self):
        """Draw the current frame."""
        # Clear screen
        self.screen.fill((10, 10, 20))
        
        # Draw your simulation
        # pygame.draw.circle(self.screen, (255, 255, 255), (600, 400), 50)
        
        # Draw UI overlay
        self._draw_ui()
        
    def _draw_ui(self):
        """Draw UI elements."""
        font = pygame.font.Font(None, 24)
        
        # Frame counter
        text = font.render(f"Frame: {self.frame_count}", True, (200, 200, 200))
        self.screen.blit(text, (10, 10))
        
        # Recording indicator
        if self.is_saving:
            pygame.draw.circle(self.screen, (255, 50, 50), (self.width - 20, 20), 8)
            
    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_SPACE:
                self._toggle_recording()
            elif event.key == pygame.K_r:
                self._reset()
                
    def _toggle_recording(self):
        """Toggle frame saving."""
        self.is_saving = not self.is_saving
        if self.is_saving:
            print("📹 Recording started...")
        else:
            print("⏹️ Recording stopped")
            
    def _reset(self):
        """Reset simulation to initial state."""
        self.frame_count = 0
        self._init_components()
        
    def save_frame(self):
        """Save current frame (override if custom logic needed)."""
        if self.is_saving:
            frame_path = self.frames_dir / f"frame_{self.frame_count:06d}.png"
            pygame.image.save(self.screen, str(frame_path))


def main():
    """Main entry point."""
    # Parse command line arguments if needed
    import argparse
    parser = argparse.ArgumentParser(description='Run simulation')
    parser.add_argument('--width', type=int, default=1200)
    parser.add_argument('--height', type=int, default=800)
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    
    # Create and run simulation
    sim = SimulationName(
        width=args.width,
        height=args.height
    )
    
    if args.record:
        sim.is_saving = True
        
    sim.run()


if __name__ == "__main__":
    main()
```

### 3. __init__.py

Package initializer for proper Python imports:

```python
"""
Simulation Name Add-on
======================
Brief description.
"""

from .main import SimulationName, main

__all__ = ['SimulationName', 'main']
__version__ = '1.0.0'
```

---

## Optional Files

### control_panel.py

A Tkinter-based GUI for controlling the simulation:

```python
#!/usr/bin/env python3
"""
Simulation Control Panel
========================
Tkinter GUI for configuring and launching the simulation.
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import sys
from pathlib import Path

SIMULATION_DIR = Path(__file__).resolve().parent
BASE_DIR = SIMULATION_DIR.parent.parent

class ControlPanel:
    """Control panel GUI."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simulation Control Panel")
        self.root.geometry("400x500")
        self.root.configure(bg='#1a1a2e')
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create GUI widgets."""
        # Title
        title = tk.Label(
            self.root, 
            text="🎮 Simulation Name",
            font=('Segoe UI', 18, 'bold'),
            fg='#eee',
            bg='#1a1a2e'
        )
        title.pack(pady=20)
        
        # Settings Frame
        settings = ttk.LabelFrame(self.root, text="Settings")
        settings.pack(padx=20, pady=10, fill='x')
        
        # Width
        ttk.Label(settings, text="Width:").grid(row=0, column=0, padx=5, pady=5)
        self.width_var = tk.StringVar(value="1200")
        ttk.Entry(settings, textvariable=self.width_var, width=10).grid(row=0, column=1)
        
        # Height  
        ttk.Label(settings, text="Height:").grid(row=1, column=0, padx=5, pady=5)
        self.height_var = tk.StringVar(value="800")
        ttk.Entry(settings, textvariable=self.height_var, width=10).grid(row=1, column=1)
        
        # Record checkbox
        self.record_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            settings, 
            text="Start Recording", 
            variable=self.record_var
        ).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Launch Button
        launch_btn = tk.Button(
            self.root,
            text="🚀 Launch Simulation",
            command=self._launch,
            font=('Segoe UI', 12),
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=10
        )
        launch_btn.pack(pady=30)
        
    def _launch(self):
        """Launch the simulation."""
        cmd = [
            sys.executable,
            str(SIMULATION_DIR / "main.py"),
            '--width', self.width_var.get(),
            '--height', self.height_var.get()
        ]
        
        if self.record_var.get():
            cmd.append('--record')
            
        subprocess.Popen(cmd)
        
    def run(self):
        """Run the control panel."""
        self.root.mainloop()


def main():
    panel = ControlPanel()
    panel.run()


if __name__ == "__main__":
    main()
```

### config.py

Configuration constants and defaults:

```python
"""
Simulation Configuration
========================
Default settings and constants.
"""

# Display Settings
DEFAULT_WIDTH = 1200
DEFAULT_HEIGHT = 800
DEFAULT_FPS = 60

# Colors (RGB tuples or hex strings)
BACKGROUND_COLOR = (10, 10, 20)
PRIMARY_COLOR = (100, 102, 241)
SECONDARY_COLOR = (59, 130, 246)
ACCENT_COLOR = (16, 185, 129)

# Simulation Parameters
MAX_PARTICLES = 1000
PHYSICS_TIMESTEP = 1/60
GRAVITY = (0, 9.8)

# File Paths
ASSETS_DIR = "assets"
FRAMES_DIR = "frames"
```

### requirements.txt

Additional Python dependencies (beyond pygame):

```
numpy>=1.20.0
scipy>=1.7.0
Pillow>=8.0.0
```

---

## Using the Base Simulation Class

The `BaseSimulation` class provides common functionality:

```python
from shared.base_simulation import BaseSimulation

class MySimulation(BaseSimulation):
    def __init__(self):
        super().__init__(
            width=1200,
            height=800,
            title="My Simulation",
            fps=60,
            resizable=False,
            fullscreen=False
        )
        
    # Required methods to implement:
    
    def update(self):
        """Called every frame to update state."""
        pass
        
    def draw(self):
        """Called every frame to render."""
        pass
        
    # Optional methods to override:
    
    def handle_event(self, event):
        """Handle pygame events."""
        pass
        
    def on_resize(self, new_width, new_height):
        """Called when window is resized."""
        pass
        
    def on_init(self):
        """Called after pygame init, before main loop."""
        pass
        
    def on_cleanup(self):
        """Called before pygame quit."""
        pass
```

### BaseSimulation Properties

| Property | Type | Description |
|----------|------|-------------|
| `screen` | pygame.Surface | Main display surface |
| `clock` | pygame.time.Clock | Frame rate controller |
| `running` | bool | Set to False to exit |
| `width` | int | Current window width |
| `height` | int | Current window height |
| `fps` | int | Target frames per second |
| `frame_count` | int | Current frame number |
| `delta_time` | float | Time since last frame |

---

## Saving Frames for Video

### Automatic Frame Saving

```python
class MySimulation(BaseSimulation):
    def __init__(self):
        super().__init__(...)
        self.is_recording = False
        self.frames_dir = Path(__file__).parent / "frames"
        self.frames_dir.mkdir(exist_ok=True)
        
    def update(self):
        if self.is_recording:
            self._save_frame()
            
    def _save_frame(self):
        filename = self.frames_dir / f"frame_{self.frame_count:06d}.png"
        pygame.image.save(self.screen, str(filename))
```

### Video Generation

After recording frames, use the VideoGenerator:

```python
from shared.video_generator import VideoGenerator

# Generate video from frames
generator = VideoGenerator()
video_path = generator.generate_video(
    frame_folder="frames",
    output_name="my_simulation",
    fps=60,
    quality="high"
)
print(f"Video saved: {video_path}")
```

---

## Packaging as Add-on

### Step 1: Verify Structure

Ensure your simulation has all required files:

```
my_simulation/
├── simulation.json    ✓
├── main.py            ✓
└── __init__.py        ✓
```

### Step 2: Validate simulation.json

Run validation (when installed in Loops):

```python
from backend.addon_manager import AddonManager

manager = AddonManager()
is_valid, errors = manager.validate_addon_folder("path/to/my_simulation")

if is_valid:
    print("✓ Add-on is valid!")
else:
    for error in errors:
        print(f"✗ {error}")
```

### Step 3: Create ZIP Package

```bash
# From parent directory
zip -r my_simulation.zip my_simulation/
```

Or with Python:

```python
import shutil
shutil.make_archive('my_simulation', 'zip', '.', 'my_simulation')
```

### Step 4: Upload via Dashboard

1. Open Loops Dashboard
2. Navigate to "Add-ons" page
3. Click "Upload Add-on"
4. Select your `.zip` file
5. Wait for validation and installation

---

## Best Practices

### 1. Code Organization

```python
# Good: Modular structure
class Simulation:
    def __init__(self):
        self.renderer = Renderer()
        self.physics = PhysicsEngine()
        self.ui = UIManager()
        
# Bad: Monolithic
class Simulation:
    def __init__(self):
        # 500 lines of initialization...
```

### 2. Performance

```python
# Good: Pre-calculate and cache
def __init__(self):
    self.color_cache = {i: self._calculate_color(i) for i in range(256)}
    
# Bad: Calculate every frame
def draw(self):
    for i in range(256):
        color = self._calculate_color(i)  # Slow!
```

### 3. Resource Management

```python
# Good: Load resources once
def __init__(self):
    self.sprites = {
        'player': pygame.image.load('assets/player.png'),
        'enemy': pygame.image.load('assets/enemy.png')
    }
    
# Bad: Load every frame
def draw(self):
    player = pygame.image.load('assets/player.png')  # Very slow!
```

### 4. Error Handling

```python
# Good: Graceful fallback
def load_config(self):
    try:
        with open('config.json') as f:
            return json.load(f)
    except FileNotFoundError:
        return self.default_config
        
# Bad: Crash on missing file
def load_config(self):
    with open('config.json') as f:
        return json.load(f)
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "pygame not found" | Ensure pygame-ce is installed in venv |
| "Import error for shared" | Check sys.path setup in main.py |
| "Add-on validation failed" | Verify simulation.json format |
| "Frames not saving" | Check frames directory permissions |

### Debug Mode

Add debug logging to your simulation:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MySimulation:
    def update(self):
        logger.debug(f"Frame {self.frame_count}: state={self.state}")
```

---

## Examples

### Example 1: Particle System

See `simulations/particle_system/` for a complete particle simulation example.

### Example 2: Sorting Visualizer

See `simulations/sorting_visualizer/` for the built-in sorting visualization.

### Example 3: Fractal Generator

See `simulations/fractal_generator/` for Mandelbrot/Julia set rendering.

---

## Support

- **Documentation**: Check `docs/` folder
- **Issues**: Report bugs via dashboard feedback
- **Community**: Share your add-ons!

---

## Changelog

### Version 1.0.0
- Initial add-on architecture
- BaseSimulation class
- VideoGenerator integration
- Upload/download system
