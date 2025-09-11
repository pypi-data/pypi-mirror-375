"""Utilities for sorting paint dictionaries by color properties or family."""

from __future__ import annotations

from typing import Dict, List

from .conversion import hex_to_hsv
from .family import get_color_family


def sort_paints_by_color(paints: List[Dict], mode: str = "hue") -> List[Dict]:
    """Sort a list of paint dictionaries by color property (hue, saturation, or value)."""
    if mode not in {"hue", "saturation", "value"}:
        raise ValueError("mode must be 'hue', 'saturation', or 'value'")

    def get_sort_key(paint: Dict):
        h, s, v = hex_to_hsv(paint["color_primary"])
        return {"hue": h, "saturation": s, "value": v}[mode]

    return sorted(paints, key=get_sort_key)


def sort_paints_by_family_value_hue(paints: List[Dict]) -> List[Dict]:
    """Hybrid sort: group by color family, sort each by value (desc), then hue (asc)."""
    enriched_paints = []
    for paint in paints:
        hex_code = paint.get("color_primary")
        h, s, v = hex_to_hsv(hex_code)
        family = get_color_family(h, s, v)
        enriched_paints.append({**paint, "_hsv": (h, s, v), "_family": family})
    family_order = [
        "Black",
        "Grey",
        "White / Off-white",
        "Red",
        "Pink",
        "Orange",
        "Yellow",
        "Green",
        "Turquoise / Teal",
        "Blue",
        "Purple / Violet",
        "Brown",
        "Unknown",
    ]
    sorted_paints = sorted(
        enriched_paints,
        key=lambda p: (
            (
                family_order.index(p["_family"]) if p["_family"] in family_order else len(family_order)
            ),
            -p["_hsv"][2],
            p["_hsv"][0],
        ),
    )
    return sorted_paints
