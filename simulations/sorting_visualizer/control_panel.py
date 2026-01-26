#!/usr/bin/env python3
# control_panel.py - Master Control Panel for Sorting Visualizer

"""
Sorting Visualizer Control Panel
================================
A tkinter-based control panel for managing sorting simulations.

Features:
- Select sorting algorithm (single or comparison mode)
- Adjust speed and bar count settings
- View and manage frames for both single and comparison modes
- Generate videos from saved frames
- Launch simulator in separate window
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
COMPARISON_FRAMES_FOLDER = os.path.join(SCRIPT_DIR, "comparison_frames")

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(SCRIPT_DIR)))

# Sorting algorithms
ALGORITHMS = ["Bubble Sort", "Quick Sort", "Merge Sort"]


class ControlPanel:
    """Master control panel for sorting visualizer."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sorting Visualizer - Control Panel")
        self.root.geometry("900x550")
        self.root.resizable(False, False)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.algorithm_var = tk.StringVar(value=ALGORITHMS[0])
        self.speed_var = tk.IntVar(value=5)
        self.num_bars_var = tk.IntVar(value=200)
        self.save_frames_var = tk.BooleanVar(value=True)
        self.mode_var = tk.StringVar(value="single")
        
        # Comparison mode variables
        self.comparison_vars = {algo: tk.BooleanVar(value=False) for algo in ALGORITHMS}
        
        # Build UI
        self._create_header()
        self._create_main_content()
        
        # Update frame counts
        self._update_frame_count()
        self._update_comparison_frame_count()
        self._on_mode_change()
        
    def _create_header(self):
        """Create header section."""
        header = ttk.Frame(self.root, padding=15)
        header.pack(fill=tk.X)
        
        title = ttk.Label(
            header, 
            text="🔄 Sorting Visualizer Control Panel", 
            font=('Arial', 20, 'bold')
        )
        title.pack()
    
    def _create_main_content(self):
        """Create main content with left and right columns."""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Mode and Algorithm selection
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self._create_mode_section(left_frame)
        self._create_algorithm_section(left_frame)
        self._create_comparison_section(left_frame)
        self._create_settings_section(left_frame)
        
        # Right column - Frames management
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self._create_single_frames_section(right_frame)
        self._create_comparison_frames_section(right_frame)
        self._create_run_button(right_frame)
    
    def _create_mode_section(self, parent):
        """Create mode selection section."""
        frame = ttk.LabelFrame(parent, text="Mode", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        single_rb = ttk.Radiobutton(
            frame, text="Single Algorithm", value="single",
            variable=self.mode_var, command=self._on_mode_change
        )
        single_rb.pack(side=tk.LEFT, padx=10)
        
        comparison_rb = ttk.Radiobutton(
            frame, text="Comparison Mode", value="comparison",
            variable=self.mode_var, command=self._on_mode_change
        )
        comparison_rb.pack(side=tk.LEFT, padx=10)
    
    def _create_algorithm_section(self, parent):
        """Create single algorithm selection section."""
        self.algo_frame = ttk.LabelFrame(parent, text="Select Algorithm", padding=10)
        self.algo_frame.pack(fill=tk.X, pady=5)
        
        for algo in ALGORITHMS:
            rb = ttk.Radiobutton(
                self.algo_frame, text=algo, value=algo,
                variable=self.algorithm_var
            )
            rb.pack(anchor=tk.W, pady=2)
    
    def _create_comparison_section(self, parent):
        """Create comparison algorithm selection."""
        self.comparison_frame = ttk.LabelFrame(parent, text="Select Algorithms to Compare", padding=10)
        
        for algo in ALGORITHMS:
            cb = ttk.Checkbutton(
                self.comparison_frame, text=algo,
                variable=self.comparison_vars[algo]
            )
            cb.pack(anchor=tk.W, pady=2)
        
        ttk.Button(
            self.comparison_frame, text="Select All",
            command=self._select_all_algorithms
        ).pack(anchor=tk.W, pady=5)
    
    def _create_settings_section(self, parent):
        """Create settings section."""
        frame = ttk.LabelFrame(parent, text="Settings", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        # Speed
        speed_row = ttk.Frame(frame)
        speed_row.pack(fill=tk.X, pady=3)
        ttk.Label(speed_row, text="Speed:").pack(side=tk.LEFT)
        self.speed_label = ttk.Label(speed_row, text=f"{self.speed_var.get()}x")
        self.speed_label.pack(side=tk.RIGHT)
        
        ttk.Scale(
            frame, from_=1, to=50, orient=tk.HORIZONTAL,
            variable=self.speed_var, command=self._on_speed_change
        ).pack(fill=tk.X, pady=3)
        
        # Number of bars
        bars_row = ttk.Frame(frame)
        bars_row.pack(fill=tk.X, pady=3)
        ttk.Label(bars_row, text="Bars:").pack(side=tk.LEFT)
        self.bars_label = ttk.Label(bars_row, text=str(self.num_bars_var.get()))
        self.bars_label.pack(side=tk.RIGHT)
        
        ttk.Scale(
            frame, from_=50, to=400, orient=tk.HORIZONTAL,
            variable=self.num_bars_var, command=self._on_bars_change
        ).pack(fill=tk.X, pady=3)
        
        # Save frames checkbox
        ttk.Checkbutton(
            frame, text="Save frames for video",
            variable=self.save_frames_var
        ).pack(anchor=tk.W, pady=5)
    
    def _create_single_frames_section(self, parent):
        """Create single simulation frames section."""
        frame = ttk.LabelFrame(parent, text="📁 Single Simulation Frames", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        # Frame count
        count_row = ttk.Frame(frame)
        count_row.pack(fill=tk.X, pady=3)
        ttk.Label(count_row, text="Saved Frames:").pack(side=tk.LEFT)
        self.frame_count_label = ttk.Label(count_row, text="0", font=('Arial', 12, 'bold'))
        self.frame_count_label.pack(side=tk.RIGHT)
        
        # Buttons row 1
        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_row, text="🔄 Refresh", command=self._update_frame_count).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="🗑️ Clear", command=self._clear_frames).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="📂 Open", command=self._open_frames_folder).pack(side=tk.LEFT, padx=2)
        
        # Video generation button
        video_btn = tk.Button(
            frame,
            text="🎬 Generate Video",
            bg='#2196F3', fg='white',
            activebackground='#1976D2',
            command=lambda: self._generate_video(FRAMES_FOLDER, "single")
        )
        video_btn.pack(fill=tk.X, pady=5)
    
    def _create_comparison_frames_section(self, parent):
        """Create comparison frames section."""
        frame = ttk.LabelFrame(parent, text="📁 Comparison Frames", padding=10)
        frame.pack(fill=tk.X, pady=5)
        
        # Frame count
        count_row = ttk.Frame(frame)
        count_row.pack(fill=tk.X, pady=3)
        ttk.Label(count_row, text="Saved Frames:").pack(side=tk.LEFT)
        self.comparison_frame_count_label = ttk.Label(count_row, text="0", font=('Arial', 12, 'bold'))
        self.comparison_frame_count_label.pack(side=tk.RIGHT)
        
        # Buttons row 1
        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_row, text="🔄 Refresh", command=self._update_comparison_frame_count).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="🗑️ Clear", command=self._clear_comparison_frames).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="📂 Open", command=self._open_comparison_frames_folder).pack(side=tk.LEFT, padx=2)
        
        # Video generation button
        video_btn = tk.Button(
            frame,
            text="🎬 Generate Video",
            bg='#2196F3', fg='white',
            activebackground='#1976D2',
            command=lambda: self._generate_video(COMPARISON_FRAMES_FOLDER, "comparison")
        )
        video_btn.pack(fill=tk.X, pady=5)
    
    def _create_run_button(self, parent):
        """Create run simulation button."""
        btn_frame = ttk.Frame(parent, padding=10)
        btn_frame.pack(fill=tk.X, pady=10)
        
        run_btn = tk.Button(
            btn_frame,
            text="▶️  RUN SIMULATION",
            font=('Arial', 14, 'bold'),
            bg='#4CAF50', fg='white',
            activebackground='#45a049',
            height=2,
            command=self._run_simulation
        )
        run_btn.pack(fill=tk.X)
    
    def _select_all_algorithms(self):
        """Select all algorithms for comparison."""
        for var in self.comparison_vars.values():
            var.set(True)
    
    def _on_mode_change(self):
        """Handle mode change."""
        if self.mode_var.get() == "single":
            self.comparison_frame.pack_forget()
            self.algo_frame.pack(fill=tk.X, pady=5)
        else:
            self.algo_frame.pack_forget()
            self.comparison_frame.pack(fill=tk.X, pady=5)
    
    def _on_speed_change(self, value):
        self.speed_label.config(text=f"{int(float(value))}x")
    
    def _on_bars_change(self, value):
        self.bars_label.config(text=str(int(float(value))))
    
    def _update_frame_count(self):
        """Update single simulation frame count."""
        count = len([f for f in os.listdir(FRAMES_FOLDER) if f.endswith('.png')]) if os.path.exists(FRAMES_FOLDER) else 0
        self.frame_count_label.config(text=str(count))
    
    def _update_comparison_frame_count(self):
        """Update comparison frame count."""
        count = len([f for f in os.listdir(COMPARISON_FRAMES_FOLDER) if f.endswith('.png')]) if os.path.exists(COMPARISON_FRAMES_FOLDER) else 0
        self.comparison_frame_count_label.config(text=str(count))
    
    def _clear_frames(self):
        """Clear single simulation frames."""
        self._clear_folder(FRAMES_FOLDER)
        self._update_frame_count()
    
    def _clear_comparison_frames(self):
        """Clear comparison frames."""
        self._clear_folder(COMPARISON_FRAMES_FOLDER)
        self._update_comparison_frame_count()
    
    def _clear_folder(self, folder):
        """Clear all PNG files from a folder."""
        if not os.path.exists(folder):
            return
        
        count = len([f for f in os.listdir(folder) if f.endswith('.png')])
        if count == 0:
            messagebox.showinfo("Info", "No frames to clear.")
            return
        
        if messagebox.askyesno("Confirm", f"Delete {count} frames?"):
            for f in os.listdir(folder):
                if f.endswith('.png'):
                    os.remove(os.path.join(folder, f))
            messagebox.showinfo("Success", "Frames cleared!")
    
    def _open_frames_folder(self):
        """Open single frames folder."""
        self._open_folder(FRAMES_FOLDER)
    
    def _open_comparison_frames_folder(self):
        """Open comparison frames folder."""
        self._open_folder(COMPARISON_FRAMES_FOLDER)
    
    def _open_folder(self, folder):
        """Open folder in file explorer."""
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        if sys.platform == 'win32':
            os.startfile(folder)
        elif sys.platform == 'darwin':
            subprocess.run(['open', folder])
        else:
            subprocess.run(['xdg-open', folder])
    
    def _run_simulation(self):
        """Launch the simulation."""
        speed = int(self.speed_var.get())
        num_bars = int(self.num_bars_var.get())
        save_frames = self.save_frames_var.get()
        
        if self.mode_var.get() == "comparison":
            selected = [algo for algo, var in self.comparison_vars.items() if var.get()]
            
            if len(selected) < 2:
                messagebox.showwarning("Warning", "Select at least 2 algorithms for comparison.")
                return
            
            settings_file = os.path.join(SCRIPT_DIR, "comparison_settings.py")
            with open(settings_file, 'w') as f:
                f.write(f"ALGORITHMS = {selected}\n")
                f.write(f"SPEED = {speed}\n")
                f.write(f"NUM_BARS = {num_bars}\n")
                f.write(f"SAVE_FRAMES = {save_frames}\n")
            
            visualizer_path = os.path.join(SCRIPT_DIR, "comparison_visualizer.py")
        else:
            algorithm = self.algorithm_var.get()
            
            settings_file = os.path.join(SCRIPT_DIR, "runtime_settings.py")
            with open(settings_file, 'w') as f:
                f.write(f"ALGORITHM = \"{algorithm}\"\n")
                f.write(f"SPEED = {speed}\n")
                f.write(f"NUM_BARS = {num_bars}\n")
                f.write(f"SAVE_FRAMES = {save_frames}\n")
                f.write(f"AUTO_START = True\n")
            
            visualizer_path = os.path.join(SCRIPT_DIR, "main.py")
        
        def run_visualizer():
            subprocess.run([sys.executable, visualizer_path])
            self.root.after(100, self._update_frame_count)
            self.root.after(100, self._update_comparison_frame_count)
        
        thread = threading.Thread(target=run_visualizer, daemon=True)
        thread.start()
    
    def _generate_video(self, frame_folder, video_type):
        """Generate video from frames using the global video generator service."""
        # Check if folder exists and has frames
        if not os.path.exists(frame_folder):
            messagebox.showwarning("Warning", "Frame folder does not exist.")
            return
        
        frame_count = len([f for f in os.listdir(frame_folder) if f.endswith('.png')])
        if frame_count == 0:
            messagebox.showwarning("Warning", "No frames to generate video from.\nRun a simulation first with 'Save frames' enabled.")
            return
        
        # Ask user for FPS
        fps_dialog = tk.Toplevel(self.root)
        fps_dialog.title("Video Settings")
        fps_dialog.geometry("300x200")
        fps_dialog.resizable(False, False)
        fps_dialog.transient(self.root)
        fps_dialog.grab_set()
        
        ttk.Label(fps_dialog, text="Video Generation Settings", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # FPS
        fps_frame = ttk.Frame(fps_dialog)
        fps_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(fps_frame, text="FPS:").pack(side=tk.LEFT)
        fps_var = tk.IntVar(value=60)
        fps_entry = ttk.Spinbox(fps_frame, from_=15, to=120, textvariable=fps_var, width=10)
        fps_entry.pack(side=tk.RIGHT)
        
        # Quality
        quality_frame = ttk.Frame(fps_dialog)
        quality_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(quality_frame, text="Quality:").pack(side=tk.LEFT)
        quality_var = tk.StringVar(value="high")
        quality_combo = ttk.Combobox(quality_frame, textvariable=quality_var, 
                                      values=["low", "medium", "high", "ultra"], state="readonly", width=10)
        quality_combo.pack(side=tk.RIGHT)
        
        ttk.Label(fps_dialog, text=f"Frames: {frame_count}", font=('Arial', 10)).pack(pady=5)
        
        def do_generate():
            fps_dialog.destroy()
            self._do_video_generation(frame_folder, video_type, fps_var.get(), quality_var.get())
        
        btn_frame = ttk.Frame(fps_dialog)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="Cancel", command=fps_dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Generate", command=do_generate).pack(side=tk.LEFT, padx=5)
    
    def _do_video_generation(self, frame_folder, video_type, fps, quality):
        """Actually perform video generation in a separate thread."""
        # Show progress dialog
        progress_dialog = tk.Toplevel(self.root)
        progress_dialog.title("Generating Video...")
        progress_dialog.geometry("350x120")
        progress_dialog.resizable(False, False)
        progress_dialog.transient(self.root)
        
        ttk.Label(progress_dialog, text="🎬 Generating video...", font=('Arial', 12)).pack(pady=15)
        progress = ttk.Progressbar(progress_dialog, mode='indeterminate')
        progress.pack(fill=tk.X, padx=30, pady=10)
        progress.start(10)
        
        status_label = ttk.Label(progress_dialog, text="Processing frames...")
        status_label.pack()
        
        def generate():
            try:
                from shared.video_generator import VideoGenerator
                
                generator = VideoGenerator()
                
                # Generate output name based on type and algorithm
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                if video_type == "single":
                    algo = self.algorithm_var.get().replace(" ", "_").lower()
                    output_name = f"sorting_{algo}_{timestamp}"
                else:
                    output_name = f"sorting_comparison_{timestamp}"
                
                output_path = generator.generate_video(
                    frame_folder=frame_folder,
                    output_name=output_name,
                    fps=fps,
                    quality=quality
                )
                
                # Close progress and show success
                self.root.after(0, progress_dialog.destroy)
                self.root.after(0, lambda: self._show_video_success(output_path))
                
            except Exception as e:
                self.root.after(0, progress_dialog.destroy)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Video generation failed:\n{str(e)}"))
        
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
    
    def _show_video_success(self, output_path):
        """Show success dialog with option to open video."""
        result = messagebox.askyesno(
            "Video Generated!",
            f"Video generated successfully!\n\n{output_path}\n\nOpen containing folder?"
        )
        if result:
            folder = os.path.dirname(str(output_path))
            self._open_folder(folder)
    
    def run(self):
        """Start the control panel."""
        self.root.mainloop()


def main():
    panel = ControlPanel()
    panel.run()


if __name__ == "__main__":
    main()