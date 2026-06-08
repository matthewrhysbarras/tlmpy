"""Reflective geometry masks."""

from __future__ import annotations

import numpy as np

from tlmpy.core.grid import Grid2D


class ObstacleMask:
    """Boolean mask of approximate reflective obstacle cells.

    The mask is geometric only. It does not carry material properties, refractive
    index, or wave speed, and it is not a resolved interface model.
    """

    def __init__(self, grid: Grid2D):
        self.grid = grid
        self.mask = np.zeros(grid.shape, dtype=bool)

    def add_circle(self, center: tuple[float, float], radius: float):
        x = np.arange(self.grid.nx)[:, None] * self.grid.dx
        y = np.arange(self.grid.ny)[None, :] * self.grid.dy
        self.mask |= (x - center[0]) ** 2 + (y - center[1]) ** 2 <= radius**2
        return self
