"""Boundary reflection coefficients."""

from __future__ import annotations


def reflection_coefficient(boundary: str | float) -> float:
    """Return scalar link-line reflection coefficient Gamma.

    ``matched`` is first-order and exact only at normal incidence; real ABC/PML is roadmap.
    """
    if boundary == "reflective":
        return 1.0
    if boundary == "matched":
        return 0.0
    gamma = float(boundary)
    if not 0.0 <= gamma <= 1.0:
        raise ValueError("boundary reflection coefficient must be in [0, 1]")
    return gamma

