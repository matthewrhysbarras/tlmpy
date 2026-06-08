# Benchmarking

TLMpy includes a lightweight JSON-friendly benchmark result schema for future
validation and reference-comparison work. It is infrastructure only: benchmark
scripts and external solver comparisons are not yet implemented.

## Purpose

The schema gives future benchmark scripts a stable way to store metadata,
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
    notes="Example metadata only; benchmark scripts are future work.",
)

result.to_json("benchmark_result.json")
loaded = result.from_json("benchmark_result.json")
```

## What This Does Not Do

- It does not run benchmarks.
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

`benchmarks/analytical_travel_time.py` runs a deterministic homogeneous
scalar-wave travel-time benchmark and writes
`outputs/benchmarks/analytical_travel_time.json`.

```bash
python benchmarks/analytical_travel_time.py
```

This benchmark checks the existing homogeneous mesh-speed relation only. It does
not validate heterogeneous media, PML, or external-solver agreement.
