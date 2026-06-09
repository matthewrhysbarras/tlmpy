# Boundary Characterisation

This page summarizes the current boundary-characterisation benchmark results for
the homogeneous v0.1.1 scalar-wave solver. It does not define a new boundary
condition and does not claim that `matched` is PML or a full absorbing boundary.

The solver currently exposes:

- `boundary="reflective"`: scalar link-line reflection coefficient `Gamma = 1`;
- `boundary="matched"`: first-order link termination, `Gamma = 0`;
- numeric coefficients in `[0, 1]`.

All metrics below are setup-specific benchmark outputs. They are useful
regressions for current behavior, not general reflection coefficients.

## Source-Free Boundary Behaviour

Command:

```bash
python benchmarks/boundary_reflection.py
```

Current benchmark output:

- reflective relative energy change: `1.39014e-16`;
- matched energy ratio after 60 steps: `0.533333`;
- pass criteria:
  - `reflective_relative_energy_change <= 1e-12`;
  - `matched_energy_ratio <= 0.95`.

Interpretation:

- reflective boundaries conserve total four-port energy to roundoff in this
  source-free closed-domain setup;
- matched boundaries remove energy from this setup;
- this does not measure angle-dependent reflection.

## Normal-Incidence Reflection Magnitude

Command:

```bash
python benchmarks/boundary_reflection_magnitude.py
```

Current benchmark output:

- reflective reflected-to-incident ratio: `0.478891`;
- matched reflected-to-incident ratio: `0.0788158`;
- matched-to-reflective ratio: `0.16458`;
- pass criteria:
  - `reflective_reflection_ratio >= 0.30`;
  - `matched_to_reflective_ratio <= 0.35`.

Interpretation:

- for this normal-incidence source/probe setup, the first-order matched
  termination produces a lower reflected peak than the reflective boundary;
- the ratio is tied to this grid, source, probe and time-window setup;
- it is not a general boundary reflection coefficient.

## Boundary Coefficient Sweep

Command:

```bash
python benchmarks/boundary_coefficient_sweep.py
```

Current benchmark output:

- `Gamma = 0.0`: ratio `0.0788158`;
- `Gamma = 0.25`: ratio `0.184484`;
- `Gamma = 0.5`: ratio `0.287908`;
- `Gamma = 0.75`: ratio `0.385540`;
- `Gamma = 1.0`: ratio `0.478891`;
- ratio span: `0.400075`;
- pass criteria:
  - ratios are monotonic across this coefficient sweep;
  - `ratio_span >= 0.30`.

Interpretation:

- the measured reflected-to-incident peak ratio increases monotonically with the
  configured scalar boundary coefficient in this setup;
- this supports regression testing of the existing coefficient API;
- it does not characterize all waveforms, incidence angles or corner behavior.

## Remaining Gaps

Still uncharacterized:

- oblique-incidence boundary reflection;
- corner behavior;
- broadband sensitivity;
- published analytical boundary-reference comparison.

Tracked follow-up issues:

- #40: oblique-incidence boundary benchmark;
- #41: corner boundary behaviour benchmark;
- #43: published TLM or analytical reference benchmark cases.
