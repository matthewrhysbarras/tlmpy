"""Homogeneous 2D scalar TLM-style solver."""

from __future__ import annotations

from math import sqrt

import numpy as np

from tlmpy.array_backend import get_array_module, to_numpy
from tlmpy.core.boundaries import reflection_coefficient
from tlmpy.core.grid import Grid2D
from tlmpy.core.results import SimulationResult


class ScalarWaveTLM2D:
    """Four-port homogeneous matched-mesh scalar wave solver.

    The mesh speed is fixed by ``c = dx / (dt * sqrt(2))``. This solver accepts a
    single homogeneous ``wave_speed`` and computes ``dt`` internally; it does not
    model heterogeneous media.
    """

    def __init__(self, grid: Grid2D, wave_speed: float = 1500.0, backend: str | None = "numpy", boundary="matched", obstacles=None):
        if grid.dx != grid.dy:
            raise ValueError("ScalarWaveTLM2D requires dx == dy; anisotropic support is roadmap")
        if wave_speed <= 0:
            raise ValueError("wave_speed must be positive")
        self.grid = grid
        self.wave_speed = float(wave_speed)
        self.dt = grid.dx / (self.wave_speed * sqrt(2))
        self.xp = get_array_module(backend)
        self.backend = backend
        self.gamma = reflection_coefficient(boundary)
        self.boundary = boundary
        self.obstacles = None if obstacles is None else self.xp.asarray(obstacles.mask, dtype=bool)
        self.n = self.xp.zeros(grid.shape, dtype=self.xp.float64)
        self.s = self.xp.zeros(grid.shape, dtype=self.xp.float64)
        self.e = self.xp.zeros(grid.shape, dtype=self.xp.float64)
        self.w = self.xp.zeros(grid.shape, dtype=self.xp.float64)
        self.sources = []
        self.probes = []

    def add_source(self, source):
        self._validate_location(source.location)
        self.sources.append(source)

    def add_probe(self, probe):
        self._validate_location(probe.location)
        self.probes.append(probe)

    def _validate_location(self, loc) -> None:
        i, j = loc
        if not (0 <= i < self.grid.nx and 0 <= j < self.grid.ny):
            raise ValueError("location must be inside grid")

    def field(self):
        return 0.5 * (self.n + self.s + self.e + self.w)

    def step(self, step_index: int | None = None) -> None:
        total = self.n + self.s + self.e + self.w
        on = 0.5 * total - self.n
        os = 0.5 * total - self.s
        oe = 0.5 * total - self.e
        ow = 0.5 * total - self.w

        if self.obstacles is not None:
            on, os, oe, ow = (
                self.xp.where(self.obstacles, self.s, on),
                self.xp.where(self.obstacles, self.n, os),
                self.xp.where(self.obstacles, self.w, oe),
                self.xp.where(self.obstacles, self.e, ow),
            )

        nn = self.xp.empty_like(self.n)
        ns = self.xp.empty_like(self.s)
        ne = self.xp.empty_like(self.e)
        nw = self.xp.empty_like(self.w)

        nn[1:, :] = os[:-1, :]
        nn[0, :] = self.gamma * on[0, :]
        ns[:-1, :] = on[1:, :]
        ns[-1, :] = self.gamma * os[-1, :]
        ne[:, :-1] = ow[:, 1:]
        ne[:, -1] = self.gamma * oe[:, -1]
        nw[:, 1:] = oe[:, :-1]
        nw[:, 0] = self.gamma * ow[:, 0]

        self.n, self.s, self.e, self.w = nn, ns, ne, nw

        if step_index is not None:
            t = step_index * self.dt
            for source in self.sources:
                i, j = source.location
                value = self.xp.float64(source.signal.value(t) / 4.0)
                self.n[i, j] += value
                self.s[i, j] += value
                self.e[i, j] += value
                self.w[i, j] += value

    def run(self, steps: int, store_final_field: bool = False) -> SimulationResult:
        if steps < 0:
            raise ValueError("steps must be non-negative")
        for probe in self.probes:
            probe.values.clear()
        time = np.arange(steps, dtype=float) * self.dt
        for k in range(steps):
            self.step(k)
            f = self.field()
            for probe in self.probes:
                i, j = probe.location
                probe.record(float(to_numpy(f[i, j])))
        return SimulationResult(
            probes={p.name: np.asarray(p.values, dtype=float) for p in self.probes},
            time=time,
            dt=self.dt,
            metadata={"wave_speed": self.wave_speed, "boundary": str(self.boundary)},
            final_field=to_numpy(self.field()) if store_final_field else None,
        )
