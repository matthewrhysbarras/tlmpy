# TLMpy v0.1.1

Patch release focused on validation and documentation hardening after the initial v0.1.0 public seed.

## Changed

- Strengthened propagation-based wave-speed validation.
- Strengthened non-periodic boundary regression.
- Added obstacle-mask validation tests.
- Added `SimulationResult` save/load round-trip tests.
- Added CLI tests.
- Improved documentation of port conventions, integer grid indices, source injection, matched-boundary limitations and obstacle-mask approximation.

## Validation

Release checks:

- `ruff check .`
- `pytest`
- `python -m tlmpy --version`
- `python -m tlmpy info`
- `python examples/01_scalar_wave_pulse.py`
- `python examples/03_thermal_diffusion_slab.py`
- `python examples/04_gpu_benchmark.py`

## Known limitations

- No heterogeneous wave-speed media.
- No stub-loaded TLM nodes.
- No PML.
- No 3D EM.
- No anisotropic wave mesh.
- Matched boundary remains first-order and is not a full absorbing boundary condition.
- Obstacle masks remain approximate reflective geometry, not resolved material interfaces.
- TLMpy remains experimental and not JOSS-ready at v0.1.1.

## Closed issues

- #1
- #2
- #3
- #4
- #5
- #6

## Next priorities

- Design stub-loaded heterogeneous 2D TLM.
- Add dispersion-characterisation tooling.
- Add boundary-condition analysis suite.
- Benchmark against analytical and established-solver references.
- Build a public example gallery.
