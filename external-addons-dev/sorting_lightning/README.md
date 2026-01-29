# ⚡ Sorting Lightning

An advanced sorting visualization plugin featuring lightning effects, particle systems, smooth animations, and multiple visual themes.

## Features

### 🎨 Visual Effects
- **Lightning Bolts**: Electric arcs between swapping elements
- **Particle System**: Sparkles and particles during comparisons
- **Smooth Animations**: Interpolated movements, not instant jumps
- **Glow Effects**: Halos around active elements
- **Multiple Themes**: Neon, Fire, Ice, Cyberpunk, Rainbow

### 🧮 Algorithms
- Bubble Sort
- Quick Sort
- Merge Sort
- Insertion Sort
- Selection Sort

### 📊 Real-time Analytics
- Comparison count
- Swap count
- Elapsed time
- Visual theme indicator
- Effects status

### 🎮 Interactive Controls

**Keyboard Shortcuts:**
- `SPACE`: Pause/Resume
- `R`: Reset simulation
- `S`: Toggle recording
- `1-5`: Switch themes (1=Neon, 2=Fire, 3=Ice, 4=Cyberpunk, 5=Rainbow)
- `E`: Toggle effects on/off
- `ESC`: Exit

### 🎬 Recording & Video
- Frame-by-frame recording
- Video generation with quality settings
- Multiple FPS options (15-120)
- Quality presets: Low, Medium, High, Ultra, Lossless

## Installation

This plugin is part of the Loops visualization system. No additional dependencies required beyond pygame (included with Loops).

## Usage

### Via Control Panel (Recommended)
1. Launch the control panel from the Loops dashboard
2. Configure algorithm, visual theme, and settings
3. Click "LAUNCH VISUALIZATION"

### Standalone
```bash
python main.py --algorithm bubble --bars 100 --speed 5 --theme neon
```

**Arguments:**
- `--width WIDTH`: Window width (default: 1400)
- `--height HEIGHT`: Window height (default: 900)
- `--fps FPS`: Target FPS (default: 60)
- `--algorithm ALG`: Algorithm choice (bubble/quick/merge/insertion/selection)
- `--bars COUNT`: Number of bars (default: 100)
- `--speed SPEED`: Speed multiplier (default: 1)
- `--theme THEME`: Visual theme (neon/fire/ice/cyberpunk/rainbow)
- `--no-effects`: Disable particle/lightning effects
- `--record`: Start recording immediately

## Visual Themes

### 💜 Neon
Vibrant neon colors with purple/cyan/magenta palette. High-energy cyberpunk aesthetic.

### 🔥 Fire
Warm red, orange, and yellow gradient. Perfect for visualizing "hot" sorting action.

### ❄️ Ice
Cool blue palette with white highlights. Clean and elegant.

### 🌃 Cyberpunk
Pink, purple, and cyan neon. Retro-futuristic vibe.

### 🌈 Rainbow
Full spectrum rainbow gradient. Classic and colorful.

## Technical Details

### Architecture
- Inherits from `BaseSimulation` for standardized pygame integration
- Generator-based algorithm implementation for step-by-step visualization
- Particle and lightning systems for visual effects
- Smooth interpolation for bar movements

### Performance
- 60 FPS target (configurable)
- Speed multiplier: 1x-50x
- Supports 20-300 bars
- Effects can be disabled for better performance

### Frame Management
- Frames saved as `frame_XXXXXX.png`
- Sequential numbering for video generation
- Automatic folder creation

## Credits

Created as part of the Loops visualization system.

## License

MIT License
