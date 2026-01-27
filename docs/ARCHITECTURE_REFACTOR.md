# Loops Visualization System - Architecture Refactoring

## 🎉 What's New

The Loops Visualization System has been refactored to support a **modular add-on architecture**, making it easy to:

- 📦 **Package simulations** as standalone ZIP files
- 🚀 **Upload and install** add-ons via the dashboard
- 🔌 **Enable/disable** simulations without removal
- 🗑️ **Uninstall cleanly** with no leftover files
- 📥 **Export simulations** for sharing
- 🤖 **AI-friendly** structure for automated generation

---

## 📁 New Project Structure

```
loops/
├── backend/
│   ├── server.py              ← Updated with add-on API endpoints
│   └── addon_manager.py       ← NEW: Add-on management service
│
├── frontend/
│   ├── index.html             ← Updated with Add-ons page
│   ├── css/
│   │   └── addons.css         ← NEW: Add-on page styles
│   └── js/
│       └── addons.js          ← NEW: Add-on management logic
│
├── shared/
│   ├── base_simulation.py     ← Base class for all simulations
│   └── video_generator.py     ← Video generation utilities
│
├── simulations/
│   ├── __init__.py
│   └── sorting_visualizer/    ← Example simulation (built-in)
│       ├── simulation.json    ← Updated with full metadata
│       ├── main.py
│       ├── control_panel.py
│       └── ...
│
├── output/
│   ├── frames/
│   │   └── {simulation_id}/   ← Organized by simulation
│   ├── videos/
│   │   └── {simulation_id}/   ← Organized by simulation
│   └── thumbnails/
│
├── uploads/                    ← NEW: Temporary upload storage
│   └── .gitkeep
│
├── docs/
│   ├── MODULAR_ADDON_ARCHITECTURE.md
│   ├── ADDON_DEVELOPMENT_GUIDE.md
│   ├── ARCHITECTURE_REFACTOR.md       ← This file
│   └── simulation.json.template       ← NEW: Template for new add-ons
│
└── addons.json                         ← NEW: Add-on registry
```

---

## 🔧 What Was Added

### 1. Backend Components

#### `backend/addon_manager.py`
- Complete add-on lifecycle management
- ZIP file validation and extraction
- Security checks (path traversal, file size)
- Registry management
- Automatic scanning of built-in add-ons

#### New API Endpoints
- `GET /api/addon/list` - List all add-ons
- `POST /api/addon/upload` - Upload and install add-on
- `GET /api/addon/<id>` - Get add-on details
- `DELETE /api/addon/<id>` - Uninstall add-on
- `POST /api/addon/<id>/enable` - Enable add-on
- `POST /api/addon/<id>/disable` - Disable add-on
- `GET /api/addon/<id>/export` - Export as ZIP

### 2. Frontend Components

#### Add-ons Dashboard Page
- Visual grid of installed add-ons
- Status indicators (enabled/disabled/built-in)
- Action buttons (launch, enable, disable, export, remove)
- File upload with drag-and-drop
- Progress tracking for installations

#### Navigation
- New "Add-ons" menu item in sidebar
- Icon: 🧩 (puzzle piece)
- Located between "Outputs" and "Settings"

### 3. Configuration Files

#### `addons.json`
```json
{
  "version": "1.0.0",
  "addons": {
    "sorting_visualizer": {
      "id": "sorting_visualizer",
      "name": "Sorting Visualizer",
      "version": "1.0.0",
      "enabled": true,
      "builtin": true,
      ...
    }
  },
  "last_updated": "2026-01-27T..."
}
```

#### Enhanced `simulation.json`
All simulations now include comprehensive metadata:
```json
{
  "id": "unique_id",
  "name": "Display Name",
  "description": "What it does",
  "icon": "🎮",
  "color": "#6366f1",
  "version": "1.0.0",
  "author": "Author Name",
  "license": "MIT",
  "tags": ["tag1", "tag2"],
  "requires_pygame": true,
  "entry_point": "main.py",
  "control_panel": "control_panel.py"
}
```

---

## 🚀 How to Use

### For Users

#### Installing an Add-on
1. Navigate to **Add-ons** page
2. Click **Upload Add-on**
3. Drop or select a `.zip` file
4. Click **Install**
5. Wait for validation and installation
6. Launch from the add-ons grid!

#### Managing Add-ons
- **Enable/Disable**: Toggle without removing files
- **Launch**: Start the simulation
- **Export**: Download as ZIP for sharing
- **Remove**: Uninstall completely (built-ins protected)

### For Developers

#### Creating an Add-on

**Minimum structure:**
```
my_simulation/
├── simulation.json    ← Required metadata
├── main.py            ← Entry point
└── __init__.py        ← Package init
```

**Package as ZIP:**
```bash
zip -r my_simulation.zip my_simulation/
```

**Upload via dashboard or API:**
```bash
curl -X POST http://localhost:5000/api/addon/upload \
  -F "file=@my_simulation.zip"
```

#### Using the CLI

