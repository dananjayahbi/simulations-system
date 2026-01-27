# Loops Visualization System - Modular Add-on Architecture

## Overview

This document describes the new modular add-on architecture for the Loops Visualization System. The goal is to enable scalable, independent simulation development where AI-generated or third-party simulations can be easily packaged, uploaded, installed, and removed without requiring access to the core system codebase.

---

## Architecture Vision

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LOOPS MASTER CONTROL DASHBOARD                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Dashboard   │  │ Simulations  │  │   Outputs    │  │   Add-ons    │     │
│  │     📊       │  │     🎮       │  │     🎬       │  │     📦       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND SERVER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │ Simulation API  │  │   Add-on API    │  │   Video API     │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│           │                    │                    │                        │
│           ▼                    ▼                    ▼                        │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │                     ADD-ON MANAGER SERVICE                       │        │
│  │  • Install (.zip upload)    • Validate structure                 │        │
│  │  • Uninstall (clean remove) • Dependency check                   │        │
│  │  • Enable/Disable           • Version management                 │        │
│  └─────────────────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SIMULATIONS DIRECTORY                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  simulations/                                                                │
│  ├── sorting_visualizer/        ← Built-in simulation                       │
│  ├── wave_patterns/             ← Uploaded add-on                           │
│  ├── fractal_generator/         ← Uploaded add-on                           │
│  └── physics_sandbox/           ← Uploaded add-on                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Add-on Manager Service

The Add-on Manager is a new backend service responsible for:

| Function | Description |
|----------|-------------|
| **Install** | Extract .zip, validate structure, copy to simulations folder |
| **Uninstall** | Remove simulation folder and all associated data cleanly |
| **Validate** | Check add-on structure, dependencies, and compatibility |
| **Enable/Disable** | Toggle simulation availability without removal |
| **List** | Enumerate installed add-ons with metadata |

```
┌─────────────────────────────────────────────────────────────────┐
│                      ADD-ON MANAGER SERVICE                      │
│                                                                  │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐ │
│  │    Installer   │    │   Validator    │    │   Uninstaller  │ │
│  │                │    │                │    │                │ │
│  │ • Extract ZIP  │    │ • Check JSON   │    │ • Remove files │ │
│  │ • Copy files   │    │ • Verify files │    │ • Clean frames │ │
│  │ • Set perms    │    │ • Check deps   │    │ • Remove videos│ │
│  └────────────────┘    └────────────────┘    └────────────────┘ │
│           │                    │                    │            │
│           └────────────────────┼────────────────────┘            │
│                                ▼                                 │
│                    ┌────────────────────┐                        │
│                    │   Add-on Registry  │                        │
│                    │   (addons.json)    │                        │
│                    └────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Add-on Package Structure

Each add-on is a `.zip` file containing a standardized folder structure:

```
simulation_name.zip
├── simulation.json          ← Required: Metadata & configuration
├── main.py                  ← Required: Entry point
├── control_panel.py         ← Optional: GUI control panel
├── requirements.txt         ← Optional: Python dependencies
├── README.md                ← Optional: Documentation
├── config.py                ← Optional: Configuration
├── __init__.py              ← Required: Package init
└── assets/                  ← Optional: Images, sounds, data
    ├── images/
    └── data/
