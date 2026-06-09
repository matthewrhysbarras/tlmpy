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

Boundary-specific benchmark results are summarized in
`docs/boundary_characterisation.md`.

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

### Boundary Coefficient Sweep

This benchmark sweeps the existing scalar boundary reflection coefficient for a
single normal-incidence source/probe setup.

```bash
python benchmarks/boundary_coefficient_sweep.py
```

Output:

- `outputs/benchmarks/boundary_coefficient_sweep.json`

What it measures:

- reflected-to-incident peak-amplitude ratio for coefficients `0.0`, `0.25`,
  `0.5`, `0.75` and `1.0`;
- monotonicity of the measured ratio across that coefficient sweep;
- ratio span between matched-like and reflective endpoints.

Current tolerance:

- `ratio_span >= 0.30`, with monotonic ratios required.

Limitations:

- the metric is tied to this source, probe, grid and time-window setup;
- it does not replace oblique-incidence or corner characterization;
- it is not a PML test and does not define general reflection behavior.

### Boundary Oblique Path

This benchmark sweeps the existing scalar boundary reflection coefficient for a
point-source/probe setup whose expected left-boundary return path is oblique.

```bash
python benchmarks/boundary_oblique_path.py
```

Output:

- `outputs/benchmarks/boundary_oblique_path.json`

What it measures:

- direct peak amplitude at one probe after a source pulse;
- later left-boundary return peak amplitude estimated with an image-source path;
- returned-to-direct peak-amplitude ratio for coefficients `0.0`, `0.25`,
  `0.5`, `0.75` and `1.0`;
- monotonicity of that setup-specific ratio across the coefficient sweep.

Current tolerance:

- `ratio_span >= 0.35`, with monotonic ratios required.

Limitations:

- this is a point-source oblique-path metric, not a plane-wave reflection
  coefficient;
- the metric is tied to this source, probe, grid and time-window setup;
- it is not a PML test and does not define general angle-dependent reflection
  behavior.

### Boundary Corner Behaviour

This benchmark records a setup-specific lower-left corner-return metric for
reflective and first-order matched terminations.

```bash
python benchmarks/boundary_corner_behaviour.py
```

Output:

- `outputs/benchmarks/boundary_corner_behaviour.json`

What it measures:

- direct peak amplitude at one probe after a source pulse;
- later corner-return peak amplitude estimated with a lower-left image-source
  path length;
- corner-return-to-direct peak-amplitude ratio for reflective and matched
  boundaries;
- the matched ratio relative to the reflective ratio for the same geometry.

Current tolerances:

- `reflective_corner_return_ratio >= 0.30`;
- `matched_to_reflective_ratio <= 0.35`.

Limitations:

- the metric is tied to this source, probe, grid, corner and time-window setup;
- it is not a general corner reflection coefficient;
- it does not characterize oblique incidence or broadband boundary behavior;
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

### Dispersion Wavelength Sweep

This benchmark sweeps a small set of Ricker-pulse frequencies and propagation
directions for the existing homogeneous scalar-wave solver.

```bash
python benchmarks/dispersion_wavelength_sweep.py
```

Output:

- `outputs/benchmarks/dispersion_wavelength_sweep.json`

What it measures:

- two-probe cross-correlation speed estimates for `x` and diagonal propagation;
- source frequencies `0.02`, `0.035`, `0.06` and `0.08`;
- central wavelength in cells, computed as expected mesh speed divided by source
  frequency;
- maximum relative speed error and overall speed spread.

Current tolerances:

- `max_relative_error <= 0.10`;
- `speed_spread_relative <= 0.04`.

Limitations:

- frequency is used as a source-bandwidth/wavelength proxy;
- cross-correlation is a coarse group-speed estimator;
- this does not measure phase velocity;
- this does not prove agreement with an analytical TLM dispersion relation.

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
