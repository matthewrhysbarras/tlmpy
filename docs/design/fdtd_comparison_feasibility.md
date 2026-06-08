# Python fdtd Package Comparison Feasibility

Decision: defer, with a higher risk of rejection than Meep unless a narrow
comparison target is identified.

The Python `fdtd` package is an electromagnetic FDTD simulator with optional GPU
support. It may be useful for lightweight exploration, but TLMpy v0.1.1 is a
homogeneous scalar TLM-style wave package. A direct comparison would need a
careful field and metric mapping before it could strengthen validation.

Primary project documentation:

- https://github.com/flaport/fdtd
- https://pypi.org/project/fdtd/

## Scientific Fit

Possible fit:

- exploratory comparison of propagation timing in a simple homogeneous grid;
- checking whether a scalar probe trace can be matched to one field component in
  a deliberately simplified electromagnetic setup.

Current mismatch:

- `fdtd` models electromagnetic fields, not TLMpy's scalar field;
- TLMpy v0.1.1 has no dielectric media model or PML;
- obstacle masks in TLMpy are approximate reflective geometry, not material
  interfaces;
- matching boundary behavior may be more difficult than matching propagation
  timing.

## Installation Burden

The package is lighter-weight than Meep in spirit, but it is still an optional
external solver dependency and should not be required for installing or testing
TLMpy. Any future use should live outside the core import path and skip cleanly
when unavailable.

## CI Burden

Do not add `fdtd` to default CI. If a comparison is later implemented, use an
optional benchmark command or optional CI job. The default test suite should
remain dependency-light.

## What A Comparison Would Mean

A valid comparison would be a narrow cross-check for one chosen field component,
setup and metric. It would not validate:

- heterogeneous TLM;
- PML;
- obstacle masks as material interfaces;
- production electromagnetic simulation;
- general agreement with all FDTD solvers.

## Acceptance Gates Before Proceeding

- Identify a scalar quantity from the `fdtd` simulation that can be compared
  honestly with TLMpy's scalar field.
- Define grid spacing, timestep handling, source waveform and boundary setup.
- Confirm the comparison adds information beyond TLMpy's analytical travel-time
  benchmark.
- Keep the dependency optional.
- Save metrics with `BenchmarkResult`.
- Document limitations in the benchmark output and docs.

## Recommendation

Defer implementation. If no narrow scalar-field mapping can be justified, reject
this comparison and prefer analytical benchmarks or published TLM references.
