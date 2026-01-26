#!/usr/bin/env python3
# control_panel.py - Master Control Panel for Sorting Visualizer

"""
Sorting Visualizer Control Panel
================================
A tkinter-based control panel for managing sorting simulations.

Features:
- Select sorting algorithm
- Adjust speed settings
- View frame count
- Clear frames folder
- Launch simulator
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import subprocess
import threading

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FRAMES_FOLDER = os.path.join(SCRIPT_DIR, "frames")

# Sorting algorithms
ALGORITHMS = ["Bubble Sort", "Quick Sort", "Merge Sort"]


class ControlPanel:
    """Master control panel for sorting visualizer."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sorting Visualizer - Control Panel")
        self.root.geometry("500x800")
        self.root.resizable(False, False)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.algorithm_var = tk.StringVar(value=ALGORITHMS[0])
        self.speed_var = tk.IntVar(value=5)
        self.num_bars_var = tk.IntVar(value=200)
        self.save_frames_var = tk.BooleanVar(value=True)
        
        # Build UI
        self._create_header()
        self._create_algorithm_section()
        self._create_settings_section()
        self._create_frames_section()
        self._create_run_button()
        
        # Update frame count initially
        self._update_frame_count()
        
    def _create_header(self):
        """Create header section."""
        header = ttk.Frame(self.root, padding=20)
        header.pack(fill=tk.X)
        
        title = ttk.Label(
            header, 
            text="🔄 Sorting Visualizer", 
            font=('Arial', 24, 'bold')
        )
        title.pack()
        
        subtitle = ttk.Label(
            header,
            text="Control Panel",
            font=('Arial', 12)
        )
        subtitle.pack()
        
    def _create_algorithm_section(self):
        """Create algorithm selection section."""
        frame = ttk.LabelFrame(self.root, text="Algorithm Selection", padding=15)
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        for algo in ALGORITHMS:
            rb = ttk.Radiobutton(
                frame,
                text=algo,
                value=algo,
                variable=self.algorithm_var
            )
            rb.pack(anchor=tk.W, pady=3)
    
    def _create_settings_section(self):
        """Create settings section."""
        frame = ttk.LabelFrame(self.root, text="Settings", padding=15)
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Speed control
        speed_frame = ttk.Frame(frame)
        speed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_label = ttk.Label(speed_frame, text=f"{self.speed_var.get()}x")
        self.speed_label.pack(side=tk.RIGHT)
        
        speed_scale = ttk.Scale(
            frame,
            from_=1,
            to=50,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=self._on_speed_change
        )
        speed_scale.pack(fill=tk.X, pady=5)
        
        # Number of bars
        bars_frame = ttk.Frame(frame)
        bars_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(bars_frame, text="Number of Bars:").pack(side=tk.LEFT)
        self.bars_label = ttk.Label(bars_frame, text=str(self.num_bars_var.get()))
        self.bars_label.pack(side=tk.RIGHT)
        
        bars_scale = ttk.Scale(
            frame,
            from_=50,
            to=400,
            orient=tk.HORIZONTAL,
            variable=self.num_bars_var,
            command=self._on_bars_change
        )
        bars_scale.pack(fill=tk.X, pady=5)
        
        # Save frames checkbox
        save_cb = ttk.Checkbutton(
            frame,
            text="Save frames for video rendering",
            variable=self.save_frames_var
        )
        save_cb.pack(anchor=tk.W, pady=10)
    
    def _create_frames_section(self):
        """Create frames management section."""
        frame = ttk.LabelFrame(self.root, text="Frames", padding=15)
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Frame count display
        count_frame = ttk.Frame(frame)
        count_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(count_frame, text="Saved Frames:").pack(side=tk.LEFT)
        self.frame_count_label = ttk.Label(count_frame, text="0", font=('Arial', 12, 'bold'))
        self.frame_count_label.pack(side=tk.RIGHT)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        refresh_btn = ttk.Button(
            btn_frame,
            text="🔄 Refresh",
            command=self._update_frame_count
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(
            btn_frame,
            text="🗑️ Clear Frames",
            command=self._clear_frames
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        open_btn = ttk.Button(
            btn_frame,
            text="📂 Open Folder",
            command=self._open_frames_folder
        )
        open_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_run_button(self):
        """Create run simulation button."""
        btn_frame = ttk.Frame(self.root, padding=20)
        btn_frame.pack(fill=tk.X)
        
        run_btn = tk.Button(
            btn_frame,
            text="▶️  RUN SIMULATION",
            font=('Arial', 16, 'bold'),
            bg='#4CAF50',
            fg='white',
            activebackground='#45a049',
            height=2,
            command=self._run_simulation
        )
        run_btn.pack(fill=tk.X)
    
    def _on_speed_change(self, value):
        """Handle speed slider change."""
        self.speed_label.config(text=f"{int(float(value))}x")
    
    def _on_bars_change(self, value):
        """Handle bars slider change."""
        self.bars_label.config(text=str(int(float(value))))
    
    def _update_frame_count(self):
        """Update the frame count display."""
        if os.path.exists(FRAMES_FOLDER):
            count = len([f for f in os.listdir(FRAMES_FOLDER) if f.endswith('.png')])
        else:
            count = 0
        self.frame_count_label.config(text=str(count))
    
    def _clear_frames(self):
        """Clear all frames from the folder."""
        if not os.path.exists(FRAMES_FOLDER):
            messagebox.showinfo("Info", "Frames folder is empty.")
            return
        
        count = len([f for f in os.listdir(FRAMES_FOLDER) if f.endswith('.png')])
        if count == 0:
            messagebox.showinfo("Info", "No frames to clear.")
            return
        
        if messagebox.askyesno("Confirm", f"Delete {count} frames?"):
            for f in os.listdir(FRAMES_FOLDER):
                if f.endswith('.png'):
                    os.remove(os.path.join(FRAMES_FOLDER, f))
            self._update_frame_count()
            messagebox.showinfo("Success", "Frames cleared!")
    
    def _open_frames_folder(self):
        """Open frames folder in file explorer."""
        if not os.path.exists(FRAMES_FOLDER):
            os.makedirs(FRAMES_FOLDER)
        
        if sys.platform == 'win32':
            os.startfile(FRAMES_FOLDER)
        elif sys.platform == 'darwin':
            subprocess.run(['open', FRAMES_FOLDER])
        else:
            subprocess.run(['xdg-open', FRAMES_FOLDER])
    
    def _run_simulation(self):
        """Launch the simulation with current settings."""
        # Prepare settings
        algorithm = self.algorithm_var.get()
        speed = int(self.speed_var.get())
        num_bars = int(self.num_bars_var.get())
        save_frames = self.save_frames_var.get()
        
        # Create a settings file that the visualizer will read
        settings_file = os.path.join(SCRIPT_DIR, "runtime_settings.py")
        with open(settings_file, 'w') as f:
            f.write(f"# Runtime settings from control panel\n")
            f.write(f"ALGORITHM = \"{algorithm}\"\n")
            f.write(f"SPEED = {speed}\n")
            f.write(f"NUM_BARS = {num_bars}\n")
            f.write(f"SAVE_FRAMES = {save_frames}\n")
            f.write(f"AUTO_START = True\n")
        
        # Launch visualizer in new process
        visualizer_path = os.path.join(SCRIPT_DIR, "main.py")
        
        def run_visualizer():
            subprocess.run([sys.executable, visualizer_path])
            # Refresh frame count after simulation ends
            self.root.after(100, self._update_frame_count)
        
        # Run in separate thread to keep control panel responsive
        thread = threading.Thread(target=run_visualizer, daemon=True)
        thread.start()
    
    def run(self):
        """Start the control panel."""
        self.root.mainloop()


def main():
    """Entry point."""
    panel = ControlPanel()
    panel.run()


if __name__ == "__main__":
    main()
