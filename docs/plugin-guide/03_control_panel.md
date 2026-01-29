# Plugin Development Guide - Part 3: Control Panel

## 📚 Table of Contents
- [Overview](#overview)
- [Control Panel Architecture](#control-panel-architecture)
- [Complete Template](#complete-template)
- [Essential Sections](#essential-sections)
- [Layout Best Practices](#layout-best-practices)
- [Launching the Simulation](#launching-the-simulation)

---

## Overview

The control panel is a Tkinter-based GUI that:
- Configures simulation settings
- Launches the simulation in a separate process
- Manages frames and video generation
- Provides a professional user interface

---

## Control Panel Architecture

### Window Structure

```
┌─────────────────────────────────────┐
│         Title & Description         │
├─────────────┬───────────────────────┤
│   Window    │   Algorithm Settings  │
│   Settings  │                       │
├─────────────┼───────────────────────┤
│   Visual    │   Recording Settings  │
│   Settings  │                       │
├─────────────┴───────────────────────┤
│        Frame Management             │
│  [Refresh] [Clear] [Open] [Video]  │
├─────────────────────────────────────┤
│      [LAUNCH VISUALIZATION]         │
└─────────────────────────────────────┘
```

### Key Components

1. **Settings Sections**: LabelFrame widgets for organization
2. **Input Widgets**: Entry, Spinbox, Scale, Combobox, Checkbutton
3. **Frame Management**: Buttons for frame operations
4. **Launch Button**: Large prominent button
5. **Status Display**: Frame count, etc.

---

## Complete Template

```python
#!/usr/bin/env python3
"""
[Plugin Name] - Control Panel
==============================
Tkinter-based GUI for configuring and launching the simulation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading
import shutil
import requests
import time
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
        self.root.geometry("900x650")  # Horizontal layout
        self.root.configure(bg='#0f172a')
        
        # Style configuration
        self._configure_styles()
        
        # Variables
        self.width_var = tk.StringVar(value="1200")
        self.height_var = tk.StringVar(value="800")
        self.fps_var = tk.StringVar(value="60")
        self.auto_record_var = tk.BooleanVar(value=False)
        
        # Add your custom variables here
        self.custom_var = tk.IntVar(value=100)
        
        # Video settings
        self.video_fps_var = tk.StringVar(value="60")
        self.video_quality_var = tk.StringVar(value="high")
        
        # Process tracking
        self.simulation_process = None
        
        # Build UI
        self._create_widgets()
        
        # Update frame count
        self._update_frame_count()
        
        # Start auto-refresh
        self._auto_refresh_frames()
    
    def _configure_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#0f172a', foreground='#e2e8f0', 
                       font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'), 
                       foreground='#10b981')
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = tk.Frame(self.root, bg='#0f172a')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Title section
        title_frame = tk.Frame(main_frame, bg='#0f172a')
        title_frame.pack(fill='x', pady=(0, 10))
        
        title = ttk.Label(
            title_frame,
            text="🎮 [Plugin Name]",
            style='Title.TLabel'
        )
        title.pack()
        
        subtitle = ttk.Label(
            title_frame,
            text="Brief description",
            font=('Segoe UI', 9),
            foreground='#94a3b8'
        )
        subtitle.pack()
        
        # Top row: Two columns side by side
        top_row = tk.Frame(main_frame, bg='#0f172a')
        top_row.pack(fill='x', pady=(0, 10))
        
        # Left column
        left_col = tk.Frame(top_row, bg='#0f172a')
        left_col.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self._create_window_settings(left_col)
        self._create_custom_settings(left_col)
        
        # Right column
        right_col = tk.Frame(top_row, bg='#0f172a')
        right_col.pack(side='left', fill='both', expand=True, padx=(5, 0))
        
        self._create_recording_settings(right_col)
        
        # Bottom section
        bottom_frame = tk.Frame(main_frame, bg='#0f172a')
        bottom_frame.pack(fill='both', expand=True)
        
        self._create_frame_management(bottom_frame)
        self._create_launch_button(bottom_frame)
    
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
        frame.pack(fill='x', pady=(0, 10))
        
        # Size
        size_frame = tk.Frame(frame, bg='#1e293b')
        size_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(size_frame, text="Size:").pack(side='left')
        ttk.Entry(size_frame, textvariable=self.width_var, width=8).pack(
            side='left', padx=(10, 5))
        ttk.Label(size_frame, text="×").pack(side='left')
        ttk.Entry(size_frame, textvariable=self.height_var, width=8).pack(
            side='left', padx=5)
        
        # FPS
        fps_frame = tk.Frame(frame, bg='#1e293b')
        fps_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(fps_frame, text="FPS:").pack(side='left')
        ttk.Spinbox(fps_frame, from_=30, to=120, textvariable=self.fps_var, 
                   width=8).pack(side='left', padx=10)
    
    def _create_custom_settings(self, parent):
        """Create plugin-specific settings."""
        frame = tk.LabelFrame(
            parent,
            text="🎯 Custom Settings",
            bg='#1e293b',
            fg='#e2e8f0',
            font=('Segoe UI', 11, 'bold'),
            relief='ridge',
            bd=2
        )
        frame.pack(fill='x', pady=(0, 10))
        
        # Example: Slider
        slider_frame = tk.Frame(frame, bg='#1e293b')
        slider_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(slider_frame, text="Setting:").pack(side='left')
        self.custom_label = ttk.Label(slider_frame, text=str(self.custom_var.get()))
        self.custom_label.pack(side='right')
        
        custom_scale = ttk.Scale(
            frame,
            from_=1,
            to=200,
            orient=tk.HORIZONTAL,
            variable=self.custom_var,
            command=lambda v: self.custom_label.config(text=str(int(float(v))))
        )
        custom_scale.pack(fill='x', padx=15, pady=(0, 10))
    
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
        frame.pack(fill='x', pady=(0, 10))
        
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
        frame.pack(fill='x', pady=(0, 10))
        
        # Frame count
        count_frame = tk.Frame(frame, bg='#1e293b')
        count_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(count_frame, text="Frames saved:").pack(side='left')
        self.frame_count_label = ttk.Label(
            count_frame,
            text="0",
            font=('Segoe UI', 10, 'bold'),
            foreground='#10b981'
        )
        self.frame_count_label.pack(side='left', padx=10)
        
        # Buttons
        btn_frame = tk.Frame(frame, bg='#1e293b')
        btn_frame.pack(fill='x', padx=15, pady=10)
        
        tk.Button(
            btn_frame, text="🔄 Refresh", command=self._update_frame_count,
            bg='#3b82f6', fg='white', font=('Segoe UI', 9, 'bold'),
            relief='flat', padx=10, pady=5, cursor='hand2'
        ).pack(side='left', padx=(0, 5))
        
        tk.Button(
            btn_frame, text="🗑️ Clear", command=self._clear_frames,
            bg='#f97316', fg='white', font=('Segoe UI', 9, 'bold'),
            relief='flat', padx=10, pady=5, cursor='hand2'
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame, text="📂 Open", command=self._open_frames_folder,
            bg='#8b5cf6', fg='white', font=('Segoe UI', 9, 'bold'),
            relief='flat', padx=10, pady=5, cursor='hand2'
        ).pack(side='left', padx=5)
        
        # Video button
        tk.Button(
            frame, text="🎥 Generate Video", command=self._show_video_dialog,
            bg='#8b5cf6', fg='white', font=('Segoe UI', 10, 'bold'),
            relief='flat', padx=20, pady=10, cursor='hand2'
        ).pack(padx=15, pady=10, fill='x')
    
    def _create_launch_button(self, parent):
        """Create main launch button."""
        self.launch_btn = tk.Button(
            parent,
            text="🚀 LAUNCH VISUALIZATION",
            command=self._launch_simulation,
            bg='#10b981',
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            relief='flat',
            padx=20,
            pady=12,
            cursor='hand2'
        )
        self.launch_btn.pack(pady=15, fill='x')
        
        shortcuts = ttk.Label(
            parent,
            text="Shortcuts: SPACE=Pause | R=Reset | S=Record | ESC=Exit",
            font=('Segoe UI', 8),
            foreground='#64748b'
        )
        shortcuts.pack()
    
    def _update_frame_count(self):
        """Update frame count display."""
        try:
            if FRAMES_FOLDER.exists():
                count = len(list(FRAMES_FOLDER.glob("frame_*.png")))
                self.frame_count_label.config(text=str(count))
            else:
                self.frame_count_label.config(text="0")
        except Exception as e:
            print(f"Error updating frame count: {e}")
    
    def _auto_refresh_frames(self):
        """Auto-refresh frame count every 2 seconds."""
        self._update_frame_count()
        self.root.after(2000, self._auto_refresh_frames)
    
    def _clear_frames(self):
        """Clear all saved frames."""
        # See Part 5 for full implementation with threading
        pass
    
    def _open_frames_folder(self):
        """Open frames folder in file explorer."""
        try:
            FRAMES_FOLDER.mkdir(parents=True, exist_ok=True)
            
            if sys.platform == 'win32':
                os.startfile(FRAMES_FOLDER)
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(FRAMES_FOLDER)])
            else:
                subprocess.run(['xdg-open', str(FRAMES_FOLDER)])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder:\\n{e}")
    
    def _show_video_dialog(self):
        """Show video generation dialog."""
        # See Part 4 for full implementation
        pass
    
    def _launch_simulation(self):
        """Launch the simulation."""
        try:
            # Get settings
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            fps = int(self.fps_var.get())
            auto_record = self.auto_record_var.get()
            custom_value = self.custom_var.get()
            
            # Build command
            main_script = SIMULATION_DIR / "main.py"
            
            cmd = [
                sys.executable,
                str(main_script),
                "--width", str(width),
                "--height", str(height),
                "--fps", str(fps),
                "--custom", str(custom_value)
            ]
            
            if auto_record:
                cmd.append("--record")
            
            # Launch (non-blocking)
            self.simulation_process = subprocess.Popen(
                cmd,
                cwd=str(SIMULATION_DIR)
            )
            
            messagebox.showinfo(
                "Launched",
                "Visualization launched!\\n\\nCheck the new window."
            )
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Check your settings:\\n{e}")
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch:\\n{e}")
    
    def run(self):
        """Start the control panel."""
        self.root.mainloop()


def main():
    """Entry point."""
    app = ControlPanel()
    app.run()


if __name__ == "__main__":
    main()
```

---

## Essential Sections

### 1. Window Settings (Required)

- Width/Height inputs
- FPS selector
- These control basic simulation properties

### 2. Plugin-Specific Settings

- Customize based on your simulation needs
- Use appropriate widgets:
  - **Slider** (Scale): For continuous ranges
  - **Spinbox**: For numeric input
  - **Combobox**: For predefined choices
  - **Checkbutton**: For toggles

### 3. Recording Settings

- Auto-record checkbox
- Simple but essential

### 4. Frame Management (Required)

- Frame count display (auto-refreshing)
- Refresh button
- Clear frames button (with confirmation)
- Open folder button
- Generate video button

### 5. Launch Button (Required)

- Large, prominent button
- Launches simulation via `subprocess.Popen()` (NOT `.run()`)

---

## Layout Best Practices

### ✅ DO:

```python
# Use horizontal layout for better space utilization
self.root.geometry("900x650")  # Wide, not tall

# Organize in columns
top_row = tk.Frame(main_frame)
top_row.pack(fill='x')

left_col = tk.Frame(top_row)
left_col.pack(side='left', fill='both', expand=True)

right_col = tk.Frame(top_row)
right_col.pack(side='left', fill='both', expand=True)
```

### ❌ DON'T:

```python
# Avoid vertical-only layout that requires scrolling
self.root.geometry("550x1200")  # Too tall!

# Don't pack everything vertically
widget1.pack()  # All widgets stacked = scrollbar needed
widget2.pack()
widget3.pack()
```

---

## Launching the Simulation

### ⚠️ CRITICAL: Use Popen, Not run

**❌ WRONG:**
```python
# This BLOCKS the control panel!
subprocess.run([sys.executable, "main.py"])
```

**✅ CORRECT:**
```python
# This runs in background
self.simulation_process = subprocess.Popen(
    [sys.executable, str(main_script), "--width", "1200"],
    cwd=str(SIMULATION_DIR)
)
```

### Building Commands

```python
def _launch_simulation(self):
    main_script = SIMULATION_DIR / "main.py"
    
    cmd = [
        sys.executable,        # Python interpreter
        str(main_script),      # Script to run
        "--width", "1200",     # Arguments
        "--height", "800",
        "--custom", "value"
    ]
    
    # Add conditional arguments
    if self.auto_record_var.get():
        cmd.append("--record")
    
    # Launch
    process = subprocess.Popen(cmd, cwd=str(SIMULATION_DIR))
```

---

## Next Steps

Control panel complete! Now learn about:

- **Part 4: Video Generation & API** - Integrate video generation properly
- **Part 5: Common Pitfalls** - Avoid mistakes with threading, error handling, etc.

---

## Quick Checklist

- [ ] Horizontal layout (900x650 or similar)
- [ ] Two-column design for settings
- [ ] All required sections present
- [ ] Launch uses `Popen` (not `run`)
- [ ] Frame count auto-refreshes
- [ ] Cross-platform folder opening
- [ ] Professional styling and colors

**Ready for Part 4?** → [Video Generation & API Integration](./04_video_api.md)
