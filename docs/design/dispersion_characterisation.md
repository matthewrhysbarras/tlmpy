# Dispersion Characterisation Design

This design note defines a future validation study for numerical dispersion in
TLMpy. It is not an implementation plan for new physics and does not claim that
dispersion is already characterised.

## Scope

The first target is the existing homogeneous 2D scalar TLM-style solver. A later
extension can reuse the same workflow for any reviewed stub-loaded heterogeneous
solver.

Goals:

- measure numerical phase and group velocity versus wavelength;
- measure directional dependence on the square grid;
- define tolerances for propagation-based wave-speed tests;
- produce documentation figures without overclaiming physical fidelity.

Non-goals:

- no PML design;
- no heterogeneous medium support;
- no 3D EM conclusions;
- no production acoustic, radar, medical, or ultrasound claims.

## Candidate Measurement Cases

Use square grids with `dx == dy`, matched boundaries, and sources placed far from
edges. Candidate cases:

1. Axis-aligned propagation along `x`.
2. Axis-aligned propagation along `y`.
3. Diagonal propagation at approximately 45 degrees.
4. Several wavelengths, from well-resolved to intentionally marginal.
5. Multiple source bandwidths to separate pulse bandwidth effects from grid
   dispersion.

Each case should report:

- grid size and spacing;
- timestep used by the solver;
- source waveform and central wavelength;
- probe locations;
- estimated velocity;
- relative error against `dx / (dt * sqrt(2))`;
- notes on boundary interaction, if any.

## Estimators

Initial estimators:

- cross-correlation between two probe traces;
- thresholded envelope arrival for broad pulses;
- optional sinusoidal phase-lag estimate for narrowband studies.

Cross-correlation is robust for regression tests but can hide pulse distortion.
Narrowband phase analysis may better expose dispersion, but requires a careful
steady-state or windowed setup.

## Acceptance Outputs

The study should produce:

- a table of measured velocity error versus wavelength and direction;
- plots suitable for documentation;
- recommended default tolerances for regression tests;
- a note describing cases where the solver should not be used without further
  validation.

## Open Questions

- Which estimator should be canonical for CI tests?
- What grid sizes keep CI fast while still measuring dispersion meaningfully?
- How should diagonal distance be computed for off-axis probe pairs?
- What wavelength range is scientifically useful for v0.2 documentation?
- Which analytical TLM dispersion relation should be cited for comparison?

Reference needed: a precise 2D shunt-node TLM dispersion relation for the scalar
quantity used by TLMpy.
