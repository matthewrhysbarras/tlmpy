# Benchmarking Against References Design

This design note defines how TLMpy should compare existing and future solvers
against analytical references or established tools. It does not add benchmark
code, dependencies, or claims of agreement.

TLMpy now provides a lightweight `BenchmarkResult` schema for benchmark outputs.
Initial benchmark scripts cover homogeneous travel time and source-free boundary
behavior. External solver comparisons described here remain future work.

## Goals

- Build confidence in implemented behavior through independent reference cases.
- Separate validation from performance benchmarking.
- Record assumptions, tolerances, and failure modes before adding comparison
  scripts.
- Avoid implying that unimplemented v0.2 features are complete.

## Near-Term Reference Cases

Start with cases that do not require external solvers:

1. Homogeneous scalar wave travel time in a large matched domain.
2. Reflective-domain port-energy conservation.
3. Non-periodic boundary regression.
4. Gaussian diffusion against the analytical heat kernel.
5. Neumann diffusion mass conservation.

These are already partly covered by tests. A benchmark suite should turn them
into reproducible, documented reference runs with fixed parameters and stored
summary metrics.

The first concrete benchmarks are:

- `benchmarks/analytical_travel_time.py`, which records a homogeneous scalar-wave
  travel-time result using the `BenchmarkResult` schema. It validates the
  homogeneous mesh-speed relation only.
- `benchmarks/boundary_reflection.py`, which records source-free reflective
  energy conservation and matched-boundary energy loss for one deterministic
  setup. It does not claim that the matched termination is a full absorber.

## External Solver Comparisons

External comparisons should be optional and isolated from core tests.

Candidate references:

- Meep for simple wave/FDTD-style reference cases, where the modeled equation and
  boundary assumptions are comparable.
- The Python `fdtd` package for simple grid-propagation comparisons, if the
  scalar quantity and boundary setup can be matched honestly.
- Published analytical TLM dispersion or interface results, where available.

Do not add Meep or `fdtd` as core dependencies. Any comparison scripts should
live outside the import path, document optional installation steps, and skip
cleanly when optional tools are unavailable.

## What Not To Compare Yet

Do not benchmark or compare:

- heterogeneous wave-speed media, until a stub-loaded formulation is implemented
  and reviewed;
- PML, because TLMpy does not implement PML;
- 3D EM, medical, radar, mmWave, or ultrasound claims;
- obstacle masks as material interfaces;
- diffusion as a TLM method.

## Acceptance Criteria

Each benchmark/reference case should define:

- purpose of the case;
- governing equation or discrete model being compared;
- grid, timestep, source, boundary, and probe setup;
- expected result or reference source;
- metric and tolerance;
- runtime budget;
- optional dependencies;
- known limitations.

A benchmark is not complete if it only produces a plot without numerical summary
metrics.

## Reproducibility Requirements

- Use deterministic parameters and seeds.
- Save machine-readable metrics, such as JSON or NPZ.
- Record package version, backend, grid size, timestep, and optional dependency
  versions.
- Prefer `tlmpy.benchmarking.BenchmarkResult` for JSON summary files.
- Keep generated artifacts out of the repository unless they are small,
  intentionally curated documentation assets.
- Prefer scripts that can be run from the repository root.

## Future Issue Breakdown

Suggested follow-up issues:

1. Add boundary reflection and passivity benchmark refinements.
2. Add optional Meep comparison feasibility study.
3. Add optional `fdtd` comparison feasibility study.
4. Add benchmark result documentation page.
5. Convert additional validation tests into documented benchmark cases.

## Open Questions

- Which external solver comparison is scientifically closest to the scalar field
  represented by TLMpy?
- What boundary setup makes a fair comparison possible without PML?
- Which metrics should gate future releases versus remain exploratory?
- Where should optional benchmark outputs be stored for reproducible papers?
- What is the smallest comparison that would strengthen a future JOSS submission?
