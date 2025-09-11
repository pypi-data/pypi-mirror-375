"""Color family assignment utilities."""

from __future__ import annotations


def get_color_family(hue: float, saturation: float, value: float) -> str:
    """Assign a color family based on HSV, with handling of dark and muted tones."""
    if value < 0.2 and saturation < 0.2:
        return "Black"
    if value > 0.9 and saturation < 0.15:
        return "White / Off-white"
    if saturation < 0.15:
        return "Grey"
    hue_deg = hue * 360
    if 20 <= hue_deg < 50 and value < 0.6:
        return "Brown"
    if 50 <= hue_deg < 95 and saturation < 0.6 and value < 0.6:
        return "Green"
    if hue_deg < 15 or hue_deg >= 345:
        return "Red"
    elif hue_deg < 30:
        return "Pink"
    elif hue_deg < 45:
        return "Orange"
    elif hue_deg < 65:
        return "Yellow"
    elif hue_deg < 160:
        return "Green"
    elif hue_deg < 180:
        return "Turquoise / Teal"
    elif hue_deg < 240:
        return "Blue"
    elif hue_deg < 290:
        return "Purple / Violet"
    elif hue_deg < 345:
        return "Brown"
    return "Unknown"
