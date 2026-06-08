# TLMpy v0.1.0

Initial public seed release of TLMpy, a Python-first experimental toolkit for Transmission Line Matrix (TLM) style scalar wave simulation.

## Included

- Homogeneous 2D scalar TLM-style wave demonstrator.
- Derived timestep based on the 2D TLM mesh velocity relation.
- Reflective and first-order matched boundary handling.
- Reflective obstacle masks, treated as geometric approximations.
- FTCS 2D diffusion reference solver for validation support.
- NumPy backend by default.
- Optional CuPy backend path, skipped cleanly when CuPy is unavailable.
- Optional matplotlib visualisation.
- CLI entry point.
- Examples, tests, documentation skeleton, citation metadata and JOSS-style draft paper skeleton.

## Validation included

- Port-energy conservation test for reflective lossless wave simulations.
- Exact timestep formula test.
- Non-periodic boundary regression.
- Neumann diffusion mass-conservation test.
- Analytical Gaussian diffusion comparison.
- Optional NumPy/CuPy parity test when CuPy is installed.

## Known limitations

- v0.1 is experimental and not JOSS-ready.
- No heterogeneous wave-speed media.
- No stub-loaded TLM nodes.
- No PML.
- No 3D EM.
- No anisotropic wave mesh.
- Matched boundary is first-order and not a full absorbing boundary condition.
- Obstacle masks are approximate reflective geometry, not resolved material interfaces.

## Next priorities

- Strengthen propagation-based wave-speed validation.
- Add obstacle-mask regression tests.
- Improve boundary-condition characterisation.
- Add SimulationResult save/load round-trip tests.
- Design stub-loaded heterogeneous 2D TLM for v0.2.
- Add dispersion-characterisation tooling.
