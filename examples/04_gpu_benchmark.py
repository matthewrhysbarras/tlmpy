"""Time NumPy versus CuPy if CuPy is available."""

from __future__ import annotations

import time

from tlmpy import Grid2D
from tlmpy.physics import ScalarWaveTLM2D


def run(backend):
    grid = Grid2D((192, 192), (1e-3, 1e-3))
    solver = ScalarWaveTLM2D(grid, wave_speed=1500.0, backend=backend, boundary="matched")
    t0 = time.perf_counter()
    solver.run(100)
    return time.perf_counter() - t0


print(f"backend=numpy grid=192x192 steps=100 elapsed={run('numpy'):.4f}s")
try:
    import cupy  # noqa: F401
except ImportError:
    print("backend=cupy skipped: CuPy is not installed. Install tlmpy[cuda].")
else:
    print(f"backend=cupy grid=192x192 steps=100 elapsed={run('cupy'):.4f}s")

