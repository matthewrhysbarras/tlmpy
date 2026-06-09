# Project Status

TLMpy is an experimental Python package for scalar 2D TLM-style wave simulation
and validation-oriented diffusion reference cases. The current public release is
v0.1.1.

## Current Capabilities

- Homogeneous 2D scalar TLM-style wave solver.
- Derived timestep from the 2D mesh relation `dt = dx / (wave_speed * sqrt(2))`.
- Reflective and first-order matched boundary handling.
- Approximate reflective obstacle masks.
- FTCS 2D diffusion reference solver.
- JSON-friendly benchmark result schema.
- NumPy backend by default and optional CuPy path where available.

## Examples And Benchmarks

Examples:

```bash
python examples/01_scalar_wave_pulse.py
python examples/02_scalar_wave_obstacle.py
python examples/03_thermal_diffusion_slab.py
python examples/04_gpu_benchmark.py
```

Benchmarks:

```bash
python benchmarks/analytical_travel_time.py
python benchmarks/boundary_reflection.py
python benchmarks/boundary_reflection_magnitude.py
python benchmarks/boundary_coefficient_sweep.py
python benchmarks/boundary_oblique_path.py
python benchmarks/boundary_corner_behaviour.py
python benchmarks/dispersion_characterisation.py
python benchmarks/dispersion_wavelength_sweep.py
python benchmarks/koay2008_gaussian_tlm_diffusion.py
```

Generated benchmark JSON under `outputs/` is local output and is not committed.

## Koay-Style Diffusion Case Study

The Koay 2008 Gaussian diffusion case study is experimental work. It compares
the Gaussian analytical diffusion solution with TLMpy's existing
finite-difference diffusion reference solver and a research-only parabolic
link-plus-stub pulse-state prototype under `tlmpy.experimental`. It includes
visible documentation figures and machine-readable benchmark metrics.

The estimator feedback is a practical implementation hypothesis based on the
paper's equations, not a complete root-locus reproduction. It should not be
treated as a validated implementation of the full paper.

For the current Gaussian benchmark parameters, the parabolic stub parameter is
`Ys = 0`; the equal-pulse parabolic mode is therefore expected to match the FTCS
reference update. The estimator-from-zero mode reports non-convergence against
the strict tolerance after 80 iterations, so this remains a partial
approximation.

## Experimental Or Planned Work

- Independent review of the passive scalar/parabolic TLM pulse equations.
- Stronger validation of the nodal state-estimator feedback.
- Stub-loaded heterogeneous 2D scalar TLM.
- Analytical dispersion comparison.
- Published reference benchmark comparison.
- Stronger publication-readiness evidence.

## Not Implemented

TLMpy does not currently implement:

- heterogeneous wave-speed media;
- PML;
- 3D electromagnetics;
- production acoustics, radar, clinical, medical or ultrasound capability;
- CAD import, GUI, MPI, JAX, Numba, Triton or required external solvers.

The matched boundary is a first-order link termination, not a full absorbing
boundary condition. Obstacle masks are approximate reflective geometry, not
material interfaces.

## Why Issue #34 Remains Open

Issue #34 asks for passive scalar stub-loaded node equations. It remains open
because the new experimental implementation needs independent review before it
should be considered resolved. The derivation note maps published link/stub
notation to TLMpy's array conventions, but stronger passivity and estimator
validation are still required.
