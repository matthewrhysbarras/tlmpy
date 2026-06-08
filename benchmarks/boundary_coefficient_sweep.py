"""Boundary reflection-coefficient sweep benchmark.

This benchmark characterises the existing scalar boundary coefficient API for a
single normal-incidence source/probe setup. It sweeps boundary coefficients from
matched-like ``0.0`` to reflective ``1.0`` and records reflected-to-incident peak
amplitude ratios.

The result is setup-specific. It is not a PML benchmark and does not define a
general boundary reflection coefficient for all angles or waveforms.
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

DEFAULT_OUTPUT = Path("outputs/benchmarks/boundary_coefficient_sweep.json")
COEFFICIENTS = (0.0, 0.25, 0.5, 0.75, 1.0)


def _peak_abs(trace: np.ndarray, center: int, half_width: int) -> float:
    lo = max(0, center - half_width)
    hi = min(trace.size, center + half_width + 1)
    return float(np.max(np.abs(trace[lo:hi])))


def _run_case(coefficient: float) -> dict[str, float]:
    grid = Grid2D((180, 90), (1.0, 1.0))
    solver = ScalarWaveTLM2D(grid, wave_speed=1.0, boundary=coefficient)
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
        "coefficient": coefficient,
        "incident_peak": incident_peak,
        "reflected_peak": reflected_peak,
        "reflection_ratio": reflection_ratio,
        "expected_speed": expected_speed,
        "dt": result.dt,
        "steps": steps,
        "incident_center_step": incident_center,
        "reflected_center_step": reflected_center,
        "window_half_width_steps": window_half_width,
    }


def run_benchmark(output_path: str | Path = DEFAULT_OUTPUT) -> BenchmarkResult:
    """Run the deterministic coefficient sweep benchmark and write JSON."""
    cases = [_run_case(coefficient) for coefficient in COEFFICIENTS]
    ratios = [case["reflection_ratio"] for case in cases]
    monotonic = all(a <= b for a, b in zip(ratios, ratios[1:], strict=False))
    ratio_span = ratios[-1] - ratios[0]
    min_ratio_span = 0.30
    passed = monotonic and ratio_span >= min_ratio_span

    grid = Grid2D((180, 90), (1.0, 1.0))
    metrics = {
        "monotonic_reflection_ratio": monotonic,
        "ratio_span": ratio_span,
        "passed": passed,
    }
    for case in cases:
        key = str(case["coefficient"]).replace(".", "_")
        metrics[f"gamma_{key}_reflection_ratio"] = case["reflection_ratio"]

    result = make_benchmark_result(
        name="boundary-coefficient-sweep",
        backend="numpy",
        grid_shape=grid.shape,
        grid_spacing=grid.spacing,
        dt=cases[0]["dt"],
        steps=int(cases[0]["steps"]),
        parameters={
            "wave_speed": 1.0,
            "coefficients": list(COEFFICIENTS),
            "source_location": [80, 45],
            "probe_location": [50, 45],
            "source": {
                "type": "RickerPulse",
                "frequency": 0.035,
                "delay_steps": 16,
            },
            "incident_center_step": int(cases[0]["incident_center_step"]),
            "reflected_center_step": int(cases[0]["reflected_center_step"]),
            "window_half_width_steps": int(cases[0]["window_half_width_steps"]),
        },
        metrics=metrics,
        tolerances={"min_ratio_span": min_ratio_span},
        artifacts={"result_json": str(output_path)},
        notes=(
            "Setup-specific sweep of existing boundary reflection coefficients. "
            "The result is not a general reflection coefficient and does not "
            "claim PML or full absorbing-boundary behavior."
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
    print(f"monotonic_reflection_ratio={result.metrics['monotonic_reflection_ratio']}")
    print(f"passed={result.metrics['passed']}")
    return 0 if result.metrics["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
