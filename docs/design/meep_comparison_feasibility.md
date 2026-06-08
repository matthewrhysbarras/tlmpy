# Meep Comparison Feasibility

Decision: defer.

Meep is a mature electromagnetic FDTD package with Python scripting. It is a
serious candidate reference tool, but TLMpy v0.1.1 currently implements a
homogeneous scalar TLM-style wave demonstrator, not Maxwell-field FDTD. A Meep
comparison should not be added until the compared field, source, boundary and
metric are defined in a way that is scientifically meaningful.

Primary project documentation:

- https://meep.readthedocs.io/
- https://meep.readthedocs.io/en/latest/Introduction/

## Scientific Fit

Possible fit:

- a simple homogeneous propagation timing comparison;
- qualitative boundary-behavior comparison where the field component and
  boundary setup are explicitly mapped;
- future comparison after TLMpy has a validated formulation with a clearer
  physical target.

Current mismatch:

- Meep solves electromagnetic FDTD problems;
- TLMpy v0.1.1 exposes a scalar homogeneous TLM-style wave solver;
- TLMpy does not implement PML;
- TLMpy obstacle masks are approximate reflective geometry, not dielectric
  material interfaces;
- a direct "same simulation" claim would be misleading without a documented
  scalar-to-EM mapping.

## Installation Burden

Meep is not a lightweight pure-Python test dependency. Any future use should be
optional, isolated from normal package installation, and documented separately.
It should not become a required dependency for TLMpy tests or examples.

## CI Burden

Do not add Meep to the default CI matrix. If a future comparison is approved, it
should run in an optional workflow or local benchmark script that skips cleanly
when Meep is unavailable.

## What A Comparison Would Mean

A valid Meep comparison would mean that a specific TLMpy scalar setup behaves
consistently with a carefully selected electromagnetic FDTD setup under stated
assumptions. It would not prove:

- general TLM correctness;
- heterogeneous TLM support;
- PML support in TLMpy;
- production electromagnetics capability.

## Acceptance Gates Before Proceeding

- Define the exact comparable field quantity.
- Define source waveform, boundary condition and probe metric.
- Document why the scalar TLMpy result should match the chosen Meep result.
- Keep Meep optional and isolated from core tests.
- Record results with `BenchmarkResult`.
- State limitations next to any generated metric or figure.

## Recommendation

Defer implementation. Keep Meep as a candidate external reference, but first
complete a short design note for a single comparable benchmark case. Reject any
PR that adds Meep as a required dependency or implies that TLMpy is externally
validated by Meep before such a benchmark exists.
