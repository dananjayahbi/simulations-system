# Testing the Add-on System

## Test Add-on: Sorting Circles ⭕

This document guides you through testing the newly implemented modular add-on architecture using the **Sorting Circles** add-on.

---

## 📦 Add-on Package

**Location**: `external-addons-dev/sorting_circles.zip`
**Size**: ~8.3 KB
**Type**: External Add-on (not built-in)

### Package Contents

```
sorting_circles/
├── simulation.json      ✓ Metadata (complete)
├── main.py              ✓ Main visualization
├── control_panel.py     ✓ GUI launcher
├── __init__.py          ✓ Package init
└── README.md            ✓ Documentation
```

---

## 🧪 Test Scenarios

### Test 1: Server Startup & Built-in Registration

**Purpose**: Verify existing simulations are auto-registered

**Steps**:
1. Start the server: `python launcher.py`
2. Check logs for "Found X simulation(s)"
3. Should see `sorting_visualizer` listed

**Expected Result**:
- ✅ Server starts without errors
- ✅ Built-in add-ons registered automatically
- ✅ `addons.json` created if missing

---

### Test 2: Dashboard Access

**Purpose**: Verify Add-ons page is accessible

**Steps**:
1. Open browser: `http://localhost:5000`
2. Click **Add-ons** in sidebar (🧩 icon)
3. Observe the add-ons page

**Expected Result**:
- ✅ Add-ons page loads
- ✅ Shows built-in sorting_visualizer
- ✅ Status badge shows "Built-in" and "Enabled"
- ✅ Upload and Scan buttons visible

---

### Test 3: Upload Add-on (Success Case)

**Purpose**: Test successful add-on installation

**Steps**:
1. Click **Upload Add-on** button
2. Modal appears with drop zone
3. Drag `sorting_circles.zip` or click to browse
4. File info shows: name and size
5. Click **Install** button
6. Progress bar animates
7. Wait for "Installation complete!"

**Expected Result**:
- ✅ Upload modal appears
- ✅ File is accepted (ZIP format check)
- ✅ Installation progresses visually
- ✅ Success notification shows
- ✅ Modal closes automatically
- ✅ Add-ons list refreshes
- ✅ New card for "Sorting Circles" appears
- ✅ Status shows "Enabled" (not built-in)

**Verify Backend**:
```bash
# Check if extracted
ls simulations/sorting_circles/

# Check if registered
cat addons.json | grep sorting_circles

# Check output directories created
ls output/frames/sorting_circles/
ls output/videos/sorting_circles/
```

---

### Test 4: Launch Add-on

**Purpose**: Test launching the installed add-on

**Steps**:
1. Find "Sorting Circles" card in grid
2. Click **🚀 Launch** button
3. New window should open with visualization

**Expected Result**:
- ✅ Launch notification appears
- ✅ New pygame window opens
- ✅ Circles arranged in radial pattern
- ✅ Visualization runs smoothly
- ✅ Controls work (SPACE, R, S, 1/2/3, arrows)

---

### Test 5: Enable/Disable

**Purpose**: Test toggling add-on state

**Steps**:
1. Find "Sorting Circles" card
2. Click **⏸️ Disable** button
3. Observe status change
4. Try to launch (should still work)
5. Click **▶️ Enable** button
6. Observe status change back

**Expected Result**:
- ✅ Status badge updates to "Disabled"
- ✅ Launch still works (disable ≠ uninstall)
- ✅ Re-enable works correctly
- ✅ Registry updates each time

---

### Test 6: Export Add-on

**Purpose**: Test exporting an add-on as ZIP

**Steps**:
1. Click **📥 Export** button on Sorting Circles
2. Browser downloads file

**Expected Result**:
- ✅ File downloads: `sorting_circles.zip`
- ✅ ZIP contains all original files
- ✅ Can be re-uploaded later

**Verify**:
```bash
# List contents
python -m zipfile -l sorting_circles.zip

# Should match original structure
```

---

### Test 7: Remove Add-on

**Purpose**: Test complete uninstallation

**Steps**:
1. Click **🗑️ Remove** button
2. Confirmation dialog appears
3. Read the warning about data deletion
4. Confirm removal
5. Wait for completion

**Expected Result**:
- ✅ Confirmation dialog shows
- ✅ Warning about frames/videos clear
- ✅ Removal notification appears
- ✅ Card disappears from grid
- ✅ Files deleted from `simulations/`
- ✅ Frames deleted from `output/frames/`
- ✅ Videos deleted from `output/videos/`
- ✅ Registry entry removed

**Verify Cleanup**:
```bash
# Should not exist
ls simulations/sorting_circles/           # Error: No such directory
ls output/frames/sorting_circles/         # Error: No such directory
ls output/videos/sorting_circles/         # Error: No such directory

# Should not be in registry
cat addons.json | grep sorting_circles    # No output
```

---

### Test 8: Built-in Protection

**Purpose**: Verify built-ins cannot be removed

**Steps**:
1. Find "Sorting Visualizer" card (built-in)
2. Look for Remove button

**Expected Result**:
- ✅ No "Remove" button visible
- ✅ Only "Launch" and "Export" available
- ✅ Disable button present (but not remove)

---

### Test 9: Scan Add-ons

**Purpose**: Test manual scanning for new add-ons

**Steps**:
1. Manually copy a simulation folder to `simulations/`
2. Click **🔍 Scan Add-ons** button
3. Wait for notification

**Expected Result**:
- ✅ Scan notification appears
- ✅ List refreshes
- ✅ New add-on appears (if valid)
- ✅ Registry updates

---

### Test 10: Upload Validation (Error Cases)

**Purpose**: Test validation and error handling

**Test Cases**:

