# Validation Checklist

Use this checklist before merging numerical changes, new examples, or stronger
claims. It is intentionally conservative.

## General Gates

- The change has a clear scope and does not introduce unrelated features.
- Existing public APIs remain compatible unless a breaking change is explicitly
  planned and documented.
- `ruff check .` passes.
- `pytest` passes.
- CLI smoke checks pass:
  - `python -m tlmpy --version`
  - `python -m tlmpy info`
- Any new example creates outputs in a documented location and does not require
  non-core dependencies unless the dependency is an optional extra.

## Numerical Claims

Before adding or strengthening a numerical claim, identify:

- governing equation or discrete model;
- assumptions and limitations;
- reference result or conservation property;
- tolerance and why it is reasonable;
- failure mode the test is expected to catch.

Do not use a test that only compares an implementation against itself unless the
test is explicitly labeled as a regression or smoke test.

## Scalar Wave Solver

For homogeneous wave changes, consider:

- exact `dt = dx / (wave_speed * sqrt(2))`;
- no free `dt` in `ScalarWaveTLM2D.run`;
- no accidental periodic wraparound;
- port-energy conservation for reflective, source-free runs;
- propagation-based wave-speed regression;
- boundary behavior separated from interior propagation.

## Obstacles

Obstacle masks are approximate reflective geometry. They are not material
interfaces. Tests may assert:

- mask shape and geometry;
- finite fields;
- changed propagation relative to no obstacle;
- no unbounded energy growth in reflective source-free cases.

Tests should not assert refractive behavior or heterogeneous material physics for
obstacle masks.

## Diffusion Reference Solver

The diffusion solver is an FTCS reference solver, not TLM. Check:

- von Neumann timestep bound;
- Neumann mass conservation;
- Dirichlet boundary behavior;
- analytical Gaussian comparison only when the finite domain approximates the
  infinite-domain solution.

## Heterogeneous TLM Work

Do not expose heterogeneous wave-speed media as public API until:

- the stub-loaded formulation is specified with references;
- passive parameter ranges are known;
- homogeneous limit matches the v0.1 solver;
- interface reflection/transmission is validated;
- travel-time through multiple media is validated;
- stability sweeps are documented;
- boundary implications are reviewed.

## Documentation Review

Search changed documentation for wording that implies:

- TLMpy is production-ready;
- TLMpy is JOSS-ready;
- PML exists;
- heterogeneous media are implemented;
- matched boundaries are full absorbers;
- obstacle masks are material interfaces;
- the diffusion solver is a TLM method;
- medical, radar, or ultrasound examples are physically validated.

Replace overclaims with terms such as "experimental", "planned", "design note",
"candidate formulation", "requires validation", or "reference needed".