```bash
# List all add-ons
python backend/addon_manager.py list

# Install from ZIP
python backend/addon_manager.py install --zip-path my_addon.zip

# Uninstall
python backend/addon_manager.py uninstall --addon-id my_simulation

# Enable/disable
python backend/addon_manager.py enable --addon-id my_simulation
python backend/addon_manager.py disable --addon-id my_simulation

# Export
python backend/addon_manager.py export --addon-id my_simulation --output export.zip

# Scan and register built-ins
python backend/addon_manager.py scan
```

---

## 🔒 Security Features

### Validation Pipeline

1. **File Size Check**: Reject files > 50MB
2. **Structure Validation**: Verify required files exist
3. **Path Safety**: Block path traversal (`../`, absolute paths)
4. **JSON Schema**: Validate `simulation.json` format
5. **Dependency Check**: Verify requirements (future)

### Protected Actions

- Built-in add-ons cannot be uninstalled
- Confirmation required for removals
- Complete cleanup on uninstall (frames, videos, files)

---

## 📊 Features Comparison

| Feature | Before | After |
|---------|--------|-------|
| Add simulation | Manual file copy | Upload ZIP via dashboard |
| Remove simulation | Manual deletion, leftover files | Clean uninstall with confirmation |
| Share simulation | Share raw files | Export as portable ZIP |
| Manage simulations | File system only | Visual dashboard + CLI |
| Enable/disable | Delete or rename | Toggle without removal |
| Metadata | Scattered or missing | Standardized `simulation.json` |
| AI generation | Complex file structure | Simple template-based |

---

## 🎯 Benefits

### Scalability
- Add unlimited simulations without modifying core code
- Each add-on is isolated and self-contained
- No naming conflicts or interference

### Developer Experience
- Clear structure with templates
- Comprehensive documentation
- CLI and GUI tools
- Easy testing and distribution

### AI-Friendly
- Standardized package format
- Simple file structure
- Template-based generation
- Automated validation

### User Experience
- Visual add-on management
- Drag-and-drop installation
- Status indicators
- Safe removal process

---

## 🔄 Migration Guide

### Existing Simulations

All existing simulations in the `simulations/` folder are automatically:

1. ✅ Scanned on server startup
2. ✅ Registered as "built-in" add-ons
3. ✅ Protected from accidental removal
4. ✅ Displayed in the add-ons dashboard

**No action required!** They work as before.

### Enhancing Existing Simulations

To take full advantage of the new system:

1. Add/update `simulation.json` with complete metadata
2. Follow the template in `docs/simulation.json.template`
3. Restart the server to refresh the registry

---

## 📚 Documentation

- **Architecture**: `docs/MODULAR_ADDON_ARCHITECTURE.md`
- **Development Guide**: `docs/ADDON_DEVELOPMENT_GUIDE.md`
- **This Document**: `docs/ARCHITECTURE_REFACTOR.md`
- **Template**: `docs/simulation.json.template`

---

## 🔮 Future Enhancements

### Phase 2: Enhanced Features
- [ ] Automatic dependency installation
- [ ] Add-on update mechanism
- [ ] Version compatibility checks
- [ ] Sandboxed execution

### Phase 3: Marketplace (Future)
- [ ] Public add-on repository
- [ ] Browse and install from catalog
- [ ] Rating and review system
- [ ] Automatic updates

---

## ✅ Testing the Refactored System

### 1. Start the Server
```bash
python launcher.py
```

### 2. Open Dashboard
Navigate to: `http://localhost:5000`

### 3. Check Add-ons Page
- Click "Add-ons" in the sidebar
- Verify built-in simulations are listed
- Check status indicators

### 4. Test Upload
- Click "Upload Add-on"
- Try uploading a ZIP (or use export first)
- Verify installation process

### 5. Test Management
- Enable/disable an add-on
- Launch a simulation
- Export an add-on
- Try removing (will be blocked for built-ins)

---

## 🐛 Troubleshooting

### Add-ons not showing
- Check `addons.json` was created
- Verify `simulation.json` exists in each simulation
- Click "Scan Add-ons" to refresh

### Upload fails
- Ensure file is a valid ZIP
- Check file size < 50MB
- Verify ZIP contains required files
- Check server logs for details

### Installation errors
- Verify `simulation.json` format
- Check for path traversal attempts
- Ensure add-on ID matches folder name
- Review validation errors in response

---

## 💡 Tips

### For Add-on Creators
- Use the template: `docs/simulation.json.template`
- Follow the guide: `docs/ADDON_DEVELOPMENT_GUIDE.md`
- Test locally before packaging
- Include descriptive metadata
- Add tags for discoverability

### For System Administrators
- Regular backups of `addons.json`
- Monitor `uploads/` directory size
- Check logs for validation errors
- Use CLI tools for automation

---

## 🎊 Summary

The Loops Visualization System has been successfully refactored to support:

✅ Modular add-on architecture
✅ Visual dashboard management
✅ ZIP-based distribution
✅ Clean installation/removal
✅ Built-in protection
✅ Export/import functionality
✅ CLI management tools
✅ Comprehensive documentation

**The system is now scalable, maintainable, and AI-friendly!**

---

*Last Updated: 2026-01-27*
*Refactored by: AI Assistant*
*Documentation: Complete*
