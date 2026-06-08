import json

import pytest

from tlmpy._version import __version__
from tlmpy.benchmarking import BenchmarkResult, make_benchmark_result


def test_minimal_result_creation():
    result = make_benchmark_result("travel-time", backend="numpy")

    assert result.name == "travel-time"
    assert result.backend == "numpy"
    assert result.package_version == __version__
    assert result.timestamp_utc


@pytest.mark.parametrize(
    ("name", "backend", "message"),
    [
        ("", "numpy", "benchmark name"),
        ("case", "", "backend"),
    ],
)
def test_required_string_validation(name, backend, message):
    with pytest.raises(ValueError, match=message):
        make_benchmark_result(name, backend=backend)


@pytest.mark.parametrize("shape", [(0, 4), (4, -1), (4,), (4.0, 5)])
def test_grid_shape_validation(shape):
    with pytest.raises(ValueError, match="grid_shape"):
        make_benchmark_result("case", backend="numpy", grid_shape=shape)


@pytest.mark.parametrize("spacing", [(0.0, 1.0), (1.0, -1.0), (1.0,), ("bad", 1.0)])
def test_grid_spacing_validation(spacing):
    with pytest.raises((ValueError, TypeError), match="grid_spacing|could not convert"):
        make_benchmark_result("case", backend="numpy", grid_spacing=spacing)


def test_dt_and_steps_validation():
    with pytest.raises(ValueError, match="dt"):
        make_benchmark_result("case", backend="numpy", dt=0.0)
    with pytest.raises(ValueError, match="steps"):
        make_benchmark_result("case", backend="numpy", steps=-1)


def test_to_dict_is_json_friendly():
    result = make_benchmark_result(
        "case",
        backend="numpy",
        grid_shape=(8, 9),
        grid_spacing=(0.1, 0.2),
        dt=0.01,
        steps=10,
        metrics={"relative_error": 0.05, "passed": True},
        artifacts={"plot": "outputs/case.png"},
    )

    data = result.to_dict()
    json.dumps(data)

    assert data["grid_shape"] == [8, 9]
    assert data["grid_spacing"] == [0.1, 0.2]


def test_from_dict_round_trip():
    original = make_benchmark_result(
        "case",
        backend="numpy",
        timestamp_utc="2026-06-08T12:00:00+00:00",
        grid_shape=(8, 9),
        grid_spacing=(0.1, 0.2),
        dt=0.01,
        steps=10,
        git_commit="abc123",
        parameters={"source": {"frequency": 10.0}},
        metrics={"relative_error": 0.05},
        tolerances={"relative_error": 0.1},
        artifacts={"plot": "outputs/case.png"},
        environment={"python": "3.12"},
        notes="deterministic smoke benchmark",
    )

    loaded = BenchmarkResult.from_dict(original.to_dict())

    assert loaded == original
    assert loaded.grid_shape == (8, 9)
    assert loaded.grid_spacing == (0.1, 0.2)


def test_json_round_trip(tmp_path):
    result = make_benchmark_result(
        "case",
        backend="numpy",
        timestamp_utc="2026-06-08T12:00:00+00:00",
        metrics={"speed": 1.0},
    )
    path = tmp_path / "benchmark.json"

    result.to_json(path)
    loaded = BenchmarkResult.from_json(path)

    assert loaded == result


def test_metrics_and_artifacts_reject_non_json_scalars():
    with pytest.raises(TypeError, match="metric"):
        make_benchmark_result("case", backend="numpy", metrics={"trace": [1.0, 2.0]})
    with pytest.raises(TypeError, match="artifact"):
        make_benchmark_result("case", backend="numpy", artifacts={"plot": 3})
