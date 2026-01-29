# AI Plugin Creation Guide for Loops Visualization System

## Table of Contents
1. [Introduction](#introduction)
2. [Mandatory Plugin Structure](#mandatory-plugin-structure)
3. [Complete File Templates](#complete-file-templates)
4. [Dependencies and Requirements](#dependencies-and-requirements)
5. [Control Panel Architecture](#control-panel-architecture)
6. [Frame Management System](#frame-management-system)
7. [Video Generation Integration](#video-generation-integration)
8. [Advanced Features Guide](#advanced-features-guide)
   - [Video Generation - Complete Reference](#video-generation---complete-reference)
     - [Error Handling - CRITICAL Section](#️-error-handling---critical-section)
   - [Frame Management Best Practices](#frame-management-best-practices)
   - [Control Panel GUI Recommendations](#control-panel-gui-recommendations)
9. [Base Simulation Class Reference](#base-simulation-class-reference)
10. [simulation.json Schema](#simulationjson-schema)
11. [Important Rules and Best Practices](#important-rules-and-best-practices)
12. [Testing Your Plugin](#testing-your-plugin)
13. [Packaging and Distribution](#packaging-and-distribution)
14. [Complete Working Example](#complete-working-example)

---

## Introduction

### What is Loops?
Loops is a modular visualization system that runs pygame-based simulations (called "plugins" or "addons"). It provides:
- A web-based dashboard for managing simulations
- A standardized plugin architecture
- Global video generation service (FFmpeg-based)
- Control panel framework (Tkinter-based)
- Frame management and video output

### What is a Plugin?
A plugin is a self-contained visualization that:
- Runs as a **separate process** from the main system
- Has its own **control panel** (separate Tkinter window)
- Launches a **clean simulation window** (pygame)
- Saves **frames** for video generation
- Can be installed, uninstalled, and launched via the dashboard

### The Two-Window Architecture
**CRITICAL CONCEPT:** Every plugin has TWO separate windows:

1. **Control Panel Window** (Tkinter)
   - Contains ALL user controls
   - Stays open during simulation
   - Can start/stop/configure simulation
   - Handles recording controls
   - Triggers video generation

2. **Simulation Window** (Pygame)
   - CLEAN visual display only
   - Minimal or NO UI overlays
   - Runs in separate process
   - Controlled by the control panel

---

## Mandatory Plugin Structure

Your plugin MUST follow this exact structure:

```
your_plugin_name/
├── __init__.py              # Package initialization (REQUIRED)
├── simulation.json          # Metadata and configuration (REQUIRED)
├── main.py                  # Simulation entry point (REQUIRED)
├── control_panel.py         # Control panel entry point (REQUIRED)
├── requirements.txt         # Python dependencies (OPTIONAL - but IMPORTANT)
├── frames/                  # Frame storage directory (REQUIRED - created at runtime)
│   └── frame_000001.png     # Sequential frame files
├── README.md                # Documentation (RECOMMENDED)
└── [additional files]       # Any other resources you need
```

### Why Each File is Required

- **`__init__.py`**: Makes your plugin a Python package, allows imports
- **`simulation.json`**: Tells Loops about your plugin (name, icon, metadata)
- **`main.py`**: Contains the pygame simulation logic
- **`control_panel.py`**: Contains the Tkinter control interface
- **`requirements.txt`**: Specifies Python package dependencies (optional but recommended)
- **`frames/`**: Directory for saved frames (your code creates this)

---

## Complete File Templates

### 1. `__init__.py` Template

```python
"""
[Plugin Name] - [Brief Description]
=================================
[Longer description of what your plugin does]

Author: [Your Name]
Version: [Version Number]
"""

from .main import [YourSimulationClass], main

__all__ = ['[YourSimulationClass]', 'main']
__version__ = '[version number]'
```

**Example:**
```python
"""
Bouncing Balls - Physics Simulation
====================================
Visualizes realistic ball physics with gravity, collisions, and energy conservation.

Author: Jane Doe
Version: 1.0.0
"""

from .main import BouncingBalls, main

__all__ = ['BouncingBalls', 'main']
__version__ = '1.0.0'
```

---

### 2. `simulation.json` Template

```json
{
  "id": "your_plugin_id",
  "name": "Your Plugin Display Name",
  "description": "Clear description of what your plugin does and what it visualizes.",
  "icon": "🎮",
  "color": "#3b82f6",
  "version": "1.0.0",
  "author": "Your Name",
  "license": "MIT",
  "homepage": "https://github.com/yourname/yourplugin",
  "min_loops_version": "1.0.0",
  "tags": ["category1", "category2", "visualization"],
  "requires_pygame": true,
  "entry_point": "main.py",
  "control_panel": "control_panel.py",
  "dependencies": []
}
```

**Field Explanations:**
- `id`: **MUST** be lowercase with underscores only (e.g., `bouncing_balls`)
- `name`: User-facing display name (can have spaces, capitals)
- `icon`: Single emoji that represents your plugin
- `color`: Hex color for the plugin card in dashboard
- `tags`: Array of strings for categorization
- `requires_pygame`: **MUST** be `true` for pygame-based simulations
- `entry_point`: Always `"main.py"`
- `control_panel`: Always `"control_panel.py"`
- `dependencies`: List of extra Python packages (if needed, e.g., `["numpy", "scipy"]`)

---

### 3. `main.py` Complete Template

```python
#!/usr/bin/env python3
"""
[Plugin Name] - Main Simulation
================================
Description of the simulation.

This module contains the main pygame simulation logic.
It can be launched standalone or via the control panel.
"""

import os
import sys
import random
import argparse
from pathlib import Path

# Add shared directory to path for imports
current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent
shared_dir = root_dir / "shared"
sys.path.insert(0, str(shared_dir))

import pygame
from base_simulation import BaseSimulation


class YourSimulationClass(BaseSimulation):
    """Main simulation class."""
    
    def __init__(self, width=1200, height=800, fps=60):
        """
        Initialize the simulation.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
            fps: Target frames per second
        """
        super().__init__(width=width, height=height, fps=fps, title="Your Plugin Name")
        
        # Initialize your simulation state here
        self.entities = []
        
        # Colors
        self.bg_color = (20, 20, 30)
        self.text_color = (255, 255, 255)
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.ui_font = pygame.font.SysFont('Arial', 20)
        
        # Setup frames folder (use current_dir for proper path)
        self.frames_folder = str(current_dir / "frames")
        self.setup_frames_folder(self.frames_folder)
    
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
        # Update your simulation logic here
        pass
    
    def draw(self):
        """Draw the simulation."""
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw your visualization here
        
        # Optional: Draw minimal status info (top-right corner)
        if self.recording:
            rec_text = self.ui_font.render(f"● REC {self.frame_count}", True, (255, 0, 0))
            self.screen.blit(rec_text, (self.width - 150, 10))
        
        # Draw pause indicator
        if self.paused:
            pause_text = self.title_font.render("PAUSED", True, (255, 255, 0))
            text_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(pause_text, text_rect)
    
    def reset(self):
        """Reset simulation to initial state."""
        # Reset your simulation state here
        pass


def main():
    """Main entry point for standalone execution."""
    parser = argparse.ArgumentParser(description="Your Plugin Name")
    parser.add_argument('--width', type=int, default=1200, help='Window width')
    parser.add_argument('--height', type=int, default=800, help='Window height')
    parser.add_argument('--fps', type=int, default=60, help='Frames per second')
    parser.add_argument('--record', action='store_true', help='Start recording immediately')
    
    args = parser.parse_args()
    
    sim = YourSimulationClass(
        width=args.width,
        height=args.height,
        fps=args.fps
    )
    
    if args.record:
        sim.start_recording()
    
    sim.run()


if __name__ == "__main__":
    main()
```

---

### 4. `control_panel.py` Complete Template

```python
#!/usr/bin/env python3
"""
[Plugin Name] - Control Panel
==============================
Tkinter-based GUI for configuring and launching the simulation.

This is the main interface for users to interact with your plugin.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading
from pathlib import Path

# Get paths
SIMULATION_DIR = Path(__file__).resolve().parent
BASE_DIR = SIMULATION_DIR.parent.parent
FRAMES_FOLDER = SIMULATION_DIR / "frames"


class ControlPanel:
    """Control panel GUI for [Plugin Name]."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎮 [Plugin Name] - Control Panel")
        self.root.geometry("500x700")
        self.root.configure(bg='#0f172a')
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#0f172a', foreground='#e2e8f0', font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), foreground='#10b981')
        
        # Variables for settings
        self.width_var = tk.StringVar(value="1200")
        self.height_var = tk.StringVar(value="800")
        self.fps_var = tk.StringVar(value="60")
        self.auto_record_var = tk.BooleanVar(value=False)
        
        # Add more variables for your specific controls
        self.speed_var = tk.IntVar(value=50)
        self.count_var = tk.IntVar(value=100)
        
        # Build UI
        self._create_widgets()
        
        # Update frame count
        self._update_frame_count()
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = tk.Frame(self.root, bg='#0f172a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = ttk.Label(
            main_frame,
            text="🎮 [Plugin Name]",
            style='Title.TLabel'
        )
        title.pack(pady=(0, 10))
        
        # Description
        desc = ttk.Label(
            main_frame,
            text="Brief description of what this does",
            font=('Segoe UI', 9),
            foreground='#94a3b8'
        )
        desc.pack(pady=(0, 20))
        
        # Window Settings
        self._create_window_settings(main_frame)
        
        # Simulation Settings
        self._create_simulation_settings(main_frame)
        
        # Recording Settings
        self._create_recording_settings(main_frame)
        
        # Frame Management
        self._create_frame_management(main_frame)
        
        # Launch Button
        self._create_launch_button(main_frame)
    
    def _create_window_settings(self, parent):
        """Create window configuration section."""
        frame = tk.LabelFrame(
            parent,
            text="⚙️ Window Settings",
            bg='#1e293b',
            fg='#e2e8f0',
            font=('Segoe UI', 11, 'bold'),
            relief='ridge',
            bd=2
        )
        frame.pack(fill='x', pady=(0, 15))
        
        # Size
        size_frame = tk.Frame(frame, bg='#1e293b')
        size_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(size_frame, text="Size:").pack(side='left')
        ttk.Entry(size_frame, textvariable=self.width_var, width=8).pack(side='left', padx=(10, 5))
        ttk.Label(size_frame, text="×").pack(side='left')
        ttk.Entry(size_frame, textvariable=self.height_var, width=8).pack(side='left', padx=5)
        
        # FPS
        fps_frame = tk.Frame(frame, bg='#1e293b')
        fps_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(fps_frame, text="FPS:").pack(side='left')
        ttk.Spinbox(fps_frame, from_=30, to=120, textvariable=self.fps_var, width=8).pack(side='left', padx=10)
    
    def _create_simulation_settings(self, parent):
        """Create simulation-specific settings."""
        frame = tk.LabelFrame(
            parent,
            text="🎯 Simulation Settings",
            bg='#1e293b',
            fg='#e2e8f0',
            font=('Segoe UI', 11, 'bold'),
            relief='ridge',
            bd=2
        )
        frame.pack(fill='x', pady=(0, 15))
        
        # Example: Speed slider
        speed_frame = tk.Frame(frame, bg='#1e293b')
        speed_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(speed_frame, text="Speed:").pack(side='left')
        self.speed_label = ttk.Label(speed_frame, text=str(self.speed_var.get()))
        self.speed_label.pack(side='right')
        
        speed_scale = ttk.Scale(
            frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=lambda v: self.speed_label.config(text=str(int(float(v))))
        )
        speed_scale.pack(fill='x', padx=15, pady=(0, 10))
        
        # Example: Count spinbox
        count_frame = tk.Frame(frame, bg='#1e293b')
        count_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(count_frame, text="Count:").pack(side='left')
        ttk.Spinbox(count_frame, from_=10, to=500, textvariable=self.count_var, width=10).pack(side='left', padx=10)
    
    def _create_recording_settings(self, parent):
        """Create recording settings section."""
        frame = tk.LabelFrame(
            parent,
            text="🎬 Recording",
            bg='#1e293b',
            fg='#e2e8f0',
            font=('Segoe UI', 11, 'bold'),
            relief='ridge',
            bd=2
        )
        frame.pack(fill='x', pady=(0, 15))
        
        record_check = tk.Checkbutton(
            frame,
            text="Start recording on launch",
            variable=self.auto_record_var,
            bg='#1e293b',
            fg='#e2e8f0',
            selectcolor='#334155',
            activebackground='#1e293b',
            activeforeground='#10b981',
            font=('Segoe UI', 10)
        )
        record_check.pack(padx=15, pady=10, anchor='w')
    
    def _create_frame_management(self, parent):
        """Create frame management section."""
        frame = tk.LabelFrame(
            parent,
            text="📁 Frame Management",
            bg='#1e293b',
            fg='#e2e8f0',
            font=('Segoe UI', 11, 'bold'),
            relief='ridge',
            bd=2
        )
        frame.pack(fill='x', pady=(0, 15))
        
        # Frame count
        count_frame = tk.Frame(frame, bg='#1e293b')
        count_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(count_frame, text="Saved Frames:").pack(side='left')
        self.frame_count_label = ttk.Label(count_frame, text="0", font=('Arial', 12, 'bold'))
        self.frame_count_label.pack(side='right')
        
        # Buttons
        btn_frame = tk.Frame(frame, bg='#1e293b')
        btn_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Button(btn_frame, text="🔄 Refresh", command=self._update_frame_count).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="🗑️ Clear", command=self._clear_frames).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="📂 Open Folder", command=self._open_frames_folder).pack(side='left', padx=2)
        
        # Video generation button
        video_btn = tk.Button(
            frame,
            text="🎬 Generate Video",
            bg='#2196F3',
            fg='white',
            activebackground='#1976D2',
            font=('Segoe UI', 11, 'bold'),
            relief='flat',
            cursor='hand2',
            command=self._generate_video
        )
        video_btn.pack(fill='x', padx=15, pady=10)
    
    def _create_launch_button(self, parent):
        """Create launch simulation button."""
        launch_btn = tk.Button(
            parent,
            text="🚀 Launch Simulation",
            command=self._launch,
            bg='#10b981',
            fg='white',
            activebackground='#059669',
            activeforeground='white',
            font=('Segoe UI', 13, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=12
        )
        launch_btn.pack(fill='x', pady=(10, 0))
        
        # Hover effects
        launch_btn.bind('<Enter>', lambda e: launch_btn.config(bg='#059669'))
        launch_btn.bind('<Leave>', lambda e: launch_btn.config(bg='#10b981'))
    
    def _launch(self):
        """Launch the simulation."""
        cmd = [
            sys.executable,
            str(SIMULATION_DIR / "main.py"),
            '--width', self.width_var.get(),
            '--height', self.height_var.get(),
            '--fps', self.fps_var.get(),
        ]
        
        # Add your custom arguments
        # cmd.extend(['--speed', str(self.speed_var.get())])
        # cmd.extend(['--count', str(self.count_var.get())])
        
        if self.auto_record_var.get():
            cmd.append('--record')
        
        subprocess.Popen(cmd)
    
    def _update_frame_count(self):
        """Update the frame count display."""
        if not FRAMES_FOLDER.exists():
            count = 0
        else:
            count = len([f for f in FRAMES_FOLDER.glob("*.png")])
        
        self.frame_count_label.config(text=str(count))
    
    def _clear_frames(self):
        """Clear all saved frames."""
        if not FRAMES_FOLDER.exists():
            messagebox.showinfo("Info", "No frames folder exists.")
            return
        
        frames = list(FRAMES_FOLDER.glob("*.png"))
        if not frames:
            messagebox.showinfo("Info", "No frames to clear.")
            return
        
        if messagebox.askyesno("Confirm", f"Delete {len(frames)} frames?"):
            for frame in frames:
                frame.unlink()
            self._update_frame_count()
            messagebox.showinfo("Success", "Frames cleared!")
    
    def _open_frames_folder(self):
        """Open frames folder in file explorer."""
        FRAMES_FOLDER.mkdir(exist_ok=True)
        
        if sys.platform == 'win32':
            os.startfile(str(FRAMES_FOLDER))
        elif sys.platform == 'darwin':
            subprocess.run(['open', str(FRAMES_FOLDER)])
        else:
            subprocess.run(['xdg-open', str(FRAMES_FOLDER)])
    
    def _generate_video(self):
        """Generate video from frames."""
        if not FRAMES_FOLDER.exists():
            messagebox.showwarning("Warning", "No frames folder exists.")
            return
        
        frame_count = len(list(FRAMES_FOLDER.glob("*.png")))
        if frame_count == 0:
            messagebox.showwarning("Warning", "No frames to generate video from.\nRun a simulation first with recording enabled.")
            return
        
        # Show settings dialog
        self._show_video_settings_dialog()
    
    def _show_video_settings_dialog(self):
        """Show video generation settings dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Video Settings")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Video Generation Settings", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # FPS
        fps_frame = ttk.Frame(dialog)
        fps_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(fps_frame, text="FPS:").pack(side=tk.LEFT)
        fps_var = tk.IntVar(value=60)
        ttk.Spinbox(fps_frame, from_=15, to=120, textvariable=fps_var, width=10).pack(side=tk.RIGHT)
        
        # Quality
        quality_frame = ttk.Frame(dialog)
        quality_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(quality_frame, text="Quality:").pack(side=tk.LEFT)
        quality_var = tk.StringVar(value="high")
        ttk.Combobox(
            quality_frame,
            textvariable=quality_var,
            values=["low", "medium", "high", "ultra", "lossless"],
            state="readonly",
            width=10
        ).pack(side=tk.RIGHT)
        
        frame_count = len(list(FRAMES_FOLDER.glob("*.png")))
        ttk.Label(dialog, text=f"Frames: {frame_count}", font=('Arial', 10)).pack(pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame,
            text="Generate",
            command=lambda: self._do_video_generation(dialog, fps_var.get(), quality_var.get())
        ).pack(side=tk.LEFT, padx=5)
    
    def _do_video_generation(self, settings_dialog, fps, quality):
        """Perform video generation."""
        settings_dialog.destroy()
        
        # Show progress
        progress = tk.Toplevel(self.root)
        progress.title("Generating Video...")
        progress.geometry("350x120")
        progress.resizable(False, False)
        progress.transient(self.root)
        
        ttk.Label(progress, text="🎬 Generating video...", font=('Arial', 12)).pack(pady=15)
        progress_bar = ttk.Progressbar(progress, mode='indeterminate')
        progress_bar.pack(fill=tk.X, padx=30, pady=10)
        progress_bar.start(10)
        
        def generate():
            try:
                from shared.video_generator import VideoGenerator
                from datetime import datetime
                
                # Use VideoGenerator directly (NOT API endpoint)
                generator = VideoGenerator()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_name = f"[plugin_name]_{timestamp}"
                
                output_path = generator.generate_video(
                    frame_folder=str(FRAMES_FOLDER),
                    output_name=output_name,
                    fps=fps,
                    quality=quality
                )
                
                self.root.after(0, progress.destroy)
                self.root.after(0, lambda: self._show_video_success(output_path))
            
            except Exception as e:
                self.root.after(0, progress.destroy)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Video generation failed:\n{str(e)}"))
        
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
    
    def _show_video_success(self, video_path):
        """Show success message."""
        result = messagebox.askyesno(
            "Video Generated!",
            f"Video generated successfully!\n\n{video_path}\n\nOpen containing folder?"
        )
        if result:
            folder = os.path.dirname(video_path)
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                subprocess.run(['open', folder])
            else:
                subprocess.run(['xdg-open', folder])
    
    def run(self):
        """Start the control panel."""
        self.root.mainloop()


def main():
    panel = ControlPanel()
    panel.run()


if __name__ == "__main__":
    main()
```

---

## Dependencies and Requirements

### Purpose
Add-ons can specify Python package dependencies that are required for their functionality. The Loops system automatically handles dependency installation when a plugin is installed.

### Requirements File

**File**: `requirements.txt` (optional but recommended)

**Location**: Root of your plugin directory

**Format**: Standard pip requirements format (one package per line)

### Automatic Installation

When you install a plugin:
1. The system checks if `requirements.txt` exists in the plugin directory
2. If found, dependencies are automatically installed using pip
3. Installation has a **5-minute timeout** to prevent hanging
4. Failed installations log a warning but don't fail the plugin installation
5. Dependencies install using the system's Python environment

### Example requirements.txt

```
pygame-ce>=2.3.2
numpy>=1.20.0
pillow>=9.0.0
requests>=2.28.0
```

### Best Practices

1. **Pin Major Versions**: Use `>=` for compatibility while ensuring minimum required features
   ```
   numpy>=1.20.0  # Good: allows updates
   numpy==1.20.0  # Avoid: too restrictive
   numpy          # Bad: no version guarantee
   ```

2. **Don't Include System Packages**: Don't list packages that come with Python
   - ❌ Don't include: `sys`, `os`, `pathlib`, `json`, `argparse`
   - ✅ Only include: Third-party packages from PyPI

3. **Test Dependencies**: Before packaging, test your plugin with a fresh install
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

4. **Keep Dependencies Minimal**: Only include what you actually need
   - Each dependency adds installation time
   - Large dependencies (TensorFlow, PyTorch) significantly increase install time
   - Consider lightweight alternatives when possible

5. **Document Dependencies**: Add comments to explain what each package is for
   ```
   # Graphics and visualization
   pygame-ce>=2.3.2
   
   # Numerical computing
   numpy>=1.20.0
   
   # Image processing for frame manipulation
   pillow>=9.0.0
   ```

### Common Dependencies for Loops Plugins

- **`pygame-ce`**: Usually pre-installed with Loops (graphics and game development)
  - Don't include unless you need a specific version
  - Loops uses pygame-ce (Community Edition)

- **`numpy`**: Numerical computing and array operations
  - Great for physics simulations
  - Fast mathematical operations

- **`pillow`**: Image processing and manipulation
  - Load/save images
  - Image transformations
  - Color manipulation

- **`requests`**: HTTP library (OPTIONAL)
  - Only needed if your plugin makes external web requests
  - NOT needed for video generation (use VideoGenerator directly)

- **`scipy`**: Scientific computing
  - Advanced mathematics
  - Optimization algorithms
  - Signal processing

- **`matplotlib`**: Plotting and graphing
  - Create charts and plots
  - Visualize data
  - Note: Adds significant size

### Important Notes

⚠️ **System Python Environment**
- Dependencies install into the system's Python environment
- Make sure dependencies are compatible with the system Python version
- Virtual environments are not used by default

⚠️ **Installation Timeout**
- 5-minute timeout prevents indefinite hanging
- Large dependencies (TensorFlow, PyTorch) may exceed timeout
- Consider pre-installation instructions in README if needed

⚠️ **Failed Installation Handling**
- Failed dependency installation logs a warning
- Plugin installation continues (doesn't fail)
- Plugin may not work correctly if dependencies are missing
- Always test your plugin after installation

⚠️ **Compatibility**
- Check that dependencies work on target platforms (Windows, macOS, Linux)
- Some packages have platform-specific requirements
- Document any platform-specific notes in README

### Example Plugin with Dependencies

For a physics simulation that uses numpy for calculations:

**requirements.txt:**
```
# Numerical computing for physics calculations
numpy>=1.20.0

# Vector and matrix operations
scipy>=1.7.0
```

**README.md snippet:**
```markdown
## Requirements

This plugin requires:
- numpy (>=1.20.0) - For fast physics calculations
- scipy (>=1.7.0) - For collision detection algorithms

Dependencies are automatically installed when you install the plugin.
```

---

## Control Panel Architecture

### Key Principles

1. **Separate Process**: Control panel runs in its own process, independent of simulation
2. **Always Visible**: Stays open while simulation runs
3. **Full Control**: Contains ALL controls for the simulation
4. **Clean Launch**: Spawns simulation via subprocess

### Required Sections

Every control panel should have:

1. **Window Settings**
   - Width/Height inputs
   - FPS selector

2. **Simulation Settings**
   - Plugin-specific controls (speed, count, algorithm, etc.)
   - Dropdowns, sliders, checkboxes as needed

3. **Recording Settings**
   - "Auto-record on launch" checkbox
   - Clear indication of recording state

4. **Frame Management**
   - Frame count display
   - Refresh/Clear/Open folder buttons
   - Video generation button

5. **Launch Button**
   - Large, prominent button to start simulation
   - Should build command-line arguments and use subprocess.Popen()

### Communication Patterns

**Control Panel → Simulation:**
- Via command-line arguments when launching
- Example: `--width 1200 --height 800 --fps 60 --record`

**Simulation → Control Panel:**
- Not directly required (they're separate processes)
- Optional: Use files, sockets, or shared memory for advanced features

---

## Frame Management System

### Directory Structure

Each plugin must create and manage its own `frames/` directory:

```
your_plugin/
├── frames/                  # Standard frame location
│   ├── frame_000001.png
│   ├── frame_000002.png
│   └── ...
└── frames/                  # OR multiple subdirectories
    ├── normal/
    │   ├── frame_000001.png
    │   └── ...
    └── comparison/
        ├── frame_000001.png
        └── ...
```

### Frame Naming Convention

**CRITICAL**: Frames MUST be named sequentially with zero-padding:

```
frame_000001.png
frame_000002.png
frame_000003.png
...
frame_009999.png
```

Use this pattern: `frame_{count:06d}.png`

### Saving Frames in main.py

The `BaseSimulation` class provides these methods:

```python
# Setup frames folder
self.frames_folder = str(current_dir / "frames")
self.setup_frames_folder(self.frames_folder)

# Start recording
self.start_recording()

# Automatically saves each frame
# (called in the base class run() loop if self.recording is True)

# Stop recording
self.stop_recording()
```

**Example in your simulation:**

```python
def handle_events(self):
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                if self.recording:
                    self.stop_recording()
                    print(f"Stopped. {self.frame_count} frames saved.")
                else:
                    self.start_recording()
                    print("Recording started...")
```

### Multiple Frame Types

If you need multiple recording modes (e.g., "normal" and "comparison"), create subdirectories:

```python
# In __init__
self.normal_frames = current_dir / "frames" / "normal"
self.comparison_frames = current_dir / "frames" / "comparison"

# Setup both
self.normal_frames.mkdir(parents=True, exist_ok=True)
self.comparison_frames.mkdir(parents=True, exist_ok=True)

# Switch active folder
def set_recording_mode(self, mode):
    if mode == "normal":
        self.frames_folder = str(self.normal_frames)
    else:
        self.frames_folder = str(self.comparison_frames)
    
    self.setup_frames_folder(self.frames_folder)
```

---

## Video Generation Integration

⚠️ **IMPORTANT: Do NOT use HTTP API for video generation!**

Always use VideoGenerator directly by importing from `shared.video_generator`

### The Correct Approach

The Loops system provides video generation through the `VideoGenerator` class:

```python
from shared.video_generator import VideoGenerator

generator = VideoGenerator()
output_path = generator.generate_video(
    frame_folder="path/to/frames",
    output_name="my_video",
    fps=60,
    quality="high"
)
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `frame_folder` | str | ✅ Yes | Absolute path to frames directory |
| `output_name` | str | ✅ Yes | Name for output video (without extension) |
| `fps` | int | ✅ Yes | Frames per second (typically 30-60) |
| `quality` | str | ✅ Yes | "low", "medium", "high", "ultra", or "lossless" |

### Return Value

Returns the absolute path to the generated video file as a string.

### Example Integration in Control Panel

```python
from shared.video_generator import VideoGenerator
from datetime import datetime
from pathlib import Path

SIMULATION_DIR = Path(__file__).resolve().parent

def generate_video(self):
    """Generate video from frames."""
    try:
        generator = VideoGenerator()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_name = f"my_plugin_{timestamp}"
        frame_folder = str(SIMULATION_DIR / "frames")
        
        output_path = generator.generate_video(
            frame_folder=frame_folder,
            output_name=output_name,
            fps=60,
            quality='high'
        )
        
        messagebox.showinfo("Success", f"Video saved: {output_path}")
    
    except Exception as e:
        messagebox.showerror("Error", f"Video generation failed: {str(e)}")
```

---

## Advanced Features Guide

### Video Generation - Complete Reference

⚠️ **CRITICAL: Do NOT use HTTP API for video generation!**

Always import and use `VideoGenerator` directly from `shared.video_generator`

This section provides comprehensive documentation for correctly implementing video generation in your plugins.

#### Required Parameters

The `VideoGenerator.generate_video()` method requires the following parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `frame_folder` | str | ✅ Yes | Absolute path to frame directory (singular, not plural) |
| `output_name` | str | ✅ Yes | Name for output video (without extension) |
| `fps` | int | ✅ Yes | Frames per second (typically 30-60) |
| `quality` | str | ✅ Yes | Video quality: "low", "medium", "high", "ultra", "lossless" |

#### Common Mistakes to Avoid

❌ **Using HTTP API (WRONG!)**
```python
# WRONG - Don't use API endpoints!
import requests
response = requests.post('http://localhost:5000/api/video/generate', ...)
```

✅ **Using VideoGenerator Directly (CORRECT)**
```python
# CORRECT - Import and use VideoGenerator
from shared.video_generator import VideoGenerator
generator = VideoGenerator()
output_path = generator.generate_video(...)
```

❌ **Using Relative Paths**
```python
# WRONG - Relative paths won't work!
generator.generate_video(frame_folder='frames', ...)
generator.generate_video(frame_folder='./frames', ...)
```

✅ **Using Absolute Paths**
```python
# CORRECT - Always use absolute paths
frame_folder = str(SIMULATION_DIR / "frames")
# Or
frame_folder = str(Path(__file__).parent / "frames")
generator.generate_video(frame_folder=frame_folder, ...)
```

❌ **Wrong Parameter Name**
```python
# WRONG - Parameter name is 'frame_folder' (singular)
generator.generate_video(
    frame_folders=[path],  # Wrong! (plural)
    frames_dir=path        # Wrong!
)
```

✅ **Correct Parameter Name**
```python
# CORRECT - Must be 'frame_folder' (singular, string)
generator.generate_video(
    frame_folder=path,  # Correct!
    output_name="video",
    fps=60,
    quality='high'
)
```

#### Complete Working Example

Here's a complete, production-ready implementation using VideoGenerator directly:

```python
#!/usr/bin/env python3
import threading
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

SIMULATION_DIR = Path(__file__).resolve().parent

def _generate_video_thread(self):
    """Generate video in background thread using VideoGenerator directly."""
    try:
        # Step 1: Import VideoGenerator
        from shared.video_generator import VideoGenerator
        
        # Step 2: Create generator instance
        generator = VideoGenerator()
        
        # Step 3: Prepare paths and parameters
        frames_dir = SIMULATION_DIR / "frames"
        frame_folder = str(frames_dir.absolute())
        
        # Step 4: Generate unique output name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"my_simulation_{timestamp}"
        
        # Step 5: Get FPS from GUI (or use default)
        fps = int(self.fps_var.get()) if hasattr(self, 'fps_var') else 60
        
        # Step 6: Generate video using VideoGenerator
        output_path = generator.generate_video(
            frame_folder=frame_folder,
            output_name=output_name,
            fps=fps,
            quality='high'
        )
        
        # Step 7: Show success message on main thread
        self.root.after(0, lambda path=output_path: messagebox.showinfo(
            "Success",
            f"Video generated successfully!\n\n{path}"
        ))
        
        if hasattr(self, 'status_label'):
            self.root.after(0, lambda: self.status_label.config(
                text="Video generated!", 
                fg='#10b981'
            ))
            
    except Exception as e:
        # Handle any errors
        self.root.after(0, lambda: messagebox.showerror(
            "Error", 
            f"Failed to generate video:\n\n{str(e)}"
        ))
        
        if hasattr(self, 'status_label'):
            self.root.after(0, lambda: self.status_label.config(
                text="Video generation failed", 
                fg='#ef4444'
            ))
    finally:
        # Re-enable the button
        if hasattr(self, 'video_btn'):
            self.root.after(0, lambda: self.video_btn.config(
                state='normal', 
                text="🎬 Generate Video"
            ))

def _generate_video(self):
    """Initiate video generation (called by button click)."""
    frames_dir = SIMULATION_DIR / "frames"
    
    # Validate frames exist
    if not frames_dir.exists() or not list(frames_dir.glob("frame_*.png")):
        messagebox.showerror("No Frames", "No frames found to generate video!")
        return
    
    # Disable button during generation
    if hasattr(self, 'video_btn'):
        self.video_btn.config(state='disabled', text="Generating...")
    if hasattr(self, 'status_label'):
        self.status_label.config(text="Generating video...", fg='#8b5cf6')
    
    # Run in background thread to prevent GUI freezing
    threading.Thread(target=self._generate_video_thread, daemon=True).start()
```

#### Threading Best Practices

Always run video generation in a background thread to prevent GUI freezing:

```python
def generate_video_button_click(self):
    """Button click handler."""
    # Update UI immediately
    self.button.config(state='disabled', text="Generating...")
    
    # Run actual generation in background
    threading.Thread(target=self._do_generation, daemon=True).start()

def _do_generation(self):
    """Background thread function."""
    try:
        # Import and use VideoGenerator
        from shared.video_generator import VideoGenerator
        generator = VideoGenerator()
        
        output_path = generator.generate_video(
            frame_folder=str(Path(__file__).parent / "frames"),
            output_name="my_video",
            fps=60,
            quality='high'
        )
        
        # Update UI on main thread
        self.root.after(0, lambda: self.button.config(state='normal'))
        self.root.after(0, lambda: messagebox.showinfo("Success", f"Video saved: {output_path}"))
    except Exception as e:
        # Handle errors on main thread
        self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        self.root.after(0, lambda: self.button.config(state='normal'))
```

**Why threading is important:**
- Video generation can take 30 seconds to several minutes
- Without threading, the GUI will freeze and become unresponsive
- Use `daemon=True` so threads don't prevent program exit
- Always update GUI elements using `root.after()` from background threads

#### ⚠️ Error Handling - CRITICAL Section

#### ⚠️ Error Handling - CRITICAL Section

**DO NOT SKIP THIS!** Improper error handling is the #1 cause of plugin crashes and poor user experience.

##### Common Errors and What They Mean

**1. `FileNotFoundError` - Frames Directory Not Found**

This error means: **The frames directory doesn't exist**

```python
# ✅ CORRECT - Always validate frames exist first
frames_dir = SIMULATION_DIR / "frames"
if not frames_dir.exists() or not list(frames_dir.glob("frame_*.png")):
    messagebox.showerror("No Frames", "No frames found! Record some frames first.")
    return
```

**2. `ImportError` - Cannot Import VideoGenerator**

This means: **The shared module path is not configured correctly**

```python
# Ensure shared module is accessible
try:
    from shared.video_generator import VideoGenerator
except ImportError as e:
    messagebox.showerror(
        "Import Error",
        f"Cannot import VideoGenerator!\n\n{str(e)}\n\n"
        "Make sure the plugin is in the correct directory."
    )
    return
```

**3. `ValueError` - Invalid Parameters**

This means: **Invalid parameters passed to generate_video()**

Solutions:
- Ensure fps is a positive integer
- Ensure quality is one of: "low", "medium", "high", "ultra", "lossless"
- Ensure frame_folder is an absolute path string
- Ensure output_name is a valid filename (no special characters)

**4. General Exceptions**

Always have a catch-all exception handler:

```python
except Exception as e:
    self.root.after(0, lambda: messagebox.showerror(
        "Error",
        f"Video generation failed:\n\n{str(e)}"
    ))
```

##### The CORRECT Error Handling Pattern

Here's the complete pattern you MUST use for video generation:

```python
def _generate_video_thread(self):
    """Generate video with comprehensive error handling."""
    try:
        frames_dir = SIMULATION_DIR / "frames"
        frames_path = str(frames_dir.resolve())
        
        # Make the API request
        response = requests.post(
            'http://localhost:5000/api/video/generate',
            json={
                'frame_folders': [frames_path],
                'output_name': f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'fps': 60,
                'quality': 'high'
            },
            timeout=300  # 5 minute timeout
        )
        
        # CRITICAL: Try to parse JSON FIRST before checking status
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError:
            # Server returned non-JSON (probably an error page)
            self.root.after(0, lambda: messagebox.showerror(
                "Invalid Response",
                "Server returned invalid response.\n\n"
                "This usually means:\n"
                "• Wrong API endpoint\n"
                "• Server error\n"
                "• Server not running properly\n\n"
                f"Response text: {response.text[:200]}"
            ))
            return
        
        # Now check if the request was successful
        if response.status_code == 200:
            # Success!
            video_path = result.get('video', {}).get('path', 'Unknown')
            self.root.after(0, lambda: messagebox.showinfo(
                "Success",
                f"✅ Video generated successfully!\n\n{video_path}"
            ))
            self.root.after(0, lambda: self.status_label.config(
                text="Video generated!", 
                fg='#10b981'
            ))
        else:
            # API returned an error
            error_msg = result.get('error', 'Unknown error')
            self.root.after(0, lambda: messagebox.showerror(
                "API Error",
                f"❌ Video generation failed!\n\n"
                f"Status Code: {response.status_code}\n"
                f"Error: {error_msg}"
            ))
            
    except requests.exceptions.ConnectionError:
        # Server not running
        self.root.after(0, lambda: messagebox.showerror(
            "Connection Error",
            "❌ Cannot connect to backend server!\n\n"
            "Make sure the server is running:\n"
            "python run.py\n\n"
            "The server should be accessible at:\n"
            "http://localhost:5000"
        ))
        
    except requests.exceptions.Timeout:
        # Request took too long
        self.root.after(0, lambda: messagebox.showerror(
            "Timeout Error",
            "❌ Video generation timed out!\n\n"
            "The video generation took longer than 5 minutes.\n\n"
            "Solutions:\n"
            "• Record fewer frames\n"
            "• Lower video quality\n"
            "• Increase timeout in code"
        ))
        
    except Exception as e:
        # Catch-all for unexpected errors
        self.root.after(0, lambda: messagebox.showerror(
            "Unexpected Error",
            f"❌ An unexpected error occurred:\n\n{str(e)}\n\n"
            f"Error type: {type(e).__name__}"
        ))
        
    finally:
        # ALWAYS re-enable the button, even if there was an error
        self.root.after(0, lambda: self.video_btn.config(
            state='normal',
            text="🎬 Generate Video"
        ))
```

##### Exception Types Reference

Common exceptions when using VideoGenerator:

```python
from shared.video_generator import VideoGenerator

try:
    generator = VideoGenerator()
    output_path = generator.generate_video(...)
except ImportError:
    # Cannot import VideoGenerator
    pass
except FileNotFoundError:
    # Frame directory or files not found
    pass
except ValueError:
    # Invalid parameters (fps, quality, etc.)
    pass
except Exception as e:
    # Catch-all for unexpected errors
    pass
```

**Exception Hierarchy:**
```
Exception
├── ImportError (cannot import VideoGenerator)
├── FileNotFoundError (frames directory/files not found)
├── ValueError (invalid parameters)
└── Other exceptions from FFmpeg/video processing
```

##### User-Friendly Error Messages

Good error messages should:
1. ✅ **Tell users WHAT went wrong** (in plain English)
2. ✅ **Explain WHY it happened** (likely causes)
3. ✅ **Show HOW to fix it** (clear steps)
4. ✅ **Use emojis** for visual clarity (❌ ✅ ⚠️ 💡)

**Examples:**

```python
# ❌ BAD - Cryptic, no help
messagebox.showerror("Error", str(e))

# ❌ BAD - Technical jargon
messagebox.showerror("Error", "JSONDecodeError at line 1 column 1")

# ✅ GOOD - Clear, actionable
messagebox.showerror(
    "Server Not Running",
    "❌ Cannot connect to the backend!\n\n"
    "The backend server is not running.\n\n"
    "To fix:\n"
    "1. Open a terminal\n"
    "2. Navigate to the loops directory\n"
    "3. Run: python run.py\n"
    "4. Wait for 'Server started' message\n"
    "5. Try generating video again"
)

# ✅ GOOD - Helpful troubleshooting
messagebox.showerror(
    "Invalid Response",
    "❌ Server returned invalid data!\n\n"
    "Possible causes:\n"
    "• Server crashed or restarted\n"
    "• Wrong API endpoint\n"
    "• Server returning error page\n\n"
    "Try restarting the backend server."
)
```

##### Complete Reference Implementation

Here's the complete, production-ready implementation using VideoGenerator directly:

```python
#!/usr/bin/env python3
"""
Complete reference implementation for video generation with error handling.
Copy this entire method into your control_panel.py
"""

import threading
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

SIMULATION_DIR = Path(__file__).resolve().parent

def _generate_video_thread(self):
    """
    Generate video in background thread with comprehensive error handling.
    
    This is the REFERENCE IMPLEMENTATION - copy this pattern!
    """
    try:
        # Step 1: Validate frames exist first
        frames_dir = SIMULATION_DIR / "frames"
        if not frames_dir.exists() or not list(frames_dir.glob("frame_*.png")):
            self.root.after(0, lambda: messagebox.showwarning(
                "No Frames",
                "⚠️ No frames found!\n\n"
                "Record some frames before generating video."
            ))
            return
        
        # Step 2: Import VideoGenerator
        from shared.video_generator import VideoGenerator
        
        # Step 3: Create generator instance
        generator = VideoGenerator()
        
        # Step 4: Prepare parameters
        frame_folder = str(frames_dir.absolute())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"video_{timestamp}"
        fps = int(self.fps_var.get()) if hasattr(self, 'fps_var') else 60
        
        # Step 5: Generate video
        output_path = generator.generate_video(
            frame_folder=frame_folder,
            output_name=output_name,
            fps=fps,
            quality='high'
        )
        
        # Step 6: Show success message
        self.root.after(0, lambda: messagebox.showinfo(
            "Video Generated",
            f"✅ Video generated successfully!\n\n"
            f"📁 Location: {output_path}"
        ))
        
        if hasattr(self, 'status_label'):
            self.root.after(0, lambda: self.status_label.config(
                text="✅ Video generated!", 
                fg='#10b981'
            ))
    
    except ImportError as e:
        # Cannot import VideoGenerator
        self.root.after(0, lambda: messagebox.showerror(
            "Import Error",
            f"❌ Cannot import VideoGenerator!\n\n{str(e)}\n\n"
            "Make sure the plugin is in the correct directory."
        ))
        if hasattr(self, 'status_label'):
            self.root.after(0, lambda: self.status_label.config(
                text="❌ Import error", 
                fg='#ef4444'
            ))
    
    except FileNotFoundError as e:
        # Frames not found
        self.root.after(0, lambda: messagebox.showerror(
            "File Not Found",
            f"❌ Frame directory or files not found!\n\n{str(e)}\n\n"
            "Make sure frames were saved correctly."
        ))
        if hasattr(self, 'status_label'):
            self.root.after(0, lambda: self.status_label.config(
                text="❌ Files not found", 
                fg='#ef4444'
            ))
    
    except ValueError as e:
        # Invalid parameters
        self.root.after(0, lambda: messagebox.showerror(
            "Invalid Parameters",
            f"❌ Invalid parameters for video generation!\n\n{str(e)}\n\n"
            "Check FPS and quality settings."
        ))
        if hasattr(self, 'status_label'):
            self.root.after(0, lambda: self.status_label.config(
                text="❌ Invalid parameters", 
                fg='#ef4444'
            ))
    
    except Exception as e:
        # Catch-all for unexpected errors
        import traceback
        error_details = traceback.format_exc()
        
        self.root.after(0, lambda: messagebox.showerror(
            "Unexpected Error",
            f"❌ Video generation failed!\n\n"
            f"Error: {str(e)}\n"
            f"Type: {type(e).__name__}"
        ))
        
        # Log full traceback for debugging
        print("=" * 80)
        print("ERROR IN VIDEO GENERATION:")
        print(error_details)
        print("=" * 80)
        
        if hasattr(self, 'status_label'):
            self.root.after(0, lambda: self.status_label.config(
                text="❌ Error occurred", 
                fg='#ef4444'
            ))
    
    finally:
        # ALWAYS re-enable the generate button
        if hasattr(self, 'video_btn'):
            self.root.after(0, lambda: self.video_btn.config(
                state='normal',
                text="🎬 Generate Video"
            ))

def _generate_video(self):
    """
    Button click handler for video generation.
    Validates and starts background thread.
    """
    # Quick validation
    frames_dir = SIMULATION_DIR / "frames"
    if not frames_dir.exists() or not list(frames_dir.glob("frame_*.png")):
        messagebox.showwarning(
            "No Frames",
            "⚠️ No frames found!\n\n"
            "Start recording to generate frames first."
        )
        return
    
    # Update UI
    if hasattr(self, 'video_btn'):
        self.video_btn.config(state='disabled', text="⏳ Generating...")
    if hasattr(self, 'status_label'):
        self.status_label.config(text="🎬 Generating video...", fg='#8b5cf6')
    
    # Run in background thread
    thread = threading.Thread(
        target=self._generate_video_thread,
        daemon=True,
        name="VideoGenerationThread"
    )
    thread.start()
```

##### Testing Your Error Handling

To verify your error handling works correctly, test these scenarios:

**Test 1: No Frames**
```python
# Delete or clear all frames
# Click "Generate Video"
# Expected: Warning message about no frames
```

**Test 2: Import Error**
```python
# Temporarily break the import (e.g., wrong path)
# Expected: Import error with helpful message
```

**Test 3: Invalid Parameters**
```python
# Set fps to invalid value (e.g., negative number)
# Expected: ValueError caught and handled gracefully
```

**Test 4: Valid Request**
```python
# With frames present
# Expected: Success message with video path
```

##### Quick Reference Checklist

Before deploying your plugin, verify:

- ✅ Video generation runs in background thread (doesn't freeze GUI)
- ✅ Import VideoGenerator from `shared.video_generator`
- ✅ Use `generator.generate_video()` method (NOT HTTP API)
- ✅ `frame_folder` parameter is singular (not plural)
- ✅ All parameters are provided (frame_folder, output_name, fps, quality)
- ✅ `ImportError` caught with helpful message
- ✅ `FileNotFoundError` caught for missing frames
- ✅ `ValueError` caught for invalid parameters
- ✅ `finally` block re-enables buttons
- ✅ All UI updates use `root.after(0, ...)`
- ✅ Error messages are user-friendly (not technical)
- ✅ Absolute paths used for frame folder

---

### Frame Management Best Practices

Implementing robust frame management in your control panel improves the user experience significantly.

#### Essential Frame Management Features

Every control panel should include:

1. **Frame Counter Display** - Shows current frame count in real-time
2. **Clear Frames Button** - Removes all frames with confirmation
3. **Open Folder Button** - Opens frames directory in file explorer
4. **Frame Monitoring** - Updates count during recording

#### Complete Implementation Example

```python
#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import threading
import shutil
import subprocess
import sys
import os
from pathlib import Path
import time

SIMULATION_DIR = Path(__file__).resolve().parent

class ControlPanel:
    def __init__(self):
        self.root = tk.Tk()
        self.frames_count = 0
        self.is_recording = False
        
        # Create GUI...
        self._create_frame_management_ui()
        
        # Start monitoring frames
        self._update_frame_count()
    
    def _create_frame_management_ui(self):
        """Create frame management UI elements."""
        
        # Frame counter display (prominent)
        self.frames_label = tk.Label(
            self.status_frame,
            text="📁 Frames: 0",
            bg='#1e293b',
            fg='#3b82f6',
            font=('Segoe UI', 11, 'bold')
        )
        self.frames_label.pack(padx=15, pady=10)
        
        # Control buttons frame
        frame_mgmt_frame = tk.Frame(self.main_frame, bg='#0f172a')
        frame_mgmt_frame.pack(fill='x', pady=5)
        
        # Clear frames button
        self.clear_frames_btn = tk.Button(
            frame_mgmt_frame,
            text="🗑️ Clear Frames",
            command=self._clear_frames,
            bg='#f97316',
            fg='white',
            activebackground='#ea580c',
            activeforeground='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8
        )
        self.clear_frames_btn.pack(side='left', fill='x', expand=True, padx=(0, 2.5))
        
        # Open folder button
        self.open_folder_btn = tk.Button(
            frame_mgmt_frame,
            text="📂 Open Frames Folder",
            command=self._open_frames_folder,
            bg='#06b6d4',
            fg='white',
            activebackground='#0891b2',
            activeforeground='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8
        )
        self.open_folder_btn.pack(side='left', fill='x', expand=True, padx=(2.5, 0))
    
    def _update_frame_count(self):
        """Update frame count display (called periodically)."""
        frames_dir = SIMULATION_DIR / "frames"
        
        if frames_dir.exists():
            frame_files = list(frames_dir.glob("frame_*.png"))
            self.frames_count = len(frame_files)
            self.frames_label.config(text=f"📁 Frames: {self.frames_count}")
            
            # Enable/disable video button based on frame count
            if self.frames_count > 0:
                self.video_btn.config(state='normal')
            else:
                self.video_btn.config(state='disabled')
        
        # Schedule next update (every 2 seconds)
        self.root.after(2000, self._update_frame_count)
    
    def _monitor_frames(self):
        """Monitor frame count during recording (more frequent updates)."""
        frames_dir = SIMULATION_DIR / "frames"
        
        while self.is_recording:
            if frames_dir.exists():
                frame_files = list(frames_dir.glob("frame_*.png"))
                count = len(frame_files)
                
                # Update on main thread
                self.root.after(0, lambda c=count: self.frames_label.config(
                    text=f"📁 Frames: {c} (Recording...)"
                ))
            
            time.sleep(0.5)  # Update every half second during recording
    
    def _clear_frames(self):
        """Clear all frames from the frames directory."""
        frames_dir = SIMULATION_DIR / "frames"
        
        # Check if directory exists
        if not frames_dir.exists():
            messagebox.showinfo("No Frames", "Frames directory doesn't exist yet.")
            return
        
        # Check if there are frames
        frame_files = list(frames_dir.glob("frame_*.png"))
        if not frame_files:
            messagebox.showinfo("No Frames", "No frames to clear.")
            return
        
        # Confirmation dialog (IMPORTANT - prevents accidental deletion)
        result = messagebox.askyesno(
            "Confirm Clear",
            f"Are you sure you want to delete {len(frame_files)} frame(s)?\n\n"
            f"This action cannot be undone.",
            icon='warning'
        )
        
        if not result:
            return  # User cancelled
        
        # Disable button during operation
        self.clear_frames_btn.config(state='disabled', text="Clearing...")
        
        # Run in background thread to prevent GUI freezing
        threading.Thread(target=self._clear_frames_thread, daemon=True).start()
    
    def _clear_frames_thread(self):
        """Clear frames in background thread."""
        try:
            frames_dir = SIMULATION_DIR / "frames"
            deleted_count = 0
            
            # Delete all frame files
            for frame_file in frames_dir.glob("frame_*.png"):
                try:
                    frame_file.unlink()  # Delete file
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {frame_file}: {e}")
            
            # Update UI on main thread
            self.frames_count = 0
            self.root.after(0, lambda: self.frames_label.config(text="📁 Frames: 0"))
            self.root.after(0, lambda: messagebox.showinfo(
                "Success",
                f"Cleared {deleted_count} frame(s) successfully!"
            ))
            self.root.after(0, lambda: self.status_label.config(
                text="Frames cleared", 
                fg='#94a3b8'
            ))
            
        except Exception as e:
            # Handle errors on main thread
            self.root.after(0, lambda: messagebox.showerror(
                "Error", 
                f"Error clearing frames:\n{str(e)}"
            ))
        finally:
            # Re-enable button on main thread
            self.root.after(0, lambda: self.clear_frames_btn.config(
                state='normal', 
                text="🗑️ Clear Frames"
            ))
    
    def _open_frames_folder(self):
        """Open the frames folder in file explorer (cross-platform)."""
        frames_dir = SIMULATION_DIR / "frames"
        
        # Create directory if it doesn't exist
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        # Open in file explorer (cross-platform implementation)
        try:
            if sys.platform == 'win32':
                # Windows
                os.startfile(frames_dir)
            elif sys.platform == 'darwin':
                # macOS
                subprocess.Popen(['open', str(frames_dir)])
            else:
                # Linux
                subprocess.Popen(['xdg-open', str(frames_dir)])
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"Could not open folder:\n{str(e)}\n\nPath: {frames_dir}"
            )
```

#### Threading Considerations for File Operations

**Why use threads for file operations?**

```python
# ❌ BAD - Deleting many files on main thread freezes GUI
def clear_frames(self):
    for frame in frames:
        frame.unlink()  # GUI freezes here!
    messagebox.showinfo("Done")

# ✅ GOOD - Delete in background, update GUI when done
def clear_frames(self):
    self.button.config(state='disabled')
    threading.Thread(target=self._do_clear, daemon=True).start()

def _do_clear(self):
    for frame in frames:
        frame.unlink()  # Doesn't freeze GUI
    self.root.after(0, lambda: messagebox.showinfo("Done"))
```

**Rules for threading:**
- File operations (delete, move, read): Use background thread
- GUI updates: Always use `root.after(0, lambda: ...)` from background threads
- Network requests: Always use background thread
- Quick operations (<100ms): Can run on main thread

#### Cross-Platform File Explorer Opening

Different operating systems require different commands to open folders:

```python
def open_folder_cross_platform(folder_path):
    """Open folder in file explorer (works on Windows, macOS, Linux)."""
    try:
        if sys.platform == 'win32':
            # Windows: Use os.startfile
            os.startfile(folder_path)
        elif sys.platform == 'darwin':
            # macOS: Use 'open' command
            subprocess.Popen(['open', str(folder_path)])
        else:
            # Linux: Use 'xdg-open' command
            subprocess.Popen(['xdg-open', str(folder_path)])
    except Exception as e:
        # If opening fails, at least show the path
        messagebox.showerror(
            "Error",
            f"Could not open folder:\n{str(e)}\n\nPath: {folder_path}"
        )
```

**Important notes:**
- Always convert paths to strings for subprocess
- Use `Popen()` instead of `run()` to avoid blocking
- Always include error handling with path display
- Create directory first if it might not exist

---

### Control Panel GUI Recommendations

Follow these guidelines for a consistent, professional control panel experience.

#### Layout Structure

Organize your control panel into logical sections:

```python
def _create_widgets(self):
    """Create all GUI widgets in organized sections."""
    main_frame = tk.Frame(self.root, bg='#0f172a')
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # 1. Title and Description
    self._create_header(main_frame)
    
    # 2. Window Settings (size, FPS)
    self._create_window_settings(main_frame)
    
    # 3. Simulation Settings (plugin-specific)
    self._create_simulation_settings(main_frame)
    
    # 4. Recording Options
    self._create_recording_settings(main_frame)
    
    # 5. Status Display
    self._create_status_display(main_frame)
    
    # 6. Control Buttons
    self._create_control_buttons(main_frame)
    
    # 7. Frame Management
    self._create_frame_management(main_frame)
```

#### Visual Design Standards

Use consistent colors and styling:

```python
# Modern color scheme (dark theme)
COLORS = {
    'bg_main': '#0f172a',      # Dark blue background
    'bg_section': '#1e293b',    # Lighter section background
    'text_primary': '#e2e8f0',  # Light gray text
    'text_secondary': '#94a3b8',# Muted text
    'accent_green': '#10b981',  # Success/positive
    'accent_red': '#ef4444',    # Recording/danger
    'accent_blue': '#3b82f6',   # Info/neutral
    'accent_purple': '#8b5cf6', # Special actions
    'accent_orange': '#f97316', # Warning/delete
    'accent_cyan': '#06b6d4',   # Utility
}

# Apply consistent styling
style = ttk.Style()
style.theme_use('clam')
style.configure('TLabel', 
    background=COLORS['bg_main'], 
    foreground=COLORS['text_primary'], 
    font=('Segoe UI', 10)
)
style.configure('Title.TLabel', 
    font=('Segoe UI', 18, 'bold'), 
    foreground=COLORS['accent_green']
)
```

#### Button Design Guidelines

**Primary Action (Launch):**
```python
launch_btn = tk.Button(
    parent,
    text="🚀 Launch Simulation",
    command=self._launch,
    bg='#10b981',      # Green for primary action
    fg='white',
    activebackground='#059669',  # Darker green on hover
    font=('Segoe UI', 11, 'bold'),
    relief='flat',
    cursor='hand2',
    padx=15,
    pady=10
)
```

**Secondary Actions (Generate Video):**
```python
video_btn = tk.Button(
    parent,
    text="🎬 Generate Video",
    command=self._generate_video,
    bg='#8b5cf6',      # Purple for secondary action
    fg='white',
    activebackground='#7c3aed',
    font=('Segoe UI', 10, 'bold'),
    relief='flat',
    cursor='hand2',
    padx=15,
    pady=8
)
```

**Destructive Actions (Clear/Delete):**
```python
clear_btn = tk.Button(
    parent,
    text="🗑️ Clear Frames",
    command=self._clear_frames,
    bg='#f97316',      # Orange for warning/destructive
    fg='white',
    activebackground='#ea580c',
    font=('Segoe UI', 10, 'bold'),
    relief='flat',
    cursor='hand2',
    padx=15,
    pady=8
)
```

#### Status Display Best Practices

Show clear feedback to users:

```python
# Status label with color-coded states
self.status_label = tk.Label(
    status_frame,
    text="Ready to launch",
    bg='#1e293b',
    fg='#94a3b8',  # Muted gray for idle
    font=('Segoe UI', 10)
)

# Update status with appropriate colors
def update_status(self, message, state):
    """Update status with color-coded message."""
    colors = {
        'idle': '#94a3b8',      # Gray
        'running': '#10b981',   # Green
        'recording': '#ef4444', # Red
        'processing': '#8b5cf6',# Purple
        'error': '#ef4444',     # Red
        'success': '#10b981'    # Green
    }
    
    self.status_label.config(
        text=message,
        fg=colors.get(state, '#94a3b8')
    )

# Examples:
self.update_status("Simulation running", 'running')
self.update_status("Recording...", 'recording')
self.update_status("Generating video...", 'processing')
self.update_status("Video generated!", 'success')
self.update_status("Error occurred", 'error')
```

#### Frame Counter Display

Make frame count prominent and informative:

```python
# Prominent frame counter with icon
self.frames_label = tk.Label(
    status_frame,
    text="📁 Frames: 0",
    bg='#1e293b',
    fg='#3b82f6',  # Blue for info
    font=('Segoe UI', 11, 'bold')  # Slightly larger, bold
)

# Update with state indication
def update_frame_count(self, count, is_recording=False):
    """Update frame counter display."""
    if is_recording:
        text = f"📁 Frames: {count} (Recording...)"
        color = '#ef4444'  # Red during recording
    else:
        text = f"📁 Frames: {count}"
        color = '#3b82f6'  # Blue when idle
    
    self.frames_label.config(text=text, fg=color)
```

#### Confirmation Dialogs

Always confirm destructive actions:

```python
# Good confirmation dialog
result = messagebox.askyesno(
    "Confirm Clear",
    f"Are you sure you want to delete {count} frame(s)?\n\n"
    f"This action cannot be undone.",
    icon='warning'
)

if result:
    # User confirmed - proceed with deletion
    self._perform_deletion()
else:
    # User cancelled - do nothing
    return
```

**When to use confirmations:**
- ✅ Deleting frames
- ✅ Clearing data
- ✅ Overwriting files
- ❌ Opening folders
- ❌ Launching simulation
- ❌ Starting recording

#### Responsive Button States

Disable buttons appropriately:

```python
def _launch(self):
    """Launch simulation."""
    # Disable launch button (prevent multiple launches)
    self.launch_btn.config(state='disabled')
    
    # Enable recording controls (now that sim is running)
    self.record_btn.config(state='normal')
    
    # Launch simulation...
    self.sim_process = subprocess.Popen(cmd)

def _on_simulation_end(self):
    """Handle simulation end."""
    # Re-enable launch button
    self.launch_btn.config(state='normal')
    
    # Disable recording controls (sim not running)
    self.record_btn.config(state='disabled')
    
    # Enable video generation if frames exist
    if self.frames_count > 0:
        self.video_btn.config(state='normal')
```

**Button state rules:**
- Launch button: Enabled when sim not running
- Record button: Enabled only when sim is running
- Video button: Enabled only when frames exist
- Clear button: Always enabled (checks frames in handler)
- Open folder button: Always enabled (creates folder if needed)

---

## Base Simulation Class Reference

### Import

```python
from shared.base_simulation import BaseSimulation
```

### Class Definition

```python
class YourSimulation(BaseSimulation):
    def __init__(self):
        super().__init__(width=1200, height=800, fps=60, title="My Sim")
```

### Constructor Parameters

- `width` (int): Window width in pixels (default: 1200)
- `height` (int): Window height in pixels (default: 700)
- `fps` (int): Target frames per second (default: 60)
- `title` (str): Window title (default: "Simulation")

### Provided Properties

After calling `super().__init__()`, you have access to:

| Property | Type | Description |
|----------|------|-------------|
| `self.width` | int | Window width |
| `self.height` | int | Window height |
| `self.fps` | int | Target FPS |
| `self.title` | str | Window title |
| `self.screen` | pygame.Surface | Main display surface |
| `self.clock` | pygame.time.Clock | Pygame clock for timing |
| `self.font` | pygame.font.Font | Default font (Arial, 24px) |
| `self.running` | bool | Main loop flag |
| `self.paused` | bool | Pause state flag |
| `self.recording` | bool | Recording state |
| `self.frame_count` | int | Number of frames recorded |
| `self.frames_folder` | str | Path to frames directory |

### Required Methods (Must Implement)

#### 1. `handle_events(self)`

Handle pygame events (keyboard, mouse, etc.).

```python
def handle_events(self):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            self.running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
```

#### 2. `update(self)`

Update simulation state. Called each frame when not paused.

```python
def update(self):
    # Update physics, positions, states, etc.
    for entity in self.entities:
        entity.update()
```

#### 3. `draw(self)`

Render the simulation. Called every frame.

```python
def draw(self):
    self.screen.fill((0, 0, 0))  # Clear screen
    
    # Draw your visualization
    for entity in self.entities:
        entity.draw(self.screen)
```

### Provided Methods

#### `setup_frames_folder(folder_path=None)`

Create frames directory for recording.

```python
self.frames_folder = str(current_dir / "frames")
self.setup_frames_folder(self.frames_folder)
```

#### `start_recording()`

Begin saving frames.

```python
self.start_recording()
print("Recording started")
```

#### `stop_recording()`

Stop saving frames.

```python
self.stop_recording()
print(f"Saved {self.frame_count} frames")
```

#### `save_frame()`

Manually save current frame (usually called automatically).

```python
if self.recording:
    self.save_frame()
```

#### `run()`

Start the main simulation loop. Call this once at the end.

```python
if __name__ == "__main__":
    sim = MySimulation()
    sim.run()
```

#### `quit()`

Clean up and exit.

```python
self.quit()
```

### Main Loop Behavior

When you call `sim.run()`, the base class does:

```python
while self.running:
    self.handle_events()
    
    if not self.paused:
        self.update()
    
    self.draw()
    
    if self.recording:
        self.save_frame()
    
    pygame.display.flip()
    self.clock.tick(self.fps)

pygame.quit()
```

You don't need to implement this yourself!

---

## simulation.json Schema

### Complete Schema with Explanations

```json
{
  "id": "unique_identifier",
  "name": "Display Name",
  "description": "Detailed description of what this plugin does.",
  "icon": "🎮",
  "color": "#3b82f6",
  "version": "1.0.0",
  "author": "Your Name or Organization",
  "license": "MIT",
  "homepage": "https://github.com/you/your-plugin",
  "min_loops_version": "1.0.0",
  "tags": ["category", "type", "feature"],
  "requires_pygame": true,
  "entry_point": "main.py",
  "control_panel": "control_panel.py",
  "dependencies": []
}
```

### Field Details

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | string | ✅ Yes | Unique identifier. **MUST** be lowercase with underscores only. | `"bouncing_balls"` |
| `name` | string | ✅ Yes | User-facing display name. Can have spaces and capitals. | `"Bouncing Balls"` |
| `description` | string | ✅ Yes | Clear explanation of what the plugin does. | `"Physics simulation showing realistic ball collisions with gravity."` |
| `icon` | string | ✅ Yes | Single emoji representing the plugin. | `"⚽"` |
| `color` | string | ✅ Yes | Hex color for dashboard card. | `"#10b981"` |
| `version` | string | ✅ Yes | Semantic version number. | `"1.0.0"` |
| `author` | string | ✅ Yes | Creator name or organization. | `"Jane Doe"` |
| `license` | string | ✅ Yes | License type. | `"MIT"` |
| `homepage` | string | ❌ No | URL to documentation or repo. | `"https://github.com/..."` |
| `min_loops_version` | string | ✅ Yes | Minimum Loops version required. | `"1.0.0"` |
| `tags` | array | ✅ Yes | List of category tags for filtering. | `["physics", "simulation"]` |
| `requires_pygame` | boolean | ✅ Yes | **Must** be `true` for pygame sims. | `true` |
| `entry_point` | string | ✅ Yes | **Must** be `"main.py"`. | `"main.py"` |
| `control_panel` | string | ✅ Yes | **Must** be `"control_panel.py"`. | `"control_panel.py"` |
| `dependencies` | array | ❌ No | Extra Python packages needed. | `["numpy", "scipy"]` |

### Validation Rules

1. **`id` format**: Must match regex `^[a-z0-9_]+$` (lowercase, numbers, underscores only)
2. **`icon`**: Must be a single emoji character
3. **`color`**: Must be valid hex color starting with `#`
4. **`version`**: Should follow semantic versioning (major.minor.patch)
5. **`requires_pygame`**: Must be `true` for pygame-based plugins
6. **`entry_point`**: Must be `"main.py"`
7. **`control_panel`**: Must be `"control_panel.py"`

### Example - Complete

```json
{
  "id": "particle_life",
  "name": "Particle Life",
  "description": "Self-organizing particle system with emergent behavior. Particles attract and repel based on color, creating life-like patterns.",
  "icon": "✨",
  "color": "#8b5cf6",
  "version": "1.2.0",
  "author": "Complexity Labs",
  "license": "MIT",
  "homepage": "https://github.com/complexity-labs/particle-life",
  "min_loops_version": "1.0.0",
  "tags": ["particles", "emergence", "complexity", "art"],
  "requires_pygame": true,
  "entry_point": "main.py",
  "control_panel": "control_panel.py",
  "dependencies": ["numpy"]
}
```

---

## Important Rules and Best Practices

### Path Handling

**❌ NEVER use hardcoded paths:**
```python
# WRONG
frames_folder = "E:/loops/simulations/my_plugin/frames"
```

**✅ ALWAYS use relative paths from `__file__`:**
```python
# CORRECT
from pathlib import Path

current_dir = Path(__file__).parent
frames_folder = current_dir / "frames"
```

This ensures your plugin works on any system and any location.

### Import Shared Modules

To import `BaseSimulation` and other shared modules:

```python
import sys
from pathlib import Path

current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent
shared_dir = root_dir / "shared"
sys.path.insert(0, str(shared_dir))

from base_simulation import BaseSimulation
```

### Clean Simulation Windows

**The simulation window should be CLEAN:**
- Minimal UI overlays
- No control buttons
- No complex status displays
- Focus on the visualization

**Good UI elements:**
- Small recording indicator (● REC)
- Pause indicator in center when paused
- Frame count in corner (optional)

**Bad UI elements:**
- Sliders
- Buttons
- Dropdowns
- Text input fields

**All controls belong in the control panel!**

### Frame Saving Best Practices

1. **Always use zero-padded numbering**: `frame_{count:06d}.png`
2. **Create frames directory at startup**: `self.setup_frames_folder()`
3. **Handle recording state properly**: Check `self.recording` before saving
4. **Use the base class method**: Don't reimplement frame saving
5. **Clear old frames before recording**: Either automatically or via control panel

### Subprocess Best Practices

In control panel, use `subprocess.Popen()`, not `subprocess.run()`:

```python
# ✅ CORRECT - Non-blocking
subprocess.Popen([sys.executable, "main.py"])

# ❌ WRONG - Blocks control panel
subprocess.run([sys.executable, "main.py"])
```

### Error Handling

Always wrap risky operations in try-except:

```python
try:
    response = requests.post(...)
    if response.status_code == 200:
        # Success
    else:
        messagebox.showerror("Error", f"API error: {response.status_code}")
except Exception as e:
    messagebox.showerror("Error", f"Failed: {str(e)}")
```

### Performance Tips

1. **Limit frame rate**: Use `self.clock.tick(self.fps)` from base class
2. **Optimize drawing**: Only redraw what changes
3. **Use pygame efficiently**: Batch `blit()` calls, use `convert_alpha()`
4. **Consider frame size**: Larger frames = larger file sizes

---

## Testing Your Plugin

### Manual Testing Checklist

Before packaging, test these scenarios:

#### 1. Control Panel
- [ ] Opens without errors
- [ ] All controls are functional
- [ ] Window is properly sized and styled
- [ ] Launch button works
- [ ] Frame management works (refresh, clear, open folder)

#### 2. Simulation
- [ ] Launches from control panel
- [ ] Window displays correctly
- [ ] Visualization renders properly
- [ ] Keyboard controls work (especially ESC, SPACE, R, S)
- [ ] Can toggle recording with 'S' key
- [ ] Frames are saved correctly

#### 3. Frame Management
- [ ] Frames directory is created
- [ ] Frames are numbered sequentially
- [ ] Frame count is accurate
- [ ] Clear frames button works
- [ ] Open folder button works

#### 4. Video Generation
- [ ] Generate video button is enabled when frames exist
- [ ] Settings dialog appears
- [ ] Video generation completes without errors
- [ ] Video file is created in correct location
- [ ] Video plays correctly

#### 5. Integration
- [ ] Plugin appears in dashboard (if testing via dashboard)
- [ ] simulation.json is valid
- [ ] No import errors
- [ ] Works on fresh Python environment

### Testing Commands

```bash
# Test control panel directly
cd simulations/your_plugin
python control_panel.py

# Test simulation directly
python main.py

# Test with command-line args
python main.py --width 800 --height 600 --fps 30 --record

# Test imports
python -c "from your_plugin import main; print('OK')"
```

### Common Issues

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| ImportError: No module named 'base_simulation' | Path not added to sys.path | Add shared directory to sys.path |
| Frames not saving | frames_folder not set correctly | Use `Path(__file__).parent / "frames"` |
| Control panel crashes on launch | subprocess.run() instead of Popen() | Change to subprocess.Popen() |
| Video generation fails | FFmpeg not installed | Ensure FFmpeg is in PATH |
| Simulation window blank | draw() not implemented | Implement draw() method |
| No frames created | Recording not started | Call self.start_recording() |

---

## Packaging and Distribution

### Files to Include

```
your_plugin/
├── __init__.py
├── simulation.json
├── main.py
├── control_panel.py
├── README.md
└── [any additional resources]
```

### Files to EXCLUDE

- **DO NOT include:**
  - `__pycache__/` directories
  - `.pyc` files
  - `frames/` directory
  - Large test files
  - `.git/` directory

### Creating a ZIP Package

**On Windows:**
```bash
cd simulations
powershell Compress-Archive -Path your_plugin -DestinationPath your_plugin.zip
```

**On Linux/Mac:**
```bash
cd simulations
zip -r your_plugin.zip your_plugin/ -x "*/frames/*" "*/__pycache__/*" "*.pyc"
```

### README Template

Create a `README.md` in your plugin directory:

```markdown
# [Plugin Name]

[Brief description]

## Features

- Feature 1
- Feature 2
- Feature 3

## Controls

- **SPACE**: Pause/Resume
- **R**: Reset
- **S**: Start/Stop Recording
- **ESC**: Exit

## Settings

Describe what each control panel setting does.

## Requirements

- Python 3.8+
- pygame
- [any other dependencies]

## Author

[Your Name]

## License

MIT
```

---

## Complete Working Example

### Reference: Sorting Circles

The `sorting_circles` plugin is a complete, production-ready example. Here's its structure:

```
simulations/sorting_circles/
├── __init__.py              # Package initialization
├── simulation.json          # Metadata
├── main.py                  # Sorting visualization (414 lines)
├── control_panel.py         # Tkinter control panel (282 lines)
├── README.md                # Documentation
└── frames/                  # Created at runtime
```

### Key Aspects to Study

#### 1. **simulation.json** (sorting_circles)
```json
{
  "id": "sorting_circles",
  "name": "Sorting Circles",
  "description": "Visualize sorting algorithms using circles arranged in a radial pattern.",
  "icon": "⭕",
  "color": "#10b981",
  "version": "1.0.0",
  "author": "Loops Community",
  "license": "MIT",
  "requires_pygame": true,
  "entry_point": "main.py",
  "control_panel": "control_panel.py"
}
```

#### 2. **Path Handling** (main.py)
```python
from pathlib import Path

current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent
shared_dir = root_dir / "shared"
sys.path.insert(0, str(shared_dir))

# Frames folder
self.frames_folder = str(current_dir / "frames")
```

#### 3. **Control Panel Structure** (control_panel.py)
- Window settings (size, FPS)
- Algorithm selection (radio buttons)
- Array size (spinbox)
- Auto-record checkbox
- Launch button that uses subprocess.Popen()

#### 4. **Simulation Features** (main.py)
- Inherits from BaseSimulation
- Implements handle_events(), update(), draw()
- Uses generator-based sorting algorithms for smooth animation
- Supports recording with 'S' key
- Clean, minimal UI (just recording indicator)

#### 5. **Frame Management**
```python
# In __init__
self.frames_folder = str(current_dir / "frames")
self.setup_frames_folder(self.frames_folder)

# In handle_events
if event.key == pygame.K_s:
    if self.recording:
        self.stop_recording()
    else:
        self.start_recording()
```

### Where to Find Examples

Look at these files in the Loops repository:
- `simulations/sorting_circles/` - Simple, well-structured example
- `simulations/sorting_visualizer/` - More complex with comparison mode
- `shared/base_simulation.py` - Base class reference
- `backend/server.py` - Video generation API (line 387)

---

## Summary Checklist

Use this checklist when creating a plugin:

### Structure
- [ ] Created `__init__.py`
- [ ] Created `simulation.json` with all required fields
- [ ] Created `main.py` with simulation logic
- [ ] Created `control_panel.py` with Tkinter GUI
- [ ] Created `README.md` with documentation

### simulation.json
- [ ] `id` is lowercase with underscores only
- [ ] Icon is a single emoji
- [ ] Color is valid hex
- [ ] `entry_point` is `"main.py"`
- [ ] `control_panel` is `"control_panel.py"`
- [ ] `requires_pygame` is `true`

### main.py
- [ ] Imports BaseSimulation correctly
- [ ] Uses relative paths (Path(__file__).parent)
- [ ] Implements handle_events()
- [ ] Implements update()
- [ ] Implements draw()
- [ ] Sets up frames folder correctly
- [ ] Supports command-line arguments
- [ ] Has recording toggle (S key)

### control_panel.py
- [ ] Has window settings section
- [ ] Has simulation-specific settings
- [ ] Has recording checkbox
- [ ] Has frame management section (count, clear, open)
- [ ] Has video generation button
- [ ] Has launch button
- [ ] Uses subprocess.Popen() not .run()
- [ ] Handles errors gracefully

### Frame Management
- [ ] Creates frames/ directory
- [ ] Uses correct naming: frame_000001.png
- [ ] Implements start/stop recording
- [ ] Frame count updates correctly
- [ ] Clear frames works

### Video Generation
- [ ] Uses VideoGenerator directly (imports from `shared.video_generator`)
- [ ] Does NOT use HTTP API endpoints
- [ ] Parameter is `frame_folder` (singular, string) not `frame_folders` (plural, list)
- [ ] Sends absolute path to frame directory
- [ ] Provides all required parameters (frame_folder, output_name, fps, quality)
- [ ] Runs in background thread (doesn't freeze GUI)
- [ ] Handles ImportError, FileNotFoundError, ValueError
- [ ] Shows progress indicator during generation
- [ ] Updates UI using `root.after()` from threads
- [ ] Opens output folder on success (optional)

### Frame Management Advanced
- [ ] Frame counter displays and updates automatically
- [ ] Clear frames button with confirmation dialog
- [ ] Open folder button works cross-platform
- [ ] Frame clearing runs in background thread
- [ ] Monitoring updates during recording
- [ ] Buttons enable/disable based on state
- [ ] All file operations have error handling

### Testing
- [ ] Control panel opens without errors
- [ ] Simulation launches from control panel
- [ ] Recording works correctly
- [ ] Video generation completes successfully
- [ ] All keyboard controls work
- [ ] Works as standalone (python main.py)

---

## Final Notes

### This Document is Your Bible

If you follow every instruction in this guide, your plugin WILL work. If it doesn't:
1. Re-read the relevant section
2. Check the example (sorting_circles)
3. Verify paths are relative, not absolute
4. Ensure all required files exist
5. Test each component individually

### Key Principles to Remember

1. **Two Windows**: Control panel (Tkinter) + Simulation (pygame)
2. **Clean Simulation**: NO controls in pygame window
3. **Relative Paths**: Always use `Path(__file__).parent`
4. **Sequential Frames**: `frame_{count:06d}.png`
5. **Separate Processes**: Use subprocess.Popen()

### What Makes a Great Plugin

- **Clear purpose**: Obvious what it visualizes
- **Good controls**: Easy to adjust parameters
- **Beautiful visuals**: Clean, colorful, smooth
- **Performant**: Runs at target FPS
- **Well-documented**: Clear README
- **Reliable**: Handles errors gracefully

---

**Good luck creating amazing visualizations for Loops!** 🚀
