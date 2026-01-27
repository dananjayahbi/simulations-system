#!/usr/bin/env python3
"""
Sorting Circles - Control Panel
================================
Tkinter-based GUI for configuring and launching the sorting circles visualization.
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import sys
from pathlib import Path

SIMULATION_DIR = Path(__file__).resolve().parent
BASE_DIR = SIMULATION_DIR.parent.parent


class SortingCirclesControlPanel:
    """Control panel GUI for Sorting Circles visualization."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⭕ Sorting Circles - Control Panel")
        self.root.geometry("450x600")
        self.root.configure(bg='#0f172a')
        
        # Make it modern
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TLabel', background='#0f172a', foreground='#e2e8f0', font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), foreground='#10b981')
        style.configure('Heading.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#e2e8f0')
        style.configure('TButton', font=('Segoe UI', 10))
        style.configure('Launch.TButton', font=('Segoe UI', 12, 'bold'))
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create GUI widgets."""
        # Main container
        main_frame = tk.Frame(self.root, bg='#0f172a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = ttk.Label(
            main_frame,
            text="⭕ Sorting Circles",
            style='Title.TLabel'
        )
        title.pack(pady=(0, 10))
        
        # Description
        desc = ttk.Label(
            main_frame,
            text="Visualize sorting algorithms using radial circle patterns",
            font=('Segoe UI', 9),
            foreground='#94a3b8'
        )
        desc.pack(pady=(0, 20))
        
        # Settings Frame
        settings_frame = tk.LabelFrame(
            main_frame,
            text="⚙️ Settings",
            bg='#1e293b',
            fg='#e2e8f0',
            font=('Segoe UI', 11, 'bold'),
            relief='ridge',
            bd=2
        )
        settings_frame.pack(fill='x', pady=(0, 15))
        
        # Window Size
        size_frame = tk.Frame(settings_frame, bg='#1e293b')
        size_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(size_frame, text="Window Size:").pack(side='left')
        
        self.width_var = tk.StringVar(value="1000")
        width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=8)
        width_entry.pack(side='left', padx=(10, 5))
        
        ttk.Label(size_frame, text="×").pack(side='left')
        
        self.height_var = tk.StringVar(value="1000")
        height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=8)
        height_entry.pack(side='left', padx=5)
        
        # FPS
        fps_frame = tk.Frame(settings_frame, bg='#1e293b')
        fps_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(fps_frame, text="Frame Rate:").pack(side='left')
        
        self.fps_var = tk.StringVar(value="60")
        fps_spinbox = ttk.Spinbox(
            fps_frame,
            from_=30,
            to=120,
            textvariable=self.fps_var,
            width=8
        )
        fps_spinbox.pack(side='left', padx=10)
        
        ttk.Label(fps_frame, text="FPS").pack(side='left')
        
        # Array Size
        array_frame = tk.Frame(settings_frame, bg='#1e293b')
        array_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(array_frame, text="Number of Circles:").pack(side='left')
        
        self.array_size_var = tk.StringVar(value="50")
        array_spinbox = ttk.Spinbox(
            array_frame,
            from_=20,
            to=100,
            textvariable=self.array_size_var,
            width=8
        )
        array_spinbox.pack(side='left', padx=10)
        
        # Recording Options
        recording_frame = tk.LabelFrame(
            main_frame,
            text="🎬 Recording",
            bg='#1e293b',
            fg='#e2e8f0',
            font=('Segoe UI', 11, 'bold'),
            relief='ridge',
            bd=2
        )
        recording_frame.pack(fill='x', pady=(0, 15))
        
        self.auto_record_var = tk.BooleanVar(value=False)
        record_check = tk.Checkbutton(
            recording_frame,
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
        
        # Algorithm Selection
        algo_frame = tk.LabelFrame(
            main_frame,
            text="🔢 Default Algorithm",
            bg='#1e293b',
            fg='#e2e8f0',
            font=('Segoe UI', 11, 'bold'),
            relief='ridge',
            bd=2
        )
        algo_frame.pack(fill='x', pady=(0, 15))
        
        self.algorithm_var = tk.StringVar(value="bubble")
        
        algorithms = [
            ("Bubble Sort", "bubble"),
            ("Quick Sort", "quick"),
            ("Merge Sort", "merge")
        ]
        
        for text, value in algorithms:
            radio = tk.Radiobutton(
                algo_frame,
                text=text,
                variable=self.algorithm_var,
                value=value,
                bg='#1e293b',
                fg='#e2e8f0',
                selectcolor='#334155',
                activebackground='#1e293b',
                activeforeground='#10b981',
                font=('Segoe UI', 10)
            )
            radio.pack(padx=15, pady=5, anchor='w')
        
        # Info Section
        info_frame = tk.LabelFrame(
            main_frame,
            text="ℹ️ Controls",
            bg='#1e293b',
            fg='#e2e8f0',
            font=('Segoe UI', 11, 'bold'),
            relief='ridge',
            bd=2
        )
        info_frame.pack(fill='x', pady=(0, 15))
        
        controls_text = """
• SPACE - Play/Pause
• R - Reset & Shuffle
• S - Start/Stop Recording
• 1/2/3 - Switch Algorithm
• ↑↓ - Speed Control
• ESC - Exit
        """
        
        controls_label = tk.Label(
            info_frame,
            text=controls_text.strip(),
            bg='#1e293b',
            fg='#94a3b8',
            font=('Consolas', 9),
            justify='left'
        )
        controls_label.pack(padx=15, pady=10)
        
        # Launch Button
        launch_btn = tk.Button(
            main_frame,
            text="🚀 Launch Visualization",
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
        
        # Hover effects for launch button
        def on_enter(e):
            launch_btn.config(bg='#059669')
        
        def on_leave(e):
            launch_btn.config(bg='#10b981')
        
        launch_btn.bind('<Enter>', on_enter)
        launch_btn.bind('<Leave>', on_leave)
        
    def _launch(self):
        """Launch the simulation with selected parameters."""
        cmd = [
            sys.executable,
            str(SIMULATION_DIR / "main.py"),
            '--width', self.width_var.get(),
            '--height', self.height_var.get(),
            '--fps', self.fps_var.get(),
            '--array-size', self.array_size_var.get(),
            '--algorithm', self.algorithm_var.get()
        ]
        
        if self.auto_record_var.get():
            cmd.append('--record')
        
        subprocess.Popen(cmd)
        
    def run(self):
        """Run the control panel."""
        self.root.mainloop()


def main():
    panel = SortingCirclesControlPanel()
    panel.run()


if __name__ == "__main__":
    main()
