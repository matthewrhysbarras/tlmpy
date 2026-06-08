"""Thin NumPy/CuPy backend helpers."""

from __future__ import annotations

import numpy as np


def get_array_module(name: str | None = None):
    """Return numpy or cupy. ``None`` selects NumPy."""
    if name is None or name == "numpy":
        return np
    if name == "cupy":
        try:
            import cupy as cp
        except ImportError as exc:
            raise ImportError(
                "CuPy backend requested but CuPy is not installed. Install tlmpy[cuda]."
            ) from exc
        return cp
    raise ValueError("backend must be one of None, 'numpy', or 'cupy'")


def to_numpy(a):
    """Return ``a`` as a NumPy host array."""
    if hasattr(a, "get"):
        return a.get()
    return np.asarray(a)

