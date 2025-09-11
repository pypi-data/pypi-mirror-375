"""Color space conversion utilities."""

from __future__ import annotations

import colorsys
import math
from typing import Optional, Tuple


def hex_to_rgb(hex_code: str) -> Tuple[float, float, float]:
    """Convert #RRGGBB or RRGGBB to RGB tuple in [0,1].

    Raises ValueError on invalid input.
    """
    s = hex_code.lstrip("#").strip()
    if len(s) != 6:
        raise ValueError(f"Invalid hex color: {hex_code}")
    try:
        return tuple(int(s[i : i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError as exc:
        raise ValueError(f"Invalid hex color: {hex_code}") from exc


def hex_to_hsv(hex_code: str) -> Tuple[float, float, float]:
    """Convert a hex color code to HSV tuple (h, s, v), with h in [0, 1]."""
    rgb = hex_to_rgb(hex_code)
    return colorsys.rgb_to_hsv(*rgb)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert integer RGB (0-255) to #RRGGBB."""
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    return f"#{r:02X}{g:02X}{b:02X}"


def hex_midpoint(c1: Optional[str], c2: Optional[str]) -> Optional[str]:
    """Midpoint of two hex colors as #RRGGBB. Returns None if invalid input."""
    if not c1 or not c2:
        return None
    try:
        r1, g1, b1 = (int(x * 255) for x in hex_to_rgb(c1))
        r2, g2, b2 = (int(x * 255) for x in hex_to_rgb(c2))
    except ValueError:
        return None
    r = (r1 + r2) // 2
    g = (g1 + g2) // 2
    b = (b1 + b2) // 2
    return rgb_to_hex(r, g, b)


def rgb_to_lab(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Approximate sRGB (D65) integer RGB (0-255) to CIE L*a*b* (L in 0..100)."""
    rs = r / 255.0
    gs = g / 255.0
    bs = b / 255.0

    def inv_gamma(u: float) -> float:
        return ((u + 0.055) / 1.055) ** 2.4 if u > 0.04045 else (u / 12.92)

    rl = inv_gamma(rs)
    gl = inv_gamma(gs)
    bl = inv_gamma(bs)

    x = rl * 0.4124564 + gl * 0.3575761 + bl * 0.1804375
    y = rl * 0.2126729 + gl * 0.7151522 + bl * 0.0721750
    z = rl * 0.0193339 + gl * 0.1191920 + bl * 0.9503041

    xn = 0.95047
    yn = 1.00000
    zn = 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else (7.787 * t + 16 / 116)

    fx = f(x / xn)
    fy = f(y / yn)
    fz = f(z / zn)

    l = 116 * fy - 16
    # clamp to valid L range to avoid tiny floating point drift
    l = min(100.0, max(0.0, l))
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    return l, a, b


def normalize_lab(
    l_value: Optional[float], a_value: Optional[float], b_value: Optional[float]
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Normalize Lab to 0..1 each. L in 0..100 -> /100; a,b in ~[-128,127] -> (v+128)/255."""

    def norm_l(v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        # if already normalized, keep within [0,1]; else divide by 100 and cap
        vv = v if v <= 1.0 else v / 100.0
        return min(1.0, max(0.0, vv))

    def norm_ab(v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        if 0.0 <= v <= 1.0:
            return v
        return (v + 128.0) / 255.0

    return norm_l(l_value), norm_ab(a_value), norm_ab(b_value)


def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[int, int, int]:
    """Convert RGB (0-255) to HSL where H in 0..360, S,L in 0..100 (ints)."""
    rs, gs, bs = r / 255.0, g / 255.0, b / 255.0
    cmax, cmin = max(rs, gs, bs), min(rs, gs, bs)
    delta = cmax - cmin
    if delta == 0:
        h = 0
    elif cmax == rs:
        h = 60 * (((gs - bs) / delta) % 6)
    elif cmax == gs:
        h = 60 * (((bs - rs) / delta) + 2)
    else:
        h = 60 * (((rs - gs) / delta) + 4)
    l = (cmax - cmin) / 2 + cmin
    if delta == 0:
        s = 0
    else:
        s = delta / (1 - abs(2 * l - 1))
    return int(round(h) % 360), int(round(s * 100)), int(round(l * 100))


def lab_to_lch(
    l_value: float, a_value: float, b_value: float
) -> Tuple[float, float, float]:
    """Convert CIE Lab to LCH(ab). Returns (L, C, H_deg)."""
    c = math.sqrt((a_value or 0.0) ** 2 + (b_value or 0.0) ** 2)
    h_rad = math.atan2((b_value or 0.0), (a_value or 0.0))
    h_deg = math.degrees(h_rad)
    if h_deg < 0:
        h_deg += 360.0
    return float(l_value or 0.0), float(c), float(h_deg)


def brightness_from_hex(hex_color: str) -> Optional[float]:
    """Perceived brightness (Lab L) from a hex color. Higher means brighter."""
    try:
        r, g, b = (int(x * 255) for x in hex_to_rgb(hex_color))
    except ValueError:
        return None
    l_value, _a, _b = rgb_to_lab(r, g, b)
    return l_value