#### A. Invalid File Type
- Upload: `.txt`, `.png`, or other non-ZIP
- **Expected**: Error "File must be a ZIP archive"

#### B. Invalid Structure
- Create ZIP missing `simulation.json`
- **Expected**: Error "Required file missing: simulation.json"

#### C. Invalid JSON
- Create ZIP with malformed `simulation.json`
- **Expected**: Error "Invalid JSON in simulation.json"

#### D. Duplicate ID
- Try uploading sorting_circles.zip again
- **Expected**: Error "Add-on 'sorting_circles' is already installed"

#### E. Large File (if implementing size check)
- Upload ZIP > 50MB
- **Expected**: Error "File too large"

---

### Test 11: Multiple Add-ons

**Purpose**: Test system with multiple add-ons

**Steps**:
1. Install Sorting Circles
2. Create another add-on (optional)
3. Install it too
4. Verify both show in grid
5. Test launching each
6. Verify no interference

**Expected Result**:
- ✅ Multiple add-ons coexist
- ✅ Each has own output directories
- ✅ No naming conflicts
- ✅ Independent enable/disable
- ✅ Can run simultaneously

---

### Test 12: Frame Recording

**Purpose**: Test frame saving integration

**Steps**:
1. Launch Sorting Circles
2. Press `S` to start recording
3. Let algorithm run
4. Press `S` to stop
5. Check frames directory

**Expected Result**:
- ✅ Frames saved to `output/frames/sorting_circles/`
- ✅ Sequential naming: `frame_000001.png`, etc.
- ✅ Can generate video from frames

---

### Test 13: Video Generation (if implemented)

**Purpose**: Test video generation from add-on frames

**Steps**:
1. Record frames from Sorting Circles
2. Use Loops video generator
3. Generate video
4. Check output

**Expected Result**:
- ✅ Video created in `output/videos/sorting_circles/`
- ✅ Thumbnail generated
- ✅ Playable in dashboard

---

### Test 14: API Endpoints

**Purpose**: Test REST API directly

**Using curl or similar**:

```bash
# List add-ons
curl http://localhost:5000/api/addon/list

# Get specific add-on
curl http://localhost:5000/api/addon/sorting_circles

# Upload (multipart form)
curl -X POST http://localhost:5000/api/addon/upload \
  -F "file=@sorting_circles.zip"

# Enable
curl -X POST http://localhost:5000/api/addon/sorting_circles/enable

# Disable
curl -X POST http://localhost:5000/api/addon/sorting_circles/disable

# Export (download)
curl http://localhost:5000/api/addon/sorting_circles/export \
  -o exported.zip

# Remove
curl -X DELETE http://localhost:5000/api/addon/sorting_circles
```

**Expected Result**:
- ✅ All endpoints return proper JSON
- ✅ Status codes correct (200, 400, 404, 500)
- ✅ Error messages clear
- ✅ Operations succeed

---

### Test 15: CLI Tools

**Purpose**: Test addon_manager.py CLI

```bash
cd backend

# List
python addon_manager.py list

# Install
python addon_manager.py install --zip-path ../external-addons-dev/sorting_circles.zip

# Enable/Disable
python addon_manager.py disable --addon-id sorting_circles
python addon_manager.py enable --addon-id sorting_circles

# Export
python addon_manager.py export --addon-id sorting_circles --output test_export.zip

# Uninstall
python addon_manager.py uninstall --addon-id sorting_circles

# Scan
python addon_manager.py scan
```

**Expected Result**:
- ✅ All commands work
- ✅ Output clear and informative
- ✅ Same behavior as dashboard

---

## 📊 Test Results Template

```markdown
## Test Session: [Date/Time]

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Server Startup | ✅ | |
| 2 | Dashboard Access | ✅ | |
| 3 | Upload Success | ✅ | |
| 4 | Launch Add-on | ✅ | |
| 5 | Enable/Disable | ✅ | |
| 6 | Export | ✅ | |
| 7 | Remove | ✅ | |
| 8 | Built-in Protection | ✅ | |
| 9 | Scan | ✅ | |
| 10 | Validation | ✅ | |
| 11 | Multiple Add-ons | ✅ | |
| 12 | Frame Recording | ✅ | |
| 13 | Video Generation | ✅ | |
| 14 | API Endpoints | ✅ | |
| 15 | CLI Tools | ✅ | |

**Overall**: ✅ PASS / ⚠️ PARTIAL / ❌ FAIL

**Issues Found**: [List any bugs or problems]

**Notes**: [Additional observations]
```

---

## 🐛 Known Limitations

- Maximum upload size: 50MB
- No automatic dependency installation yet
- No sandboxed execution (runs with full permissions)
- No version checking for updates

---

## 📝 Testing Checklist

Before considering testing complete, verify:

- [ ] All 15 test scenarios pass
- [ ] No errors in server logs
- [ ] No browser console errors
- [ ] Clean uninstallation works
- [ ] Multiple add-ons don't interfere
- [ ] Frame/video generation works
- [ ] API endpoints return proper responses
- [ ] CLI tools work correctly
- [ ] Documentation is accurate
- [ ] Built-in add-ons protected

---

## 🎯 Success Criteria

The add-on system is successful if:

1. ✅ Users can upload ZIP files via dashboard
2. ✅ Validation catches common errors
3. ✅ Installation is quick and visual
4. ✅ Add-ons run without core modification
5. ✅ Enable/disable works correctly
6. ✅ Export creates shareable packages
7. ✅ Removal is clean and complete
8. ✅ Built-ins are protected
9. ✅ Multiple add-ons coexist peacefully
10. ✅ API and CLI are functional

---

**Ready to test! 🚀**

Start with Test 1 and work through sequentially for best results.
