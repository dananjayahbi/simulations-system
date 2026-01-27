# ⭕ Sorting Circles

Beautiful circular visualization of sorting algorithms using radial patterns.

## Overview

Sorting Circles presents a unique approach to visualizing sorting algorithms by arranging values as circles in a radial pattern around the center. Each circle's size represents its value, creating a mesmerizing visual experience as the algorithms organize them.

## Features

- **Radial Layout**: 50 circles arranged in a perfect circle
- **Size-based Visualization**: Larger values = larger circles
- **Beautiful Gradients**: Full HSV color spectrum
- **Three Algorithms**: Bubble Sort, Quick Sort, Merge Sort
- **Visual Feedback**: 
  - White outline = comparing
  - Yellow outline = swapping
- **Speed Control**: Adjustable from 1-60 ops/second
- **Frame Recording**: Save frames for video generation

## Controls

| Key | Action |
|-----|--------|
| `SPACE` | Toggle play/pause |
| `R` | Reset and shuffle |
| `S` | Start/stop recording frames |
| `1` | Switch to Bubble Sort |
| `2` | Switch to Quick Sort |
| `3` | Switch to Merge Sort |
| `↑` | Increase speed |
| `↓` | Decrease speed |
| `ESC` | Exit |

## Installation

### Via Loops Dashboard
1. Package this folder as `sorting_circles.zip`
2. Open Loops Dashboard
3. Navigate to **Add-ons** page
4. Click **Upload Add-on**
5. Select the ZIP file
6. Click **Install**

### Manual Installation
1. Copy `sorting_circles/` to `loops/simulations/`
2. Restart the Loops server
3. The add-on will be auto-detected

## Usage

### Control Panel
```bash
python control_panel.py
```

Configure settings:
- Window size
- Frame rate
- Number of circles
- Default algorithm
- Auto-record option

Then click **Launch Visualization**

### Direct Launch
```bash
python main.py
```

With custom parameters:
```bash
python main.py --width 1000 --height 1000 --fps 60 --array-size 50 --algorithm bubble
```

## Algorithms

### Bubble Sort
- **Complexity**: O(n²)
- **Method**: Repeatedly swap adjacent elements
- **Visual**: Watch bubbles slowly rise to their positions

### Quick Sort
- **Complexity**: O(n log n) average
- **Method**: Partition around pivot
- **Visual**: Dramatic rearrangements

### Merge Sort
- **Complexity**: O(n log n)
- **Method**: Divide and conquer
- **Visual**: Smooth merging patterns

## Customization

Edit parameters in `main.py`:

```python
self.num_elements = 50      # Number of circles
self.speed = 10              # Operations per second
self.circle_padding = 20     # Space between circles
```

## Recording Videos

1. Press `S` to start recording
2. Run the algorithm
3. Press `S` again to stop
4. Frames saved to `frames/` directory
5. Use video generator to create MP4

## Technical Details

- **Engine**: pygame-ce
- **Resolution**: 1000×1000 (default)
- **FPS**: 60 (default)
- **Colors**: HSV gradient mapping
- **Layout**: Polar coordinates for circular arrangement

## Requirements

- Python 3.8+
- pygame-ce
- Loops System v1.0.0+

## License

MIT License - See LICENSE file

## Author

Loops Community

## Version

1.0.0

---

**Enjoy the mesmerizing dance of sorting algorithms! 🎨**
