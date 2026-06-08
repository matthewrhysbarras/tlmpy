# Boundary Characterisation Design

This design note defines how TLMpy should characterise simple boundary
terminations before making stronger claims. It does not introduce a new boundary
condition.

## Current Boundary Model

The v0.1.1 solver exposes a scalar link-line reflection coefficient:

- `reflective`: `Gamma = 1`;
- `matched`: `Gamma = 0`;
- user coefficient in `[0, 1]`.

The `matched` option is a first-order link termination. It is not PML and should
not be described as a full absorbing boundary condition. It is expected to be
most accurate for normal incidence and leakier at oblique incidence.

## Characterisation Goals

Measure, document, and regression-test:

- normal-incidence reflection from `matched` and reflective boundaries;
- oblique-incidence reflection for several angles;
- early-time non-periodic behavior to guard against accidental torus wrapping;
- energy conservation in reflective domains;
- behavior near corners;
- interaction between source bandwidth and observed boundary reflection.

## Candidate Test Cases

1. Normal incidence pulse toward a flat boundary.
2. Oblique incidence pulse toward a flat boundary.
3. Pulse launched near one boundary with a probe near the opposite boundary,
   designed to fail if a periodic connection is introduced.
4. Reflective closed box with random port initial conditions and no source.
5. Corner reflection case with probes near both adjacent walls.

`benchmarks/boundary_reflection.py` implements an initial source-free benchmark
for case 4 and records matched-boundary energy loss for the same initial state.
It is a reproducibility benchmark for current behavior, not a complete boundary
reflection-characterisation suite.

`benchmarks/boundary_reflection_magnitude.py` implements an initial
normal-incidence source/probe benchmark for case 1. It compares peak amplitudes
in fixed incident and reflected time windows for reflective and first-order
matched terminations. The reported ratio is setup-specific and should not be
treated as a general reflection coefficient.

For each case, record:

- boundary type and coefficient;
- source location and waveform;
- probe positions;
- expected observation window;
- measured reflection amplitude;
- caveats about dispersion and source bandwidth.

## Documentation Rules

Use cautious wording:

- say "first-order matched termination";
- say "not PML";
- say "characterised for this setup" only after tests exist;
- do not call `matched` a general absorbing boundary condition.

## Open Questions

- Which reflection metric is stable enough for CI?
- What incidence angles can be generated cleanly with point sources?
- Should boundary characterisation use line sources or phased source arrays?
- How should corner behavior be separated from flat-boundary behavior?
- What reference results should be used for comparison?

Reference needed: a boundary-characterisation reference for 2D TLM link-line
terminations.
