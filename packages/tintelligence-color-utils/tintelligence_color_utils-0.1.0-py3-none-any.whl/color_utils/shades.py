"""Shade and tone utilities."""

from __future__ import annotations

import colorsys

from .conversion import hex_to_hsv


def get_darker_shades(hex_code: str, steps: int = 2, factor: float = 0.8):
    """Return a tuple of darker hex codes derived from input hex_code."""
    h, s, v = hex_to_hsv(hex_code)
    shades = []
    for _ in range(steps):
        v = max(0, v * factor)
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        hex_shade = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
        shades.append(hex_shade)
    return tuple(shades)
