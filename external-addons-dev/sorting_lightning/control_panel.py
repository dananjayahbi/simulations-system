#!/usr/bin/env python3
"""
Sorting Lightning - Control Panel
==================================
Tkinter-based GUI for configuring and launching the sorting visualization.
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
    """Control panel GUI for Sorting Lightning."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⚡ Sorting Lightning - Control Panel")
        self.root.geometry("900x650")
        self.root.configure(bg='#0f172a')
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#0f172a', foreground='#e2e8f0', 
                       font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'), 
                       foreground='#a855f7')
        style.configure('Section.TLabel', font=('Segoe UI', 12, 'bold'), 
                       foreground='#10b981')
        
        # Variables
        self.width_var = tk.StringVar(value="1400")
        self.height_var = tk.StringVar(value="900")
        self.fps_var = tk.StringVar(value="60")
        self.algorithm_var = tk.StringVar(value="bubble")
        self.bar_count_var = tk.IntVar(value=100)
        self.speed_var = tk.IntVar(value=1)
        self.theme_var = tk.StringVar(value="neon")
        self.effects_var = tk.BooleanVar(value=True)
        self.auto_record_var = tk.BooleanVar(value=False)
        
        # Video generation vars
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
            text="⚡ Sorting Lightning",
            style='Title.TLabel'
        )
        title.pack()
        
        subtitle = ttk.Label(
            title_frame,
            text="Advanced Sorting Visualization with Effects",
            font=('Segoe UI', 9),
            foreground='#94a3b8'
        )
        subtitle.pack()
        
        # Top row: Window + Algorithm settings (side by side)
        top_row = tk.Frame(main_frame, bg='#0f172a')
        top_row.pack(fill='x', pady=(0, 10))
        
        # Left column
        left_col = tk.Frame(top_row, bg='#0f172a')
        left_col.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self._create_window_settings(left_col)
        self._create_algorithm_settings(left_col)
        
        # Right column
        right_col = tk.Frame(top_row, bg='#0f172a')
        right_col.pack(side='left', fill='both', expand=True, padx=(5, 0))
        
        self._create_visual_settings(right_col)
        self._create_recording_settings(right_col)
        
        # Bottom section: Frame management and launch
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
        frame.pack(fill='x', pady=(0, 15))
        
        # Size
        size_frame = tk.Frame(frame, bg='#1e293b')
        size_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(size_frame, text="Window Size:").pack(side='left')
        ttk.Entry(size_frame, textvariable=self.width_var, width=8).pack(
            side='left', padx=(10, 5))
        ttk.Label(size_frame, text="×").pack(side='left')
        ttk.Entry(size_frame, textvariable=self.height_var, width=8).pack(
            side='left', padx=5)
        
        # FPS
        fps_frame = tk.Frame(frame, bg='#1e293b')
        fps_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(fps_frame, text="Target FPS:").pack(side='left')
        ttk.Spinbox(fps_frame, from_=30, to=120, textvariable=self.fps_var, 
                   width=8).pack(side='left', padx=10)
    
    def _create_algorithm_settings(self, parent):
        """Create algorithm selection section."""
        frame = tk.LabelFrame(
            parent,
            text="🧮 Algorithm Settings",
            bg='#1e293b',
            fg='#e2e8f0',
            font=('Segoe UI', 11, 'bold'),
            relief='ridge',
            bd=2
        )
        frame.pack(fill='x', pady=(0, 15))
        
        # Algorithm selection
        algo_frame = tk.Frame(frame, bg='#1e293b')
        algo_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(algo_frame, text="Algorithm:").pack(side='left')
        
        algorithms = [
            ("Bubble Sort", "bubble"),
            ("Quick Sort", "quick"),
            ("Merge Sort", "merge"),
            ("Insertion Sort", "insertion"),
            ("Selection Sort", "selection")
        ]
        
        algo_menu = ttk.Combobox(
            algo_frame,
            textvariable=self.algorithm_var,
            values=[name for name, _ in algorithms],
            state='readonly',
            width=18
        )
        algo_menu.pack(side='left', padx=10)
        
        # Map display names to internal names
        self.algorithm_var.set("Bubble Sort")
        self.algo_map = {name: value for name, value in algorithms}
        
        # Bar count
        bar_frame = tk.Frame(frame, bg='#1e293b')
        bar_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(bar_frame, text="Bar Count:").pack(side='left')
        self.bar_count_label = ttk.Label(bar_frame, text=str(self.bar_count_var.get()))
        self.bar_count_label.pack(side='right')
        
        bar_scale = ttk.Scale(
            frame,
            from_=20,
            to=300,
            orient=tk.HORIZONTAL,
            variable=self.bar_count_var,
            command=lambda v: self.bar_count_label.config(text=str(int(float(v))))
        )
        bar_scale.pack(fill='x', padx=15, pady=(0, 10))
        
        # Speed
        speed_frame = tk.Frame(frame, bg='#1e293b')
        speed_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(speed_frame, text="Speed:").pack(side='left')
        self.speed_label = ttk.Label(speed_frame, text=f"{self.speed_var.get()}x")
        self.speed_label.pack(side='right')
        
        speed_scale = ttk.Scale(
            frame,
            from_=1,
            to=50,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=lambda v: self.speed_label.config(text=f"{int(float(v))}x")
        )
        speed_scale.pack(fill='x', padx=15, pady=(0, 10))
    
    def _create_visual_settings(self, parent):
        """Create visual theme section."""
        frame = tk.LabelFrame(
            parent,
            text="🎨 Visual Settings",
            bg='#1e293b',
            fg='#e2e8f0',
            font=('Segoe UI', 11, 'bold'),
            relief='ridge',
            bd=2
        )
        frame.pack(fill='x', pady=(0, 15))
        
        # Theme selection
        theme_frame = tk.Frame(frame, bg='#1e293b')
        theme_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(theme_frame, text="Color Theme:").pack(side='left')
        
        themes = [
            ("🌈 Rainbow", "rainbow"),
            ("💜 Neon", "neon"),
            ("🔥 Fire", "fire"),
            ("❄️ Ice", "ice"),
            ("🌃 Cyberpunk", "cyberpunk")
        ]
        
        theme_menu = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=[name for name, _ in themes],
            state='readonly',
            width=18
        )
        theme_menu.pack(side='left', padx=10)
        
        self.theme_var.set("💜 Neon")
        self.theme_map = {name: value for name, value in themes}
        
        # Effects toggle
        effects_check = tk.Checkbutton(
            frame,
            text="⚡ Enable Lightning & Particle Effects",
            variable=self.effects_var,
            bg='#1e293b',
            fg='#e2e8f0',
            selectcolor='#334155',
            activebackground='#1e293b',
            activeforeground='#a855f7',
            font=('Segoe UI', 10)
        )
        effects_check.pack(padx=15, pady=10, anchor='w')
        
        # Theme preview info
        info = ttk.Label(
            frame,
            text="Tip: Press 1-5 during simulation to switch themes live!",
            font=('Segoe UI', 8),
            foreground='#64748b'
        )
        info.pack(padx=15, pady=(0, 10))
    
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
            text="Start recording on launch (Press S to toggle during simulation)",
            variable=self.auto_record_var,
            bg='#1e293b',
            fg='#e2e8f0',
            selectcolor='#334155',
            activebackground='#1e293b',
            activeforeground='#10b981',
            font=('Segoe UI', 10),
            wraplength=450
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
        
        # Frame count display
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
        
        # Button frame
        btn_frame = tk.Frame(frame, bg='#1e293b')
        btn_frame.pack(fill='x', padx=15, pady=10)
        
        # Refresh button
        refresh_btn = tk.Button(
            btn_frame,
            text="🔄 Refresh",
            command=self._update_frame_count,
            bg='#3b82f6',
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            padx=10,
            pady=5,
            cursor='hand2'
        )
        refresh_btn.pack(side='left', padx=(0, 5))
        
        # Clear button
        clear_btn = tk.Button(
            btn_frame,
            text="🗑️ Clear",
            command=self._clear_frames,
            bg='#f97316',
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            padx=10,
            pady=5,
            cursor='hand2'
        )
        clear_btn.pack(side='left', padx=5)
        
        # Open folder button
        open_btn = tk.Button(
            btn_frame,
            text="📂 Open Folder",
            command=self._open_frames_folder,
            bg='#8b5cf6',
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            relief='flat',
            padx=10,
            pady=5,
            cursor='hand2'
        )
        open_btn.pack(side='left', padx=5)
        
        # Video generation button
        video_btn = tk.Button(
            frame,
            text="🎥 Generate Video",
            command=self._show_video_dialog,
            bg='#8b5cf6',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        video_btn.pack(padx=15, pady=10, fill='x')
    
    def _create_launch_button(self, parent):
        """Create main launch button."""
        self.launch_btn = tk.Button(
            parent,
            text="⚡ LAUNCH VISUALIZATION",
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
        
        # Keyboard shortcuts info
        shortcuts = ttk.Label(
            parent,
            text="Shortcuts: SPACE=Pause | R=Reset | S=Record | 1-5=Themes | E=Effects | ESC=Exit",
            font=('Segoe UI', 8),
            foreground='#64748b',
            justify='center'
        )
        shortcuts.pack(pady=(0, 5))
    
    def _update_frame_count(self):
        """Update the frame count display."""
        try:
            if FRAMES_FOLDER.exists():
                frame_files = list(FRAMES_FOLDER.glob("frame_*.png"))
                count = len(frame_files)
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
        if not FRAMES_FOLDER.exists():
            messagebox.showinfo("Info", "No frames folder found.")
            return
        
        frame_files = list(FRAMES_FOLDER.glob("frame_*.png"))
        if not frame_files:
            messagebox.showinfo("Info", "No frames to clear.")
            return
        
        result = messagebox.askyesno(
            "Confirm Clear",
            f"Delete {len(frame_files)} frame(s)?\n\n"
            "This action cannot be undone."
        )
        
        if result:
            def delete_frames():
                try:
                    for frame_file in frame_files:
                        frame_file.unlink()
                    self.root.after(0, lambda: self._update_frame_count())
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Success", f"✅ Deleted {len(frame_files)} frame(s)."))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error", f"❌ Failed to delete frames:\n{e}"))
            
            threading.Thread(target=delete_frames, daemon=True).start()
    
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
            messagebox.showerror("Error", f"Failed to open folder:\n{e}")
    
    def _show_video_dialog(self):
        """Show video generation settings dialog."""
        if not FRAMES_FOLDER.exists() or not list(FRAMES_FOLDER.glob("frame_*.png")):
            messagebox.showwarning(
                "No Frames",
                "⚠️ No frames found!\n\n"
                "Launch the simulation and press 'S' to start recording first."
            )
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("🎥 Video Generation Settings")
        dialog.geometry("400x300")
        dialog.configure(bg='#1e293b')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Title
        title = ttk.Label(
            dialog,
            text="🎥 Video Generation",
            font=('Segoe UI', 16, 'bold'),
            foreground='#a855f7',
            background='#1e293b'
        )
        title.pack(pady=20)
        
        # FPS setting
        fps_frame = tk.Frame(dialog, bg='#1e293b')
        fps_frame.pack(fill='x', padx=30, pady=10)
        
        ttk.Label(
            fps_frame,
            text="Output FPS:",
            background='#1e293b',
            foreground='#e2e8f0'
        ).pack(side='left')
        
        fps_spinbox = ttk.Spinbox(
            fps_frame,
            from_=15,
            to=120,
            textvariable=self.video_fps_var,
            width=10
        )
        fps_spinbox.pack(side='left', padx=10)
        
        # Quality setting
        quality_frame = tk.Frame(dialog, bg='#1e293b')
        quality_frame.pack(fill='x', padx=30, pady=10)
        
        ttk.Label(
            quality_frame,
            text="Quality:",
            background='#1e293b',
            foreground='#e2e8f0'
        ).pack(side='left')
        
        quality_menu = ttk.Combobox(
            quality_frame,
            textvariable=self.video_quality_var,
            values=['low', 'medium', 'high', 'ultra', 'lossless'],
            state='readonly',
            width=15
        )
        quality_menu.pack(side='left', padx=10)
        
        # Generate button
        generate_btn = tk.Button(
            dialog,
            text="🎬 Generate Video",
            command=lambda: self._generate_video(dialog),
            bg='#8b5cf6',
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        generate_btn.pack(pady=30)
    
    def _generate_video(self, dialog):
        """Generate video from frames."""
        dialog.destroy()
        
        # Create progress dialog
        progress_dialog = tk.Toplevel(self.root)
        progress_dialog.title("Generating Video")
        progress_dialog.geometry("400x150")
        progress_dialog.configure(bg='#1e293b')
        progress_dialog.transient(self.root)
        progress_dialog.grab_set()
        
        # Center progress dialog
        progress_dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (progress_dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (progress_dialog.winfo_height() // 2)
        progress_dialog.geometry(f"+{x}+{y}")
        
        # Progress message
        msg = ttk.Label(
            progress_dialog,
            text="🎬 Generating video...\n\nThis may take a few moments.",
            font=('Segoe UI', 11),
            foreground='#e2e8f0',
            background='#1e293b',
            justify='center'
        )
        msg.pack(pady=20)
        
        # Progress bar
        progress = ttk.Progressbar(
            progress_dialog,
            mode='indeterminate',
            length=300
        )
        progress.pack(pady=10)
        progress.start(10)
        
        def generate():
            try:
                # Get absolute path to frames folder
                frames_path = str(FRAMES_FOLDER.absolute())
                
                # Use correct API endpoint for video generation
                response = requests.post(
                    'http://localhost:5000/api/video/generate',
                    json={
                        'frame_folders': [frames_path],  # Array of frame folder paths
                        'output_name': f"sorting_lightning_{int(time.time())}",
                        'fps': int(self.video_fps_var.get()),
                        'quality': self.video_quality_var.get()
                    },
                    timeout=300
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        # Extract video path from the response
                        video_info = result.get('video', {})
                        output_path = video_info.get('path', 'output/videos/')
                        self.root.after(0, lambda: progress_dialog.destroy())
                        self.root.after(0, lambda path=output_path: self._show_video_success(path))
                    else:
                        error_msg = f"❌ Video generation failed:\n\n{result.get('message', 'Unknown error')}"
                        self.root.after(0, lambda: progress_dialog.destroy())
                        self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                            "Error", msg))
                else:
                    error_msg = f"❌ Server error (Status {response.status_code}):\n\n" \
                               f"{response.text}"
                    self.root.after(0, lambda: progress_dialog.destroy())
                    self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                        "Server Error", msg))
                
            except requests.exceptions.ConnectionError as err:
                error_msg = "❌ Cannot connect to backend server!\n\n" \
                           "Make sure the Loops server is running.\n" \
                           "Start it with: python run.py"
                self.root.after(0, lambda: progress_dialog.destroy())
                self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                    "Connection Error", msg))
            except requests.exceptions.Timeout as err:
                error_msg = "❌ Video generation timed out!\n\n" \
                           "The video might be too long or complex.\n" \
                           "Try with fewer frames or lower quality."
                self.root.after(0, lambda: progress_dialog.destroy())
                self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                    "Timeout Error", msg))
            except Exception as err:
                error_msg = f"❌ Unexpected error:\n\n{err}"
                self.root.after(0, lambda: progress_dialog.destroy())
                self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                    "Error", msg))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def _show_video_success(self, output_path):
        """Show success dialog after video generation."""
        result = messagebox.askyesno(
            "Success!",
            f"✅ Video generated successfully!\n\n"
            f"Location:\n{output_path}\n\n"
            "Open the output folder?"
        )
        
        if result:
            try:
                output_folder = Path(output_path).parent
                if sys.platform == 'win32':
                    os.startfile(output_folder)
                elif sys.platform == 'darwin':
                    subprocess.run(['open', str(output_folder)])
                else:
                    subprocess.run(['xdg-open', str(output_folder)])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open folder:\n{e}")
    
    def _launch_simulation(self):
        """Launch the sorting visualization."""
        try:
            # Get settings
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            fps = int(self.fps_var.get())
            algorithm_display = self.algorithm_var.get()
            algorithm = self.algo_map.get(algorithm_display, "bubble")
            bar_count = self.bar_count_var.get()
            speed = self.speed_var.get()
            theme_display = self.theme_var.get()
            theme = self.theme_map.get(theme_display, "neon")
            effects = self.effects_var.get()
            auto_record = self.auto_record_var.get()
            
            # Build command
            main_script = SIMULATION_DIR / "main.py"
            
            cmd = [
                sys.executable,
                str(main_script),
                "--width", str(width),
                "--height", str(height),
                "--fps", str(fps),
                "--algorithm", algorithm,
                "--bars", str(bar_count),
                "--speed", str(speed),
                "--theme", theme
            ]
            
            if not effects:
                cmd.append("--no-effects")
            
            if auto_record:
                cmd.append("--record")
            
            # Launch in separate process
            self.simulation_process = subprocess.Popen(
                cmd,
                cwd=str(SIMULATION_DIR)
            )
            
            messagebox.showinfo(
                "Launched",
                "⚡ Sorting Lightning visualization launched!\n\n"
                "Check the new window for the visualization."
            )
            
        except ValueError as e:
            messagebox.showerror(
                "Invalid Input",
                f"❌ Invalid settings:\n\n{e}\n\n"
                "Please check your width, height, and FPS values."
            )
        except Exception as e:
            messagebox.showerror(
                "Launch Error",
                f"❌ Failed to launch simulation:\n\n{e}"
            )
    
    def run(self):
        """Start the control panel."""
        self.root.mainloop()


def main():
    """Entry point for control panel."""
    app = ControlPanel()
    app.run()


if __name__ == "__main__":
    main()
