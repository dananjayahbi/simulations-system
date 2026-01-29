# ✅ Dependency Management Added

## Summary

The Loops plugin system now supports automatic dependency installation during plugin upload. This makes it easy for plugins to specify their required Python packages, which are automatically installed when the plugin is added to the system.

---

## 🎯 What Was Added

### 1. Automatic Dependency Installation

**File**: `backend/addon_manager.py`

**New Method**: `_install_dependencies()`

```python
def _install_dependencies(self, addon_id: str, requirements_file: Path) -> Tuple[bool, str]:
    """Install Python dependencies from requirements.txt."""
    # Reads requirements.txt
    # Uses system Python to install via pip
    # Has 5-minute timeout
    # Logs success/failure
```

**Integration**:
- During `install_addon()`, after extracting ZIP
- If `requirements.txt` exists, automatically install dependencies
- Non-blocking: Dependency failure logs warning but doesn't fail installation
- Uses the same Python interpreter running the system

---

### 2. Documentation Updated

**File**: `docs/AI_PLUGIN_CREATION_GUIDE.md`

**New Section**: "Dependencies and Requirements"

Covers:
- Purpose and format of requirements.txt
- Automatic installation process
- Timeout (5 minutes)
- Best practices for specifying dependencies
- Common dependencies for Loops plugins
- Compatibility notes
- Complete example

---

### 3. Example Plugin Updated

**File**: `external-addons-dev/sorting_circles/requirements.txt`

```
# Sorting Circles - Python Dependencies
pygame-ce>=2.3.2
requests>=2.28.0
```

**Repackaged**: `sorting_circles.zip` (10 KB)

---

## 📝 Requirements.txt Format

### Standard Pip Format

```
# Comments start with #
package-name>=version
another-package==exact.version
third-package  # Any version
```

### Example for Loops Plugin

```
# Core visualization (usually pre-installed)
pygame-ce>=2.3.2

# Numerical computing
numpy>=1.20.0

# Image processing
pillow>=9.0.0

# HTTP requests (for API calls)
requests>=2.28.0

# Scientific computing (if needed)
scipy>=1.7.0
```

---

## 🔧 How It Works

### Installation Flow

```
1. User uploads plugin.zip
   │
2. System extracts ZIP to temp directory
   │
3. Validates plugin structure
   │
4. Copies to simulations/ directory
   │
5. ✨ Checks for requirements.txt ✨
   │
   ├─ If exists:
   │  ├─ Parse requirements
   │  ├─ Run: pip install <packages>
   │  ├─ Log success/failure
   │  └─ Continue (non-blocking)
   │
   └─ If not exists: Skip
   │
6. Create output directories
   │
7. Update registry
   │
8. Installation complete!
```

### Command Executed

```bash
python -m pip install package1 package2 package3
```

### Timeout

- Maximum: 5 minutes
- If exceeded: Logs warning, continues installation
- Prevents hanging on large/slow dependencies

---

## ✅ Best Practices

### For Plugin Creators

1. **Pin Major Versions**: Use `>=` for flexibility
   ```
   ✅ numpy>=1.20.0
   ❌ numpy==1.20.3
   ```

2. **Keep Minimal**: Only include necessary packages
   ```
   ✅ 3-5 dependencies
   ❌ 20+ dependencies
   ```

3. **Test First**: Install locally before packaging
   ```bash
   pip install -r requirements.txt
   ```

4. **Document Purpose**: Add comments explaining each dependency
   ```
   # numpy - For array operations and fast computations
   numpy>=1.20.0
   ```

5. **Check Compatibility**: Ensure packages work with Python version
   ```
   # Most Loops systems use Python 3.8+
   ```

---

## 🎨 Common Dependencies

### Usually Pre-installed
- `pygame-ce` - Graphics engine
- `tkinter` - GUI (part of Python)

### Commonly Needed
- `numpy` - Numerical computing
- `pillow` - Image processing
- `requests` - HTTP requests
- `scipy` - Scientific computing
- `matplotlib` - Plotting (if needed)

### Avoid If Possible
- `tensorflow`, `torch` - Very large, slow install
- `opencv-python` - Large, may need system dependencies
- System packages - Won't install via pip

---

## ⚠️ Important Notes

### Non-Blocking
- Dependency installation failure **does not fail** plugin installation
- Warning logged, but plugin still installs
- User can manually install dependencies later if needed

### System Python
- Uses the same Python running the Loops server
- Dependencies install globally or in virtual environment
- May need elevated permissions in some cases

### Timeout
- 5-minute maximum per installation
- Prevents hanging on problematic packages
- Consider splitting large dependencies into optional features

### Compatibility
- Ensure packages are compatible with:
  - Python version (usually 3.8+)
  - Operating system (Windows, Linux, macOS)
  - Architecture (x64, arm64)

---

## 🧪 Testing

### Local Testing

```bash
cd my_plugin/

# Create virtual environment
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
test_env\Scripts\activate     # Windows

# Test installation
pip install -r requirements.txt

# Test plugin
python main.py

# Deactivate
deactivate
```

### After Upload

1. Check server logs for dependency installation messages
2. Look for:
   ```
   Installing 2 dependencies for 'plugin_name'...
   Dependencies installed successfully for 'plugin_name'
   ```
3. If warnings appear, install manually:
   ```bash
   pip install -r simulations/plugin_name/requirements.txt
   ```

---

## 📊 Example Output

### Successful Installation

```
INFO | Uploading add-on file: my_plugin.zip
INFO | Installing dependencies for 'my_plugin'...
INFO | Installing 3 dependencies for 'my_plugin'...
INFO | Dependencies installed successfully for 'my_plugin'
INFO | Add-on 'my_plugin' installed successfully
```

### Failed Dependencies (Non-Critical)

```
INFO | Uploading add-on file: my_plugin.zip
INFO | Installing dependencies for 'my_plugin'...
WARNING | Dependency installation warning: Installation failed: ...
INFO | Add-on 'my_plugin' installed successfully
```

---

## 🎉 Summary

✅ **Automatic**: requirements.txt processed during upload
✅ **Non-Blocking**: Failure doesn't prevent installation
✅ **Standard Format**: Uses pip requirements format
✅ **Documented**: Comprehensive guide in AI_PLUGIN_CREATION_GUIDE.md
✅ **Timeout**: 5-minute safety limit
✅ **Logging**: Clear messages for success/failure

**The plugin system now handles dependencies automatically! 🚀**

---

## 📦 Files Changed

1. `backend/addon_manager.py` - Added `_install_dependencies()` method
2. `docs/AI_PLUGIN_CREATION_GUIDE.md` - Added dependencies section
3. `external-addons-dev/sorting_circles/requirements.txt` - Example file
4. `external-addons-dev/sorting_circles.zip` - Repackaged (10 KB)

---

*Feature Added: January 28, 2026*
*Status: Ready for testing*
