"""Qt QColor helpers.

Note: This module requires a Qt binding (PySide6 or PyQt6) or a compatible
qt_core shim providing QColor to be importable at runtime.
"""

from __future__ import annotations

import importlib
from typing import Any


def _resolve_qcolor() -> Any:  # pragma: no cover
    # Try PySide6
    try:
        qtgui = importlib.import_module("PySide6.QtGui")
        qcolor = getattr(qtgui, "QColor", None)
        if qcolor is not None:
            return qcolor
    except ModuleNotFoundError:
        pass
    # Try PyQt6
    try:
        qtgui = importlib.import_module("PyQt6.QtGui")
        qcolor = getattr(qtgui, "QColor", None)
        if qcolor is not None:
            return qcolor
    except ModuleNotFoundError:
        pass
    # Try custom qt_core fallback
    try:
        qtcore = importlib.import_module("qt_core")
        qcolor = getattr(qtcore, "QColor", None)
        if qcolor is not None:
            return qcolor
    except ModuleNotFoundError:
        pass
    return None


def to_qcolor(color):
    """Convert various color formats to a QColor object.

    Accepts QColor instance, hex string, or RGB tuple of three integers (0-255).
    """
    QColor = _resolve_qcolor()  # pylint: disable=invalid-name
    if QColor is None:
        raise RuntimeError(
            "QColor is not available. Install PySide6 (pip install tintelligence-color-utils[qt_pyside6]) "
            "or PyQt6 (pip install tintelligence-color-utils[qt_pyqt6]), or provide qt_core.QColor."
        )
    if isinstance(color, QColor):
        return color
    if isinstance(color, str):
        return QColor(color)
    if isinstance(color, tuple) and len(color) == 3:
        return QColor(*color)
    raise ValueError("Unsupported color format for to_qcolor")
