#!/usr/bin/env python3
"""
Sorting Circles - Control Panel
================================
Tkinter-based GUI for configuring and launching the sorting circles visualization.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import json
import requests
import time
from pathlib import Path
import threading

SIMULATION_DIR = Path(__file__).resolve().parent
BASE_DIR = SIMULATION_DIR.parent.parent


class SortingCirclesControlPanel:
    """Control panel GUI for Sorting Circles visualization."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⭕ Sorting Circles - Control Panel")
        self.root.geometry("500x750")
        self.root.configure(bg='#0f172a')
        
        # Simulation process
        self.sim_process = None
        self.is_recording = False
        self.frames_count = 0
        
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
            text="🔢 Algorithm",
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
        
        # Speed Control
        speed_frame = tk.LabelFrame(
            main_frame,
            text="⚡ Animation Speed",
            bg='#1e293b',
            fg='#e2e8f0',
            font=('Segoe UI', 11, 'bold'),
            relief='ridge',
            bd=2
        )
        speed_frame.pack(fill='x', pady=(0, 15))
        
        speed_inner = tk.Frame(speed_frame, bg='#1e293b')
        speed_inner.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(speed_inner, text="Operations/sec:").pack(side='left')
        
        self.speed_var = tk.IntVar(value=5)
        speed_scale = tk.Scale(
            speed_inner,
            from_=1,
            to=60,
            orient='horizontal',
            variable=self.speed_var,
            bg='#1e293b',
            fg='#e2e8f0',
            activebackground='#10b981',
            highlightthickness=0,
            troughcolor='#334155',
            length=200
        )
        speed_scale.pack(side='left', padx=10)
        
        # Status Display
        status_frame = tk.LabelFrame(
            main_frame,
            text="📊 Status",
            bg='#1e293b',
            fg='#e2e8f0',
            font=('Segoe UI', 11, 'bold'),
            relief='ridge',
            bd=2
        )
        status_frame.pack(fill='x', pady=(0, 15))
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready to launch",
            bg='#1e293b',
            fg='#94a3b8',
            font=('Segoe UI', 10)
        )
        self.status_label.pack(padx=15, pady=10)
        
        self.frames_label = tk.Label(
            status_frame,
            text="Frames: 0",
            bg='#1e293b',
            fg='#94a3b8',
            font=('Segoe UI', 10)
        )
        self.frames_label.pack(padx=15, pady=(0, 10))
        
        # Control Buttons
        btn_frame = tk.Frame(main_frame, bg='#0f172a')
        btn_frame.pack(fill='x', pady=(0, 10))
        
        # Launch Button
        self.launch_btn = tk.Button(
            btn_frame,
            text="🚀 Launch Simulation",
            command=self._launch,
            bg='#10b981',
            fg='white',
            activebackground='#059669',
            activeforeground='white',
            font=('Segoe UI', 11, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=10
        )
        self.launch_btn.pack(fill='x', pady=(0, 5))
        
        # Recording Controls
        rec_frame = tk.Frame(btn_frame, bg='#0f172a')
        rec_frame.pack(fill='x', pady=(5, 0))
        
        self.record_btn = tk.Button(
            rec_frame,
            text="⏺ Start Recording",
            command=self._toggle_recording,
            bg='#ef4444',
            fg='white',
            activebackground='#dc2626',
            activeforeground='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8,
            state='disabled'
        )
        self.record_btn.pack(side='left', fill='x', expand=True, padx=(0, 2.5))
        
        self.video_btn = tk.Button(
            rec_frame,
            text="🎬 Generate Video",
            command=self._generate_video,
            bg='#8b5cf6',
            fg='white',
            activebackground='#7c3aed',
            activeforeground='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8,
            state='disabled'
        )
        self.video_btn.pack(side='left', fill='x', expand=True, padx=(2.5, 0))
        
    def _launch(self):
        """Launch the simulation with selected parameters."""
        if self.sim_process and self.sim_process.poll() is None:
            messagebox.showwarning("Already Running", "Simulation is already running!")
            return
        
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
            self.is_recording = True
        
        self.sim_process = subprocess.Popen(cmd)
        self.launch_btn.config(state='disabled')
        self.record_btn.config(state='normal' if not self.is_recording else 'disabled')
        self.status_label.config(text="Simulation running", fg='#10b981')
        
        # Monitor simulation process
        threading.Thread(target=self._monitor_simulation, daemon=True).start()
        
        # Monitor frames if recording
        if self.is_recording:
            self.record_btn.config(text="⏹ Stop Recording")
            threading.Thread(target=self._monitor_frames, daemon=True).start()
    
    def _monitor_simulation(self):
        """Monitor the simulation process."""
        while self.sim_process and self.sim_process.poll() is None:
            time.sleep(0.5)
        
        # Simulation ended
        self.root.after(0, self._on_simulation_end)
    
    def _on_simulation_end(self):
        """Handle simulation end."""
        self.launch_btn.config(state='normal')
        self.record_btn.config(state='disabled', text="⏺ Start Recording")
        self.status_label.config(text="Simulation ended", fg='#94a3b8')
        
        if self.is_recording:
            self.is_recording = False
            self.video_btn.config(state='normal')
    
    def _toggle_recording(self):
        """Toggle recording on/off."""
        if not self.sim_process or self.sim_process.poll() is not None:
            messagebox.showwarning("Not Running", "No simulation is running!")
            return
        
        # Send 's' key to simulation window (simplified - actual implementation would need IPC)
        self.is_recording = not self.is_recording
        
        if self.is_recording:
            self.record_btn.config(text="⏹ Stop Recording", bg='#f59e0b')
            self.status_label.config(text="Recording...", fg='#ef4444')
            threading.Thread(target=self._monitor_frames, daemon=True).start()
        else:
            self.record_btn.config(text="⏺ Start Recording", bg='#ef4444')
            self.status_label.config(text="Recording stopped", fg='#94a3b8')
            self.video_btn.config(state='normal')
    
    def _monitor_frames(self):
        """Monitor frame count."""
        frames_dir = SIMULATION_DIR / "frames"
        while self.is_recording:
            if frames_dir.exists():
                frame_files = list(frames_dir.glob("frame_*.png"))
                self.frames_count = len(frame_files)
                self.root.after(0, lambda: self.frames_label.config(text=f"Frames: {self.frames_count}"))
            time.sleep(0.5)
    
    def _generate_video(self):
        """Generate video from frames using API."""
        frames_dir = SIMULATION_DIR / "frames"
        
        if not frames_dir.exists() or not list(frames_dir.glob("frame_*.png")):
            messagebox.showerror("No Frames", "No frames found to generate video!")
            return
        
        self.video_btn.config(state='disabled', text="Generating...")
        self.status_label.config(text="Generating video...", fg='#8b5cf6')
        
        threading.Thread(target=self._generate_video_thread, daemon=True).start()
    
    def _generate_video_thread(self):
        """Generate video in background thread."""
        try:
            # Call API endpoint
            response = requests.post(
                'http://localhost:5000/api/generate-video',
                json={
                    'addon_id': 'sorting_circles',
                    'frame_type': 'normal',
                    'fps': int(self.fps_var.get()),
                    'codec': 'libx264'
                },
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"Video generated successfully!\n{result.get('video_path', '')}"
                ))
                self.root.after(0, lambda: self.status_label.config(text="Video generated!", fg='#10b981'))
            else:
                error = response.json().get('error', 'Unknown error')
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate video:\n{error}"))
                self.root.after(0, lambda: self.status_label.config(text="Video generation failed", fg='#ef4444'))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error generating video:\n{str(e)}"))
            self.root.after(0, lambda: self.status_label.config(text="Video generation failed", fg='#ef4444'))
        finally:
            self.root.after(0, lambda: self.video_btn.config(state='normal', text="🎬 Generate Video"))
        
    def run(self):
        """Run the control panel."""
        self.root.mainloop()


def main():
    panel = SortingCirclesControlPanel()
    panel.run()


if __name__ == "__main__":
    main()