```

### 3. Dashboard Add-on Management Page

New dashboard section for add-on management:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Add-ons                                                    [Upload Add-on] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  📦 Sorting Visualizer                               v1.0.0         │   │
│  │  Visualize sorting algorithms with rainbow gradient bars             │   │
│  │  ────────────────────────────────────────────────────────────────── │   │
│  │  Author: Loops System  │  Status: ● Enabled  │  [Disable] [Remove]  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  🌊 Wave Patterns                                    v2.1.0         │   │
│  │  Generate beautiful wave interference patterns                       │   │
│  │  ────────────────────────────────────────────────────────────────── │   │
│  │  Author: AI Generated  │  Status: ● Enabled  │  [Disable] [Remove]  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Add-on Installation Flow

```
┌──────────┐     ┌──────────────┐     ┌─────────────┐     ┌───────────────┐
│  User    │     │   Frontend   │     │   Backend   │     │  File System  │
│          │     │  Dashboard   │     │   Server    │     │               │
└────┬─────┘     └──────┬───────┘     └──────┬──────┘     └───────┬───────┘
     │                  │                    │                    │
     │  Select .zip     │                    │                    │
     │─────────────────>│                    │                    │
     │                  │                    │                    │
     │                  │  POST /api/addon/  │                    │
     │                  │  upload (multipart)│                    │
     │                  │───────────────────>│                    │
     │                  │                    │                    │
     │                  │                    │  Save temp file    │
     │                  │                    │───────────────────>│
     │                  │                    │                    │
     │                  │                    │  Validate structure│
     │                  │                    │<───────────────────│
     │                  │                    │                    │
     │                  │                    │  Extract to        │
     │                  │                    │  simulations/      │
     │                  │                    │───────────────────>│
     │                  │                    │                    │
     │                  │   Success/Error    │                    │
     │                  │<───────────────────│                    │
     │                  │                    │                    │
     │  Show result     │                    │                    │
     │<─────────────────│                    │                    │
     │                  │                    │                    │
```

### Add-on Uninstallation Flow

```
┌──────────┐     ┌──────────────┐     ┌─────────────┐     ┌───────────────┐
│  User    │     │   Frontend   │     │   Backend   │     │  File System  │
│          │     │  Dashboard   │     │   Server    │     │               │
└────┬─────┘     └──────┬───────┘     └──────┬──────┘     └───────┬───────┘
     │                  │                    │                    │
     │  Click Remove    │                    │                    │
     │─────────────────>│                    │                    │
     │                  │                    │                    │
     │                  │  Confirm dialog    │                    │
     │<─────────────────│                    │                    │
     │                  │                    │                    │
     │  Confirm         │                    │                    │
     │─────────────────>│                    │                    │
     │                  │                    │                    │
     │                  │ DELETE /api/addon/ │                    │
     │                  │ {addon_id}         │                    │
     │                  │───────────────────>│                    │
     │                  │                    │                    │
     │                  │                    │  Stop if running   │
     │                  │                    │───────────────────>│
     │                  │                    │                    │
     │                  │                    │  Remove:           │
     │                  │                    │  • simulations/id/ │
     │                  │                    │  • output/frames/  │
     │                  │                    │  • output/videos/  │
     │                  │                    │───────────────────>│
     │                  │                    │                    │
     │                  │   Success          │                    │
     │                  │<───────────────────│                    │
     │                  │                    │                    │
     │  Update UI       │                    │                    │
     │<─────────────────│                    │                    │
```

---

## API Endpoints

### Add-on Management API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/addon/list` | GET | List all installed add-ons |
| `/api/addon/upload` | POST | Upload and install new add-on (.zip) |
| `/api/addon/{id}` | GET | Get add-on details |
| `/api/addon/{id}` | DELETE | Uninstall add-on completely |
| `/api/addon/{id}/enable` | POST | Enable disabled add-on |
| `/api/addon/{id}/disable` | POST | Disable add-on (keep files) |
| `/api/addon/{id}/export` | GET | Export add-on as .zip |

### Request/Response Examples

#### Upload Add-on
```http
POST /api/addon/upload
Content-Type: multipart/form-data

file: [simulation.zip]
```

Response:
```json
{
  "status": "success",
  "message": "Add-on installed successfully",
  "addon": {
    "id": "wave_patterns",
    "name": "Wave Patterns",
    "version": "1.0.0",
    "installed_at": "2026-01-27T10:30:00Z"
  }
}
```

#### Uninstall Add-on
```http
DELETE /api/addon/wave_patterns
```

Response:
```json
{
  "status": "success",
  "message": "Add-on removed completely",
  "removed": {
    "simulation_folder": true,
    "frames": 245,
    "videos": 3,
    "thumbnails": 3
  }
}
```

---

## File Structure After Implementation

