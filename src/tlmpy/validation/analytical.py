"""Analytical validation helpers."""

from __future__ import annotations

import numpy as np


def gaussian_diffusion_2d(grid, alpha: float, sigma0: float, t: float, center=None, mass: float = 1.0):
    sigma2 = sigma0**2 + 2.0 * alpha * t
    if center is None:
        center = ((grid.nx - 1) * grid.dx / 2.0, (grid.ny - 1) * grid.dy / 2.0)
    x = np.arange(grid.nx)[:, None] * grid.dx
    y = np.arange(grid.ny)[None, :] * grid.dy
    r2 = (x - center[0]) ** 2 + (y - center[1]) ** 2
    density = np.exp(-0.5 * r2 / sigma2)
    density *= mass / (density.sum() * grid.dx * grid.dy)
    return density


def estimate_wave_speed_from_probes(p1, p2, distance: float, dt: float) -> float:
    a = np.asarray(p1) - np.mean(p1)
    b = np.asarray(p2) - np.mean(p2)
    corr = np.correlate(b, a, mode="full")
    lag = int(np.argmax(corr) - (len(a) - 1))
    return distance / (lag * dt)

