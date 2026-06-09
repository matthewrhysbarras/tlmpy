"""Oblique-path boundary reflection benchmark.

This benchmark uses the existing homogeneous 2D scalar TLM-style solver. A point
source and probe are placed so the expected left-boundary return path is oblique
to the boundary. The benchmark sweeps selected scalar boundary coefficients and
records setup-specific returned-to-direct peak-amplitude ratios.

The metric is not a plane-wave reflection coefficient, not a PML benchmark, and
not external solver validation.
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

DEFAULT_OUTPUT = Path("outputs/benchmarks/boundary_oblique_path.json")
COEFFICIENTS = (0.0, 0.25, 0.5, 0.75, 1.0)


def _peak_abs(trace: np.ndarray, center: int, half_width: int) -> float:
    lo = max(0, center - half_width)
    hi = min(trace.size, center + half_width + 1)
    return float(np.max(np.abs(trace[lo:hi])))


def _run_case(coefficient: float) -> dict[str, float | int]:
    grid = Grid2D((180, 140), (1.0, 1.0))
    solver = ScalarWaveTLM2D(grid, wave_speed=1.0, boundary=coefficient)
    source_location = (90, 80)
    probe_location = (55, 45)
    source_frequency = 0.03
    source_delay_steps = 18
    steps = 340

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
    direct_distance = sqrt(
        (source_location[0] - probe_location[0]) ** 2
        + (source_location[1] - probe_location[1]) ** 2
    )
    # Image-source estimate for an oblique return from the left boundary.
    oblique_return_distance = sqrt(
        (source_location[0] + probe_location[0]) ** 2
        + (source_location[1] - probe_location[1]) ** 2
    )
    direct_center = int(round((source_delay + direct_distance / expected_speed) / result.dt))
    oblique_return_center = int(
        round((source_delay + oblique_return_distance / expected_speed) / result.dt)
    )
    window_half_width = 22
    direct_peak = _peak_abs(trace, direct_center, window_half_width)
    oblique_return_peak = _peak_abs(trace, oblique_return_center, window_half_width)
    oblique_return_ratio = oblique_return_peak / direct_peak

    return {
        "coefficient": coefficient,
        "direct_peak": direct_peak,
        "oblique_return_peak": oblique_return_peak,
        "oblique_return_ratio": oblique_return_ratio,
        "expected_speed": expected_speed,
        "dt": result.dt,
        "steps": steps,
        "direct_center_step": direct_center,
        "oblique_return_center_step": oblique_return_center,
        "window_half_width_steps": window_half_width,
    }


def run_benchmark(output_path: str | Path = DEFAULT_OUTPUT) -> BenchmarkResult:
    """Run the deterministic oblique-path benchmark and write JSON."""
    cases = [_run_case(coefficient) for coefficient in COEFFICIENTS]
    ratios = [case["oblique_return_ratio"] for case in cases]
    monotonic = all(a <= b for a, b in zip(ratios, ratios[1:], strict=False))
    ratio_span = ratios[-1] - ratios[0]
    min_ratio_span = 0.35
    passed = monotonic and ratio_span >= min_ratio_span

    grid = Grid2D((180, 140), (1.0, 1.0))
    metrics = {
        "monotonic_oblique_return_ratio": monotonic,
        "ratio_span": ratio_span,
        "passed": passed,
    }
    for case in cases:
        key = str(case["coefficient"]).replace(".", "_")
        metrics[f"gamma_{key}_oblique_return_ratio"] = case["oblique_return_ratio"]

    result = make_benchmark_result(
        name="boundary-oblique-path",
        backend="numpy",
        grid_shape=grid.shape,
        grid_spacing=grid.spacing,
        dt=cases[0]["dt"],
        steps=int(cases[0]["steps"]),
        parameters={
            "wave_speed": 1.0,
            "coefficients": list(COEFFICIENTS),
            "source_location": [90, 80],
            "probe_location": [55, 45],
            "source": {
                "type": "RickerPulse",
                "frequency": 0.03,
                "delay_steps": 18,
            },
            "direct_center_step": int(cases[0]["direct_center_step"]),
            "oblique_return_center_step": int(cases[0]["oblique_return_center_step"]),
            "window_half_width_steps": int(cases[0]["window_half_width_steps"]),
        },
        metrics=metrics,
        tolerances={"min_ratio_span": min_ratio_span},
        artifacts={"result_json": str(output_path)},
        notes=(
            "Setup-specific point-source oblique-path boundary benchmark for "
            "the existing homogeneous solver. It is not a plane-wave reflection "
            "coefficient and does not claim PML or full absorbing-boundary "
            "behavior."
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
    print(f"ratio_span={result.metrics['ratio_span']:.6g}")
    print(f"monotonic_oblique_return_ratio={result.metrics['monotonic_oblique_return_ratio']}")
    print(f"passed={result.metrics['passed']}")
    return 0 if result.metrics["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
