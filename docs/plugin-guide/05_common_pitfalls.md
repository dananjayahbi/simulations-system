# Plugin Development Guide - Part 5: Common Pitfalls & Solutions

## 📚 Table of Contents
- [Path Issues](#path-issues)
- [Import Errors](#import-errors)
- [Threading Problems](#threading-problems)
- [Video Generation Issues](#video-generation-issues)
- [UI/Layout Issues](#uilayout-issues)
- [Frame Management](#frame-management)
- [Performance Issues](#performance-issues)
- [Debugging Tips](#debugging-tips)

---

## Path Issues

### ❌ Problem: Hardcoded Paths

```python
# Wrong - breaks on other systems
self.frames_folder = "C:/Users/me/loops/frames"
self.frames_folder = "/home/user/loops/frames"
```

### ✅ Solution: Use Relative Paths

```python
from pathlib import Path

current_dir = Path(__file__).parent
self.frames_folder = str(current_dir / "frames")
```

---

### ❌ Problem: Wrong Path for Video API

```python
# Wrong - relative path
frames_path = "frames"
response = requests.post(url, json={'frame_folders': [frames_path]})
```

### ✅ Solution: Use Absolute Paths

```python
# Correct - absolute path
frames_path = str(FRAMES_FOLDER.absolute())
response = requests.post(url, json={'frame_folders': [frames_path]})
```

---

### ❌ Problem: Path Separators

```python
# Wrong - hardcoded separators
path = "loops\\frames\\output"  # Breaks on Linux/Mac
```

### ✅ Solution: Use Path Objects

```python
# Correct - cross-platform
path = Path("loops") / "frames" / "output"
```

---

## Import Errors

### ❌ Problem: Cannot Import BaseSimulation

```
ModuleNotFoundError: No module named 'base_simulation'
```

### ✅ Solution: Add Shared to Path

```python
import sys
from pathlib import Path

current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent
shared_dir = root_dir / "shared"
sys.path.insert(0, str(shared_dir))

from base_simulation import BaseSimulation
```

---

### ❌ Problem: Import VideoGenerator Directly

```python
from shared.video_generator import VideoGenerator  # Don't do this!
```

### ✅ Solution: Use API Instead

```python
import requests

response = requests.post(
    'http://localhost:5000/api/video/generate',
    json={'frame_folders': [frames_path], ...}
)
```

---

## Threading Problems

### ❌ Problem: Variable Scope in Lambda

```python
except Exception as e:
    # Wrong - 'e' goes out of scope
    self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {e}"))
```

**Error:**
```
NameError: cannot access free variable 'e' where it is not associated with a value
```

### ✅ Solution: Capture Variable

```python
except Exception as err:
    # Correct - capture as default argument
    error_msg = f"Error: {err}"
    self.root.after(0, lambda msg=error_msg: messagebox.showerror("Error", msg))
```

---

### ❌ Problem: Updating GUI from Thread

```python
def generate():
    # ... video generation ...
    messagebox.showinfo("Done", "Video created!")  # CRASH!
```

**Error:**
```
RuntimeError: main thread is not in main loop
```

### ✅ Solution: Use root.after()

```python
def generate():
    # ... video generation ...
    self.root.after(0, lambda: messagebox.showinfo("Done", "Video created!"))
```

---

### ❌ Problem: Blocking GUI with Long Operation

```python
def _generate_video(self):
    # Wrong - freezes GUI
    response = requests.post(url, json=data, timeout=300)
    # GUI is frozen for up to 5 minutes!
```

### ✅ Solution: Use Background Thread

```python
def _generate_video(self):
    def generate():
        response = requests.post(url, json=data, timeout=300)
        # Update GUI safely
        self.root.after(0, lambda: self._handle_response(response))
    
    threading.Thread(target=generate, daemon=True).start()
```

---

## Video Generation Issues

### ❌ Problem: Wrong Endpoint

```python
response = requests.post(
    'http://localhost:5000/api/generate-video',  # Wrong URL!
    ...
)
```

**Error:**
```
405 Method Not Allowed
```

### ✅ Solution: Use Correct Endpoint

```python
response = requests.post(
    'http://localhost:5000/api/video/generate',  # Correct!
    ...
)
```

---

### ❌ Problem: Wrong Response Parsing

```python
if result.get('success'):  # Wrong field!
    path = result.get('video_path')  # Wrong field!
```

**Result:** Shows "Unknown error" even when video is generated

### ✅ Solution: Parse Correct Fields

```python
if result.get('status') == 'success':
    video_info = result.get('video', {})
    path = video_info.get('path')
```

---

### ❌ Problem: Missing Connection Error Handling

```python
try:
    response = requests.post(url, json=data)
except Exception as e:
    print(f"Error: {e}")
```

**Result:** Generic error message, user doesn't know server isn't running

### ✅ Solution: Handle Specific Errors

```python
try:
    response = requests.post(url, json=data, timeout=300)
except requests.exceptions.ConnectionError:
    messagebox.showerror(
        "Connection Error",
        "Cannot connect to backend server!\\n\\n"
        "Make sure Loops is running:\\npython run.py"
    )
except requests.exceptions.Timeout:
    messagebox.showerror(
        "Timeout",
        "Video generation timed out!\\n\\n"
        "Try with fewer frames or lower quality."
    )
except Exception as e:
    messagebox.showerror("Error", f"Unexpected error:\\n{e}")
```

---

## UI/Layout Issues

### ❌ Problem: Vertical Layout Requires Scrolling

```python
self.root.geometry("550x1200")  # Too tall!
```

**Result:** User has to scroll to see all controls

### ✅ Solution: Horizontal Layout

```python
self.root.geometry("900x650")  # Wide layout

# Use two columns
top_row = tk.Frame(main_frame)
top_row.pack(fill='x')

left_col = tk.Frame(top_row)
left_col.pack(side='left', fill='both', expand=True)

right_col = tk.Frame(top_row)
right_col.pack(side='left', fill='both', expand=True)
```

---

### ❌ Problem: Button Doesn't Launch

```python
subprocess.run([sys.executable, "main.py"])  # Blocks!
```

**Result:** Control panel freezes until simulation closes

### ✅ Solution: Use Popen

```python
subprocess.Popen([sys.executable, str(main_script)], cwd=str(SIMULATION_DIR))
```

---

## Frame Management

### ❌ Problem: Wrong Frame Naming

```python
frame_name = f"frame_{i}.png"  # Wrong!
```

**Result:** Video generation fails or frames out of order

### ✅ Solution: Zero-Padded Numbers

```python
frame_name = f"frame_{i:06d}.png"  # Correct: frame_000001.png
```

---

### ❌ Problem: Deleting Frames Freezes GUI

```python
def _clear_frames(self):
    for frame in frames:
        frame.unlink()  # Blocks GUI!
```

### ✅ Solution: Delete in Thread

```python
def _clear_frames(self):
    if not messagebox.askyesno("Confirm", "Delete all frames?"):
        return
    
    def delete():
        try:
            frames = list(FRAMES_FOLDER.glob("frame_*.png"))
            for frame in frames:
                frame.unlink()
            self.root.after(0, lambda: self._update_frame_count())
            self.root.after(0, lambda: messagebox.showinfo("Success", "Frames deleted!"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed: {e}"))
    
    threading.Thread(target=delete, daemon=True).start()
```

---

### ❌ Problem: Opening Folder Not Cross-Platform

```python
os.system(f'explorer "{folder}"')  # Windows only!
```

### ✅ Solution: Platform Detection

```python
def _open_folder(self):
    folder.mkdir(parents=True, exist_ok=True)
    
    if sys.platform == 'win32':
        os.startfile(folder)
    elif sys.platform == 'darwin':
        subprocess.run(['open', str(folder)])
    else:
        subprocess.run(['xdg-open', str(folder)])
```

---

## Performance Issues

### ❌ Problem: Creating Surfaces Every Frame

```python
def draw(self):
    bg = pygame.Surface((self.width, self.height))  # Slow!
    bg.fill(self.bg_color)
```

### ✅ Solution: Reuse Surfaces

```python
def __init__(self, ...):
    self.bg_surface = pygame.Surface((width, height))
    self.bg_surface.fill(self.bg_color)

def draw(self):
    self.screen.blit(self.bg_surface, (0, 0))
```

---

### ❌ Problem: Too Many Particles

```python
# Spawns 100 particles per frame = lag!
for _ in range(100):
    self.particles.append(Particle(...))
```

### ✅ Solution: Limit Particles

```python
MAX_PARTICLES = 500

if len(self.particles) < MAX_PARTICLES:
    for _ in range(5):  # Spawn fewer
        self.particles.append(Particle(...))
```

---

## Debugging Tips

### 1. Enable Debug Prints

```python
def _launch_simulation(self):
    print(f"Launching with command: {cmd}")
    process = subprocess.Popen(cmd, cwd=str(SIMULATION_DIR))
    print(f"Process ID: {process.pid}")
```

### 2. Check Frame Folder

```python
def _update_frame_count(self):
    if not FRAMES_FOLDER.exists():
        print(f"Frames folder doesn't exist: {FRAMES_FOLDER}")
        self.frame_count_label.config(text="0")
        return
    
    frames = list(FRAMES_FOLDER.glob("frame_*.png"))
    print(f"Found {len(frames)} frames in {FRAMES_FOLDER}")
    self.frame_count_label.config(text=str(len(frames)))
```

### 3. Print API Response

```python
response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

### 4. Test Standalone First

```bash
# Test simulation standalone
python main.py --width 800 --height 600

# Test with recording
python main.py --record
```

### 5. Check Pygame Version

```bash
python -c "import pygame; print(pygame.version.ver)"
```

---

## Troubleshooting Checklist

When something doesn't work, check:

- [ ] Is the Loops backend running? (`python run.py`)
- [ ] Are paths absolute (for API) or relative (for local files)?
- [ ] Are you using `Popen` (not `run`) to launch simulation?
- [ ] Are GUI updates from threads using `root.after()`?
- [ ] Are frame names zero-padded? (`frame_000001.png`)
- [ ] Is `BaseSimulation` imported correctly?
- [ ] Are all required files present? (`__init__.py`, `simulation.json`, etc.)
- [ ] Is `simulation.json` valid JSON?
- [ ] Are you using the correct API endpoint? (`/api/video/generate`)
- [ ] Is the response parsed correctly? (`result['video']['path']`)

---

## Getting Help

If you're still stuck:

1. **Check Example Plugins:**
   - `external-addons-dev/sorting_lightning`
   - `external-addons-dev/sorting_circles`

2. **Read Full Guide:**
   - `docs/AI_PLUGIN_CREATION_GUIDE.md`

3. **Check Logs:**
   - Backend logs in terminal running `python run.py`
   - Your plugin's print statements

4. **Test Components Separately:**
   - Test `main.py` standalone
   - Test control panel without launching simulation
   - Test API endpoint with curl/Postman

---

## Final Checklist

Before releasing your plugin:

### Required Files
- [ ] `__init__.py` with correct imports
- [ ] `simulation.json` with valid JSON
- [ ] `main.py` inheriting from `BaseSimulation`
- [ ] `control_panel.py` with API-based video generation
- [ ] `requirements.txt` with dependencies
- [ ] `README.md` with usage instructions

### Functionality
- [ ] Simulation launches from control panel
- [ ] Recording works (S key toggles)
- [ ] Frames save with correct naming
- [ ] Video generation works via API
- [ ] All keyboard shortcuts functional
- [ ] Cross-platform folder opening works

### Code Quality
- [ ] No hardcoded paths
- [ ] No direct VideoGenerator imports
- [ ] Threading for long operations
- [ ] Error handling for all API calls
- [ ] GUI updates use `root.after()`
- [ ] Clean, minimal simulation UI

### Testing
- [ ] Tested on fresh environment
- [ ] Tested standalone (`python main.py`)
- [ ] Tested via control panel
- [ ] Tested video generation
- [ ] Tested frame clearing
- [ ] Tested all error cases

---

## Success!

If you've followed all 5 guides and completed the checklist, your plugin is ready! 🎉

### Next Steps

1. **Test thoroughly** on a clean environment
2. **Create a zip file** for distribution:
   ```bash
   cd external-addons-dev
   zip -r your_plugin.zip your_plugin/
   ```
3. **Upload via Loops dashboard** or share with others
4. **Write good documentation** in your README.md

---

## Summary of All Guides

- **Part 1:** Project structure, required files, setup
- **Part 2:** Main simulation with `BaseSimulation`
- **Part 3:** Control panel with Tkinter
- **Part 4:** Video generation via API
- **Part 5:** Common mistakes and solutions

You now have everything needed to create professional Loops plugins! 🚀