```
loops/
├── backend/
│   ├── server.py               ← Main server (updated)
│   └── addon_manager.py        ← NEW: Add-on management service
│
├── frontend/
│   ├── index.html              ← Updated with Add-ons page
│   ├── css/
│   │   └── addons.css          ← NEW: Add-on page styles
│   └── js/
│       └── addons.js           ← NEW: Add-on management logic
│
├── shared/
│   ├── __init__.py
│   ├── base_simulation.py      ← Base class for all simulations
│   └── video_generator.py
│
├── simulations/
│   ├── __init__.py
│   └── sorting_visualizer/     ← Example simulation
│
├── output/
│   ├── frames/
│   │   └── {simulation_id}/    ← Frames organized by simulation
│   ├── videos/
│   │   └── {simulation_id}/    ← Videos organized by simulation
│   └── thumbnails/
│
├── uploads/                     ← NEW: Temporary upload storage
│   └── .gitkeep
│
├── docs/
│   ├── MODULAR_ADDON_ARCHITECTURE.md  ← This document
│   └── ADDON_DEVELOPMENT_GUIDE.md     ← Developer guide
│
└── addons.json                  ← NEW: Add-on registry
```

---

## Security Considerations

### Validation Checks

1. **Structure Validation**
   - Required files exist (`simulation.json`, `main.py`, `__init__.py`)
   - No path traversal in filenames
   - Maximum file size limits

2. **Code Safety**
   - Sandboxed execution environment (future)
   - No system calls outside allowed scope
   - Resource limits (CPU, memory)

3. **Dependency Management**
   - Whitelist of allowed packages
   - Version compatibility checks
   - Automatic dependency installation (optional)

```
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION PIPELINE                           │
│                                                                  │
│  .zip file                                                       │
│     │                                                            │
│     ▼                                                            │
│  ┌────────────────┐                                              │
│  │ Size Check     │ ──── Reject if > 50MB                       │
│  └────────────────┘                                              │
│     │                                                            │
│     ▼                                                            │
│  ┌────────────────┐                                              │
│  │ Structure      │ ──── Check required files                   │
│  │ Validation     │                                              │
│  └────────────────┘                                              │
│     │                                                            │
│     ▼                                                            │
│  ┌────────────────┐                                              │
│  │ Path Safety    │ ──── No ../ or absolute paths               │
│  └────────────────┘                                              │
│     │                                                            │
│     ▼                                                            │
│  ┌────────────────┐                                              │
│  │ JSON Schema    │ ──── Validate simulation.json               │
│  └────────────────┘                                              │
│     │                                                            │
│     ▼                                                            │
│  ┌────────────────┐                                              │
│  │ Dependency     │ ──── Check requirements.txt                 │
│  │ Check          │                                              │
│  └────────────────┘                                              │
│     │                                                            │
│     ▼                                                            │
│  ✓ Install                                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Benefits

| Benefit | Description |
|---------|-------------|
| **Scalability** | Add unlimited simulations without modifying core |
| **AI-Friendly** | Easy for AI to generate standardized add-on packages |
| **Isolation** | Each add-on is self-contained and removable |
| **Versioning** | Track add-on versions and updates |
| **Clean Removal** | Complete uninstall with no leftovers |
| **Distribution** | Share simulations as portable .zip files |

---

## Implementation Phases

### Phase 1: Core Infrastructure
- [ ] Create `addon_manager.py` service
- [ ] Add upload API endpoint
- [ ] Add uninstall API endpoint
- [ ] Create `addons.json` registry

### Phase 2: Dashboard Integration
- [ ] Add "Add-ons" page to dashboard
- [ ] Implement upload UI with drag-and-drop
- [ ] Add add-on cards with enable/disable/remove
- [ ] Show installation progress

### Phase 3: Enhanced Features
- [ ] Dependency auto-installation
- [ ] Add-on update mechanism
- [ ] Export add-on as .zip
- [ ] Add-on marketplace (future)

---

## Conclusion

The modular add-on architecture transforms the Loops Visualization System into a plugin-based platform where:

1. **Developers** can create simulations independently
2. **AI Agents** can generate and package simulations automatically  
3. **Users** can easily install, manage, and remove simulations
4. **The Core System** remains stable and minimal

This architecture enables scaling from a single simulation to hundreds without increasing complexity of the core system.
