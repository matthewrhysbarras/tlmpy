# Benchmarking

TLMpy includes a lightweight JSON-friendly benchmark result schema and a small
set of deterministic benchmark scripts for current homogeneous v0.1 behavior.
External solver comparisons are not yet implemented.

## Purpose

The schema gives benchmark scripts a stable way to store metadata,
parameters, scalar metrics, tolerances and artifact paths. It supports
reproducible validation planning without adding external dependencies.

## Schema Fields

`tlmpy.benchmarking.BenchmarkResult` stores:

- `name`;
- `package_version`;
- `timestamp_utc`;
- `backend`;
- `grid_shape`;
- `grid_spacing`;
- `dt`;
- `steps`;
- `git_commit`;
- `parameters`;
- `metrics`;
- `tolerances`;
- `artifacts`;
- `environment`;
- `notes`.

The JSON representation uses lists for grid tuples and converts them back to
tuples when loaded.

## Minimal Example

```python
from tlmpy.benchmarking import make_benchmark_result

result = make_benchmark_result(
    name="homogeneous-travel-time",
    backend="numpy",
    grid_shape=(128, 128),
    grid_spacing=(1e-3, 1e-3),
    dt=4.7e-7,
    steps=200,
    parameters={"source": "RickerPulse"},
    metrics={"relative_speed_error": 0.03},
    tolerances={"relative_speed_error": 0.10},
    notes="Example metadata only; choose tolerances for each benchmark case.",
)

result.to_json("benchmark_result.json")
loaded = result.from_json("benchmark_result.json")
```

## What This Does Not Do

- It does not validate TLMpy against external solvers.
- It does not add Meep or `fdtd` dependencies.
- It does not implement heterogeneous media.
- It does not define release-gating tolerances by itself.

## Related Work

- #16 defines the benchmark result schema.
- #17 tracks an analytical scalar-wave travel-time benchmark.
- #18 tracks boundary reflection benchmarking.
- #19 tracks Meep comparison feasibility.
- #20 tracks Python `fdtd` comparison feasibility.
- #21 tracks benchmark documentation once initial benchmark scripts exist.

The broader benchmark plan is in
`docs/design/benchmarking_against_references.md`.

## Implemented Benchmarks

The current benchmark scripts are deterministic, use the NumPy backend, and
write `BenchmarkResult` JSON files under `outputs/benchmarks/`.

### Analytical Travel Time

```bash
python benchmarks/analytical_travel_time.py
```

Output:

- `outputs/benchmarks/analytical_travel_time.json`

What it measures:

- propagation speed between two probes in a homogeneous scalar-wave mesh;
- comparison against the mesh-speed relation `dx / (dt * sqrt(2))`;
- relative speed error using a cross-correlation arrival estimator.

Current tolerance:

- `relative_error <= 0.10`.

Limitations:

- the tolerance accounts for numerical dispersion and finite source bandwidth;
- this checks homogeneous mesh-speed behavior only;
- it does not validate heterogeneous media, PML or external-solver agreement.

### Boundary Reflection

This benchmark records source-free boundary behavior for the current homogeneous
solver.

```bash
python benchmarks/boundary_reflection.py
```

Output:

- `outputs/benchmarks/boundary_reflection.json`

What it measures:

- reflective-domain conservation of total four-port energy;
- matched-boundary energy loss for the same deterministic initial port state.

Current tolerances:

- `reflective_relative_energy_change <= 1e-12`;
- `matched_energy_ratio <= 0.95`.

Limitations:

- this is a source-free boundary behavior benchmark;
- it characterises the current first-order matched termination for one setup;
- it is not a PML test;
- it does not estimate a general reflection coefficient.

### Boundary Reflection Magnitude

This benchmark records a setup-specific normal-incidence reflection-magnitude
comparison for reflective and first-order matched terminations.

```bash
python benchmarks/boundary_reflection_magnitude.py
```

Output:

- `outputs/benchmarks/boundary_reflection_magnitude.json`

What it measures:

- incident peak amplitude at one probe between a source and the left boundary;
- reflected peak amplitude in a later expected reflection window;
- reflected-to-incident peak-amplitude ratio for reflective and matched
  boundaries;
- the matched ratio relative to the reflective ratio for the same geometry.

Current tolerances:

- `reflective_reflection_ratio >= 0.30`;
- `matched_to_reflective_ratio <= 0.35`.

Limitations:

- the metric is tied to this source, probe, grid and time-window setup;
- it is not a general reflection coefficient;
- it does not characterise oblique incidence, corners or broadband boundary
  behavior;
- it is not a PML test and does not claim full absorption.

### Dispersion Characterisation

This benchmark records an initial direction-dependent group-speed check for the
existing homogeneous scalar-wave solver.

```bash
python benchmarks/dispersion_characterisation.py
```

Output:

- `outputs/benchmarks/dispersion_characterisation.json`

What it measures:

- two-probe cross-correlation speed estimates along `x`, `y` and diagonal
  directions;
- maximum relative speed error against `dx / (dt * sqrt(2))`;
- relative spread between measured directional speeds.

Current tolerances:

- `max_relative_error <= 0.10`;
- `directional_spread_relative <= 0.03`.

Limitations:

- this is a CI-friendly group-speed directionality benchmark;
- it does not measure phase velocity;
- it does not sweep wavelength;
- it does not replace a full dispersion-characterisation notebook or analytical
  TLM dispersion comparison.

## Reading Results

Benchmark JSON files can be loaded with:

```python
from tlmpy.benchmarking import BenchmarkResult

result = BenchmarkResult.from_json("outputs/benchmarks/analytical_travel_time.json")
print(result.metrics)
```

Each result records the package version, backend, grid shape, grid spacing,
timestep, step count, benchmark parameters, scalar metrics and tolerances. The
JSON files are intended for reproducible local runs and future documentation
assets; they are not proof of production validation.

## Adding New Benchmarks

New benchmark scripts should:

- use deterministic parameters and seeds where applicable;
- write a `BenchmarkResult` JSON summary;
- document the governing behavior being checked;
- state tolerances explicitly;
- avoid optional external dependencies unless they are isolated and skipped
  cleanly;
- avoid claims about unimplemented physics.
