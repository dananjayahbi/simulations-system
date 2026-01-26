# colors.py - Color utilities for rainbow gradient visualization
import colorsys


def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB color values (0-255 range)."""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


def get_rainbow_color(value, max_value):
    """
    Get a rainbow color based on value position.
    Maps value to hue in HSV spectrum (0-1 range).
    """
    hue = value / max_value  # Normalize to 0-1
    saturation = 0.9
    brightness = 0.95
    return hsv_to_rgb(hue, saturation, brightness)


def generate_rainbow_colors(num_bars, max_height):
    """Generate a list of rainbow colors for the bars."""
    colors = []
    for i in range(num_bars):
        height = int((i + 1) / num_bars * max_height)
        color = get_rainbow_color(i, num_bars)
        colors.append(color)
    return colors
