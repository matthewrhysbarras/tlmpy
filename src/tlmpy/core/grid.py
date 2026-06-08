"""Grid definitions."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Grid2D:
    """Uniform two-dimensional grid."""

    shape: tuple[int, int]
    spacing: tuple[float, float]

    def __post_init__(self) -> None:
        if len(self.shape) != 2 or any(not isinstance(v, int) or v <= 0 for v in self.shape):
            raise ValueError("shape must contain two positive integers")
        if len(self.spacing) != 2 or any(float(v) <= 0 for v in self.spacing):
            raise ValueError("spacing must contain two positive floats")
        object.__setattr__(self, "spacing", (float(self.spacing[0]), float(self.spacing[1])))

    @property
    def nx(self) -> int:
        return self.shape[0]

    @property
    def ny(self) -> int:
        return self.shape[1]

    @property
    def dx(self) -> float:
        return self.spacing[0]

    @property
    def dy(self) -> float:
        return self.spacing[1]

    @property
    def extent(self) -> tuple[float, float]:
        return (self.nx * self.dx, self.ny * self.dy)

    @property
    def x(self) -> np.ndarray:
        return np.arange(self.nx, dtype=float) * self.dx

    @property
    def y(self) -> np.ndarray:
        return np.arange(self.ny, dtype=float) * self.dy

