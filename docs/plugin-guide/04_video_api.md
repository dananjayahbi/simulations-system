# Plugin Development Guide - Part 4: Video Generation & API

## 📚 Table of Contents
- [Overview](#overview)
- [The Backend API](#the-backend-api)
- [Implementing Video Generation](#implementing-video-generation)
- [Complete Implementation](#complete-implementation)
- [Testing Video Generation](#testing-video-generation)

---

## Overview

Loops uses a **backend API** for video generation, not direct library imports. This ensures consistent behavior and prevents path/import issues across different plugin locations.

### ⚠️ CRITICAL: Use API, Not Direct Import

**❌ WRONG:**
```python
from shared.video_generator import VideoGenerator  # Don't do this!
```

**✅ CORRECT:**
```python
import requests

response = requests.post(
    'http://localhost:5000/api/video/generate',
    json={'frame_folders': ['/path/to/frames'], ...}
)
```

---

## The Backend API

### Endpoint Details

**URL:** `http://localhost:5000/api/video/generate`  
**Method:** `POST`  
**Content-Type:** `application/json`

### Request Parameters

```json
{
  "frame_folders": ["/absolute/path/to/frames"],
  "output_name": "my_video_20260129",
  "fps": 60,
  "quality": "high"
}
```

| Parameter | Required | Type | Description | Values |
|-----------|----------|------|-------------|--------|
| `frame_folders` | ✅ Yes | array | Absolute paths to frame directories | `["/path/to/frames"]` |
| `output_name` | ❌ No | string | Video filename (without extension) | `"sorting_20260129"` |
| `fps` | ❌ No | integer | Frames per second | 15-120 (default: 60) |
| `quality` | ❌ No | string | Video quality preset | `"low"`, `"medium"`, `"high"`, `"ultra"`, `"lossless"` (default: `"high"`) |

### Response Format

**Success (200 OK):**
```json
{
  "status": "success",
  "message": "Video generated successfully",
  "video": {
    "path": "/absolute/path/to/video.mp4",
    "name": "video.mp4",
    "size_mb": 15.3
  }
}
```

**Error (400/500):**
```json
{
  "status": "error",
  "message": "Error description here"
}
```

---

## Implementing Video Generation

### Step 1: Add Requests Dependency

In `requirements.txt`:
```
pygame>=2.0.0
requests>=2.25.0
```

### Step 2: Import Requests

In `control_panel.py`:
```python
import requests
import time
```

### Step 3: Create Video Dialog

```python
def _show_video_dialog(self):
    """Show video generation settings dialog."""
    if not FRAMES_FOLDER.exists() or not list(FRAMES_FOLDER.glob("frame_*.png")):
        messagebox.showwarning(
            "No Frames",
            "⚠️ No frames found!\\n\\nLaunch the simulation and press 'S' to start recording."
        )
        return
    
    # Create dialog
    dialog = tk.Toplevel(self.root)
    dialog.title("🎥 Video Generation Settings")
    dialog.geometry("400x250")
    dialog.configure(bg='#1e293b')
    dialog.transient(self.root)
    dialog.grab_set()
    
    # Center dialog
    dialog.update_idletasks()
    x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Title
    ttk.Label(
        dialog,
        text="🎥 Video Generation",
        font=('Segoe UI', 16, 'bold'),
        foreground='#a855f7',
        background='#1e293b'
    ).pack(pady=20)
    
    # FPS setting
    fps_frame = tk.Frame(dialog, bg='#1e293b')
    fps_frame.pack(fill='x', padx=30, pady=10)
    
    ttk.Label(fps_frame, text="Output FPS:", background='#1e293b', 
             foreground='#e2e8f0').pack(side='left')
    fps_spinbox = ttk.Spinbox(fps_frame, from_=15, to=120, 
                               textvariable=self.video_fps_var, width=10)
    fps_spinbox.pack(side='left', padx=10)
    
    # Quality setting
    quality_frame = tk.Frame(dialog, bg='#1e293b')
    quality_frame.pack(fill='x', padx=30, pady=10)
    
    ttk.Label(quality_frame, text="Quality:", background='#1e293b',
             foreground='#e2e8f0').pack(side='left')
    quality_menu = ttk.Combobox(quality_frame, textvariable=self.video_quality_var,
                                values=['low', 'medium', 'high', 'ultra', 'lossless'],
                                state='readonly', width=15)
    quality_menu.pack(side='left', padx=10)
    
    # Generate button
    tk.Button(
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
    ).pack(pady=30)
```

### Step 4: Implement Video Generation

```python
def _generate_video(self, dialog):
    """Generate video from frames using API."""
    dialog.destroy()
    
    # Create progress dialog
    progress_dialog = tk.Toplevel(self.root)
    progress_dialog.title("Generating Video")
    progress_dialog.geometry("400x150")
    progress_dialog.configure(bg='#1e293b')
    progress_dialog.transient(self.root)
    progress_dialog.grab_set()
    
    # Center
    progress_dialog.update_idletasks()
    x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (progress_dialog.winfo_width() // 2)
    y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (progress_dialog.winfo_height() // 2)
    progress_dialog.geometry(f"+{x}+{y}")
    
    # Message
    ttk.Label(
        progress_dialog,
        text="🎬 Generating video...\\n\\nThis may take a few moments.",
        font=('Segoe UI', 11),
        foreground='#e2e8f0',
        background='#1e293b',
        justify='center'
    ).pack(pady=20)
    
    # Progress bar
    progress = ttk.Progressbar(progress_dialog, mode='indeterminate', length=300)
    progress.pack(pady=10)
    progress.start(10)
    
    # Generate in thread
    def generate():
        try:
            # Get absolute path to frames
            frames_path = str(FRAMES_FOLDER.absolute())
            
            # Call API
            response = requests.post(
                'http://localhost:5000/api/video/generate',
                json={
                    'frame_folders': [frames_path],
                    'output_name': f"[plugin_name]_{int(time.time())}",
                    'fps': int(self.video_fps_var.get()),
                    'quality': self.video_quality_var.get()
                },
                timeout=300
            )
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    video_info = result.get('video', {})
                    output_path = video_info.get('path', '')
                    
                    self.root.after(0, lambda: progress_dialog.destroy())
                    self.root.after(0, lambda path=output_path: self._show_video_success(path))
                else:
                    error_msg = f"❌ Video generation failed:\\n\\n{result.get('message', 'Unknown error')}"
                    self.root.after(0, lambda: progress_dialog.destroy())
                    self.root.after(0, lambda msg=error_msg: messagebox.showerror("Error", msg))
            else:
                error_msg = f"❌ Server error (Status {response.status_code}):\\n\\n{response.text}"
                self.root.after(0, lambda: progress_dialog.destroy())
                self.root.after(0, lambda msg=error_msg: messagebox.showerror("Server Error", msg))
        
        except requests.exceptions.ConnectionError:
            error_msg = "❌ Cannot connect to backend server!\\n\\nMake sure the Loops server is running.\\nStart it with: python run.py"
            self.root.after(0, lambda: progress_dialog.destroy())
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("Connection Error", msg))
        
        except requests.exceptions.Timeout:
            error_msg = "❌ Video generation timed out!\\n\\nThe video might be too long or complex.\\nTry with fewer frames or lower quality."
            self.root.after(0, lambda: progress_dialog.destroy())
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("Timeout Error", msg))
        
        except Exception as err:
            error_msg = f"❌ Unexpected error:\\n\\n{err}"
            self.root.after(0, lambda: progress_dialog.destroy())
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("Error", msg))
    
    threading.Thread(target=generate, daemon=True).start()
```

### Step 5: Handle Success

```python
def _show_video_success(self, output_path):
    """Show success dialog."""
    result = messagebox.askyesno(
        "Success!",
        f"✅ Video generated successfully!\\n\\n"
        f"Location:\\n{output_path}\\n\\n"
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
            messagebox.showerror("Error", f"Failed to open folder:\\n{e}")
```

---

## Complete Implementation

Here's the full video generation code to add to your `control_panel.py`:

```python
# At the top, add imports:
import requests
import time

# In __init__, add video variables:
self.video_fps_var = tk.StringVar(value="60")
self.video_quality_var = tk.StringVar(value="high")

# Then add these methods to your ControlPanel class:

def _show_video_dialog(self):
    # ... (see Step 3 above)

def _generate_video(self, dialog):
    # ... (see Step 4 above)

def _show_video_success(self, output_path):
    # ... (see Step 5 above)
```

---

## Testing Video Generation

### Prerequisites

1. **Start the Loops backend server:**
   ```bash
   cd /path/to/loops
   python run.py
   ```

2. **Generate some frames:**
   - Launch your simulation from control panel
   - Press `S` to start recording
   - Let it run for a few seconds
   - Press `S` again to stop recording

3. **Test video generation:**
   - Click "Generate Video" in control panel
   - Wait for progress bar
   - Check if video opens successfully

### Common Issues

#### Issue: "Cannot connect to backend server"
**Solution:** Make sure `python run.py` is running

#### Issue: "No frames found"
**Solution:** Record some frames first (press `S` in simulation)

#### Issue: "Unknown error" but video exists
**Solution:** Check response parsing - make sure you're extracting `result['video']['path']` not `result['video_path']`

#### Issue: 405 Method Not Allowed
**Solution:** Make sure you're using POST to `/api/video/generate` (not `/api/generate-video`)

---

## Best Practices

### 1. Always Use Absolute Paths

```python
# ✅ Correct
frames_path = str(FRAMES_FOLDER.absolute())

# ❌ Wrong
frames_path = "frames"  # Relative path won't work
```

### 2. Use Threading for API Calls

```python
# ✅ Correct - non-blocking
threading.Thread(target=generate_function, daemon=True).start()

# ❌ Wrong - blocks GUI
response = requests.post(...)  # UI freezes during generation
```

### 3. Handle All Error Types

```python
try:
    # API call
except requests.exceptions.ConnectionError:
    # Server not running
except requests.exceptions.Timeout:
    # Took too long
except Exception as err:
    # Unexpected error
```

### 4. Update GUI from Threads Safely

```python
# ✅ Correct
self.root.after(0, lambda: messagebox.showinfo("Done", "Success!"))

# ❌ Wrong
messagebox.showinfo("Done", "Success!")  # From thread = crash
```

---

## Next Steps

Video generation complete! Now learn about:

- **Part 5: Common Pitfalls & Solutions** - Avoid common mistakes and debug issues

---

## Quick Checklist

- [ ] Using API endpoint (not direct import)
- [ ] Added `requests` to requirements.txt
- [ ] Using absolute paths for frame folders
- [ ] Video generation runs in thread
- [ ] GUI updates use `root.after()`
- [ ] All error types handled
- [ ] Success dialog opens folder

**Ready for the final part?** → [Common Pitfalls & Solutions](./05_common_pitfalls.md)
