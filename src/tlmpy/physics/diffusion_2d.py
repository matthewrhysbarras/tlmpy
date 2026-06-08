"""FTCS reference solver for 2D diffusion."""

from __future__ import annotations

import numpy as np

from tlmpy.array_backend import get_array_module, to_numpy
from tlmpy.core.grid import Grid2D
from tlmpy.core.results import SimulationResult


class Diffusion2D:
    """FTCS solver for ``du/dt = alpha laplacian(u)``.

    The von Neumann stability bound is checked in ``run``. ``dt == stable_dt`` is
    marginally stable; use a safety margin such as ``dt <= 0.9 * stable_dt``.
    """

    def __init__(self, grid: Grid2D, diffusivity: float, backend: str | None = "numpy", boundary: str = "neumann", boundary_value: float = 0.0):
        if diffusivity <= 0:
            raise ValueError("diffusivity must be positive")
        if boundary not in {"neumann", "dirichlet"}:
            raise ValueError("boundary must be 'neumann' or 'dirichlet'")
        self.grid = grid
        self.diffusivity = float(diffusivity)
        self.xp = get_array_module(backend)
        self.backend = backend
        self.boundary = boundary
        self.boundary_value = float(boundary_value)
        self.u = self.xp.zeros(grid.shape, dtype=self.xp.float64)

    def set_initial_condition(self, u0) -> None:
        arr = self.xp.asarray(u0, dtype=self.xp.float64)
        if arr.shape != self.grid.shape:
            raise ValueError("initial condition shape must match grid")
        self.u = arr.copy()

    def stable_dt(self) -> float:
        dx2 = self.grid.dx**2
        dy2 = self.grid.dy**2
        return dx2 * dy2 / (2.0 * self.diffusivity * (dx2 + dy2))

    def _laplacian(self):
        xp = self.xp
        if self.boundary == "neumann":
            p = xp.pad(self.u, 1, mode="edge")
        else:
            p = xp.pad(self.u, 1, mode="constant", constant_values=self.boundary_value)
        c = p[1:-1, 1:-1]
        return (p[2:, 1:-1] - 2 * c + p[:-2, 1:-1]) / self.grid.dx**2 + (
            p[1:-1, 2:] - 2 * c + p[1:-1, :-2]
        ) / self.grid.dy**2

    def run(self, steps: int, dt: float, store_final_field: bool = False) -> SimulationResult:
        stable = self.stable_dt()
        if dt > stable:
            raise ValueError(f"dt exceeds von Neumann stability bound {stable:g}")
        if steps < 0:
            raise ValueError("steps must be non-negative")
        for _ in range(steps):
            self.u = self.u + dt * self.diffusivity * self._laplacian()
            if self.boundary == "dirichlet":
                self.u[0, :] = self.boundary_value
                self.u[-1, :] = self.boundary_value
                self.u[:, 0] = self.boundary_value
                self.u[:, -1] = self.boundary_value
        return SimulationResult(
            probes={},
            time=np.arange(steps, dtype=float) * dt,
            dt=float(dt),
            metadata={"diffusivity": self.diffusivity, "boundary": self.boundary},
            final_field=to_numpy(self.u) if store_final_field else None,
        )

