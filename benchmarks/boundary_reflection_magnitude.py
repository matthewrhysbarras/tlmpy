"""Normal-incidence boundary reflection magnitude benchmark.

This benchmark uses the existing homogeneous 2D scalar TLM-style solver. A point
source launches a pulse toward the left boundary and a probe records the incident
and reflected arrivals in fixed time windows. The benchmark compares reflective
and first-order matched terminations for the same source/probe geometry.

The metric is a setup-specific reflected-to-incident peak-amplitude ratio. It is
not a general reflection coefficient, not a PML benchmark, and not external
solver validation.
"""

from __future__ import annotations

import argparse
from math import sqrt
from pathlib import Path

import numpy as np

from tlmpy import Grid2D
from tlmpy.benchmarking import BenchmarkResult, make_benchmark_result
from tlmpy.core.probes import PointProbe2D
from tlmpy.core.sources import PointSource2D, RickerPulse
from tlmpy.physics import ScalarWaveTLM2D

DEFAULT_OUTPUT = Path("outputs/benchmarks/boundary_reflection_magnitude.json")


def _peak_abs(trace: np.ndarray, center: int, half_width: int) -> float:
    lo = max(0, center - half_width)
    hi = min(trace.size, center + half_width + 1)
    return float(np.max(np.abs(trace[lo:hi])))


def _run_case(boundary: str):
    grid = Grid2D((180, 90), (1.0, 1.0))
    solver = ScalarWaveTLM2D(grid, wave_speed=1.0, boundary=boundary)
    source_location = (80, 45)
    probe_location = (50, 45)
    source_frequency = 0.035
    source_delay_steps = 16
    steps = 260

    solver.add_source(
        PointSource2D(
            source_location,
            RickerPulse(
                frequency=source_frequency,
                delay=source_delay_steps * solver.dt,
            ),
        )
    )
    solver.add_probe(PointProbe2D("probe", probe_location))
    result = solver.run(steps=steps)
    trace = result.probes["probe"]

    expected_speed = grid.dx / (result.dt * sqrt(2))
    source_delay = source_delay_steps * result.dt
    incident_distance = abs(source_location[0] - probe_location[0]) * grid.dx
    reflected_distance = (source_location[0] + probe_location[0]) * grid.dx
    incident_center = int(round((source_delay + incident_distance / expected_speed) / result.dt))
    reflected_center = int(round((source_delay + reflected_distance / expected_speed) / result.dt))
    window_half_width = 18
    incident_peak = _peak_abs(trace, incident_center, window_half_width)
    reflected_peak = _peak_abs(trace, reflected_center, window_half_width)
    reflection_ratio = reflected_peak / incident_peak

    return {
        "grid": grid,
        "dt": result.dt,
        "steps": steps,
        "source_location": source_location,
        "probe_location": probe_location,
        "source_frequency": source_frequency,
        "source_delay_steps": source_delay_steps,
        "expected_speed": expected_speed,
        "incident_center_step": incident_center,
        "reflected_center_step": reflected_center,
        "window_half_width_steps": window_half_width,
        "incident_peak": incident_peak,
        "reflected_peak": reflected_peak,
        "reflection_ratio": reflection_ratio,
    }


def run_benchmark(output_path: str | Path = DEFAULT_OUTPUT) -> BenchmarkResult:
    """Run the deterministic reflection-magnitude benchmark and write JSON."""
    reflective = _run_case("reflective")
    matched = _run_case("matched")
    ratio_reduction = matched["reflection_ratio"] / reflective["reflection_ratio"]
    reflective_min_ratio = 0.30
    matched_ratio_reduction_max = 0.35
    passed = (
        reflective["reflection_ratio"] >= reflective_min_ratio
        and ratio_reduction <= matched_ratio_reduction_max
    )

    grid = reflective["grid"]
    result = make_benchmark_result(
        name="boundary-reflection-magnitude",
        backend="numpy",
        grid_shape=grid.shape,
        grid_spacing=grid.spacing,
        dt=reflective["dt"],
        steps=reflective["steps"],
        parameters={
            "wave_speed": 1.0,
            "source_location": list(reflective["source_location"]),
            "probe_location": list(reflective["probe_location"]),
            "source": {
                "type": "RickerPulse",
                "frequency": reflective["source_frequency"],
                "delay_steps": reflective["source_delay_steps"],
            },
            "incident_center_step": reflective["incident_center_step"],
            "reflected_center_step": reflective["reflected_center_step"],
            "window_half_width_steps": reflective["window_half_width_steps"],
            "boundaries": ["reflective", "matched"],
        },
        metrics={
            "expected_speed": reflective["expected_speed"],
            "reflective_incident_peak": reflective["incident_peak"],
            "reflective_reflected_peak": reflective["reflected_peak"],
            "reflective_reflection_ratio": reflective["reflection_ratio"],
            "matched_incident_peak": matched["incident_peak"],
            "matched_reflected_peak": matched["reflected_peak"],
            "matched_reflection_ratio": matched["reflection_ratio"],
            "matched_to_reflective_ratio": ratio_reduction,
            "passed": passed,
        },
        tolerances={
            "reflective_reflection_ratio_min": reflective_min_ratio,
            "matched_to_reflective_ratio_max": matched_ratio_reduction_max,
        },
        artifacts={"result_json": str(output_path)},
        notes=(
            "Setup-specific normal-incidence reflection magnitude benchmark for "
            "the existing homogeneous solver. Matched is a first-order link "
            "termination, not PML or a full absorbing boundary condition."
        ),
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_json(output_path)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="JSON output path")
    args = parser.parse_args(argv)

    result = run_benchmark(args.output)
    print(f"benchmark={result.name}")
    print(f"output={args.output}")
    print(f"reflective_reflection_ratio={result.metrics['reflective_reflection_ratio']:.6g}")
    print(f"matched_reflection_ratio={result.metrics['matched_reflection_ratio']:.6g}")
    print(f"matched_to_reflective_ratio={result.metrics['matched_to_reflective_ratio']:.6g}")
    print(f"passed={result.metrics['passed']}")
    return 0 if result.metrics["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
