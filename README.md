# TLMpy

Python-first toolkit for scalar Transmission Line Matrix style time-domain wave simulation, with a finite-difference diffusion reference solver for validation.

TLMpy v0.1 is experimental research software. APIs and numerical coverage are intentionally modest.

## Installation

```bash
pip install -e ".[dev]"
pip install -e ".[dev,viz]"
pip install -e ".[cuda,dev,viz]"
```

## Scalar Wave Quick Start

```python
import tlmpy as tlm
from tlmpy.core.sources import PointSource2D, RickerPulse
from tlmpy.physics import ScalarWaveTLM2D

grid = tlm.Grid2D((128, 128), (1e-3, 1e-3))
solver = ScalarWaveTLM2D(grid, wave_speed=1500.0, boundary="matched")
solver.add_source(PointSource2D((64, 64), RickerPulse(frequency=100_000.0)))
result = solver.run(steps=200, store_final_field=True)
```

## Diffusion Quick Start

```python
from tlmpy.physics import Diffusion2D

solver = Diffusion2D(grid, diffusivity=1e-5, boundary="neumann")
result = solver.run(steps=100, dt=0.9 * solver.stable_dt(), store_final_field=True)
```

Backends are thin: NumPy is core, CuPy is optional through `tlmpy[cuda]`.

The scalar wave solver stores four directional port arrays named `n`, `s`, `e`, and `w`, each with shape `(nx, ny)`. Source and probe locations use integer grid indices `(i, j)`, where `i` is the first array axis and `j` is the second. A point source is evaluated as `signal.value(step * dt)` and split equally into the four ports. The scalar field used for probes and plots is `0.5 * (n + s + e + w)`.

Limitations: the 2D TLM mesh speed is fixed by `c = dx / (dt * sqrt(2))`; `dt` is computed from `wave_speed`, not supplied. Matched boundaries are first-order link terminations, not PML or full absorbing boundary conditions. Obstacles are approximate reflective geometry masks only, not refractive materials or resolved interfaces. There is no heterogeneous medium and no PML in v0.1.

Validation emphasizes exact `dt`, port-energy conservation, non-periodic boundaries, propagation-based mesh-speed regression, Gaussian diffusion, Neumann mass conservation, result round trips, and CLI behavior.

## Benchmark Infrastructure

TLMpy includes a lightweight JSON-friendly benchmark result schema in `tlmpy.benchmarking` to support reproducible validation work. Current benchmark scripts cover homogeneous travel time and a source-free boundary behavior case. External solver comparisons remain planned future work.

An experimental Koay 2008 Gaussian diffusion case-study benchmark compares the
analytical Gaussian solution with the existing finite-difference diffusion
reference solver and a research-only parabolic link-plus-stub pulse-state
prototype under `tlmpy.experimental`. The estimator feedback is not yet a full
paper reproduction and remains experimental; the current Gaussian benchmark
also records that the strict estimator convergence flag remains false.

## Examples

Examples live in `examples/`, with a reproducible command gallery in
`docs/example_gallery.md`. They cover current homogeneous scalar wave behavior,
approximate reflective obstacle masks, the finite-difference diffusion reference
solver and optional backend timing.

Roadmap highlights include stub-loaded heterogeneous nodes, dispersion and boundary characterization, and reproducible sensing demos.

Please cite TLMpy using `CITATION.cff`. License: BSD-3-Clause.

Current capabilities and limitations are summarized in
`docs/project_status.md`.
