# Plugin Development Guide - Part 1: Getting Started

## 📚 Table of Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Required Files](#required-files)
- [Setting Up Your Environment](#setting-up-your-environment)
- [Quick Start Template](#quick-start-template)

---

## Introduction

Welcome to the Loops Plugin Development Guide! This guide will walk you through creating a fully functional visualization plugin for the Loops system.

### What is a Loops Plugin?

A Loops plugin is a self-contained visualization module that:
- Runs as a **separate process** from the main system
- Has its own **control panel** (Tkinter-based GUI)
- Displays a **clean simulation window** (Pygame-based)
- Saves **frames** for video generation
- Can be installed via the web dashboard

### The Two-Window Architecture

**CRITICAL CONCEPT:** Every plugin has TWO separate windows:

1. **Control Panel Window** (Tkinter)
   - Contains ALL user controls and settings
   - Launches the simulation
   - Manages frame operations and video generation
   - Stays open independently

2. **Simulation Window** (Pygame)
   - CLEAN visual display only
   - Minimal or NO UI overlays (only status indicators)
   - Runs in a separate process
   - Controlled by keyboard shortcuts

---

## Prerequisites

### Required Knowledge
- **Python 3.8+**: Basic to intermediate Python programming
- **Pygame**: Basic knowledge of Pygame for graphics
- **Tkinter**: Basic GUI development (we provide templates)
- **Git**: Basic version control (optional but recommended)

### Required Software
- Python 3.8 or higher
- Pygame library
- FFmpeg (for video generation)
- Text editor or IDE (VS Code recommended)

### System Requirements
- Windows, macOS, or Linux
- 4GB+ RAM recommended
- Disk space for frame storage and videos

---

## Project Structure

Your plugin **MUST** follow this exact structure:

```
your_plugin_name/
├── __init__.py              # Package initialization (REQUIRED)
├── simulation.json          # Metadata configuration (REQUIRED)
├── main.py                  # Simulation entry point (REQUIRED)
├── control_panel.py         # Control panel GUI (REQUIRED)
├── requirements.txt         # Python dependencies (RECOMMENDED)
├── README.md                # Documentation (RECOMMENDED)
└── frames/                  # Frame storage (auto-created at runtime)
    └── frame_000001.png     # Sequential frame files
```

### File Locations

**For External Addons (Recommended):**
```
loops/
└── external-addons-dev/
    └── your_plugin_name/
        ├── __init__.py
        ├── simulation.json
        ├── main.py
        ├── control_panel.py
        └── ...
```

**For Built-in Simulations:**
```
loops/
└── simulations/
    └── your_plugin_name/
        ├── __init__.py
        ├── simulation.json
        ├── main.py
        ├── control_panel.py
        └── ...
```

---

## Required Files

### 1. `__init__.py`

Makes your plugin a Python package.

**Template:**
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
Sorting Lightning - Advanced Sorting Visualization
==================================================
Eye-catching sorting visualization with lightning effects and particles.

Author: AI Assistant
Version: 1.0.0
"""

from .main import SortingLightning, main

__all__ = ['SortingLightning', 'main']
__version__ = '1.0.0'
```

---

### 2. `simulation.json`

Configuration file that tells Loops about your plugin.

**Template:**
```json
{
  "id": "your_plugin_id",
  "name": "Your Plugin Display Name",
  "description": "Clear description of what your plugin does.",
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

**Field Descriptions:**

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `id` | ✅ Yes | Unique identifier (lowercase, underscores only) | `"sorting_lightning"` |
| `name` | ✅ Yes | Display name (can have spaces) | `"⚡ Sorting Lightning"` |
| `description` | ✅ Yes | Brief description of your plugin | `"Advanced sorting..."` |
| `icon` | ✅ Yes | Single emoji representing your plugin | `"⚡"` |
| `color` | ✅ Yes | Hex color for plugin card | `"#a855f7"` |
| `version` | ✅ Yes | Semantic version number | `"1.0.0"` |
| `author` | ✅ Yes | Your name or organization | `"Your Name"` |
| `license` | ✅ Yes | License type | `"MIT"` |
| `homepage` | ❌ No | Project website/repo URL | `"https://..."` |
| `min_loops_version` | ❌ No | Minimum Loops version required | `"1.0.0"` |
| `tags` | ❌ No | Array of category tags | `["sorting", "algorithm"]` |
| `requires_pygame` | ✅ Yes | Must be `true` for pygame plugins | `true` |
| `entry_point` | ✅ Yes | Always `"main.py"` | `"main.py"` |
| `control_panel` | ✅ Yes | Always `"control_panel.py"` | `"control_panel.py"` |
| `dependencies` | ❌ No | Extra Python packages needed | `["numpy", "scipy"]` |

---

### 3. `requirements.txt`

List Python packages your plugin needs (one per line).

**Example:**
```
pygame>=2.0.0
requests>=2.25.0
numpy>=1.20.0
```

**Important Notes:**
- Only list **external packages** (not built-in modules like `os`, `sys`)
- Use version constraints: `>=`, `==`, `~=`
- Don't include `pygame` if it's already in Loops
- Keep it minimal - only what you actually use

---

## Setting Up Your Environment

### Step 1: Clone or Navigate to Loops

```bash
cd /path/to/loops
```

### Step 2: Create Your Plugin Directory

```bash
# For external addon
mkdir -p external-addons-dev/my_awesome_plugin
cd external-addons-dev/my_awesome_plugin

# OR for built-in simulation
mkdir -p simulations/my_awesome_plugin
cd simulations/my_awesome_plugin
```

### Step 3: Create Required Files

```bash
# Create empty files
touch __init__.py
touch simulation.json
touch main.py
touch control_panel.py
touch requirements.txt
touch README.md
```

### Step 4: Copy Templates

Use the templates provided in this guide to populate your files.

---

## Quick Start Template

Here's a minimal plugin structure to get you started:

### `__init__.py`
```python
"""
My Plugin - Description
"""
from .main import MyPlugin, main
__all__ = ['MyPlugin', 'main']
__version__ = '1.0.0'
```

### `simulation.json`
```json
{
  "id": "my_plugin",
  "name": "My Awesome Plugin",
  "description": "A simple visualization plugin.",
  "icon": "🎮",
  "color": "#3b82f6",
  "version": "1.0.0",
  "author": "Your Name",
  "license": "MIT",
  "tags": ["visualization"],
  "requires_pygame": true,
  "entry_point": "main.py",
  "control_panel": "control_panel.py",
  "dependencies": []
}
```

### `requirements.txt`
```
pygame>=2.0.0
```

---

## Next Steps

Now that you understand the basic structure, proceed to:

- **Part 2: Main Simulation** - Learn how to create the pygame visualization
- **Part 3: Control Panel** - Build the configuration GUI
- **Part 4: Video Generation & API** - Integrate video recording
- **Part 5: Common Pitfalls** - Avoid common mistakes

---

## Quick Reference Checklist

Before moving to Part 2, make sure you have:

- [ ] Created plugin directory in correct location
- [ ] Created all required files (`__init__.py`, `simulation.json`, `main.py`, `control_panel.py`)
- [ ] Populated `simulation.json` with correct metadata
- [ ] Listed dependencies in `requirements.txt`
- [ ] Understood the two-window architecture concept

---

## Getting Help

- Check the existing plugins: `sorting_lightning`, `sorting_circles`
- Read the AI_PLUGIN_CREATION_GUIDE.md for detailed reference
- Review Part 5 for troubleshooting common issues

**Ready?** Let's move to [Part 2: Main Simulation](./02_main_simulation.md)!
