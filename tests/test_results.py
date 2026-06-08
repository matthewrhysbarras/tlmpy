import numpy as np

from tlmpy.core.results import SimulationResult


def test_result_npz_round_trip_one_probe(tmp_path):
    result = SimulationResult(
        probes={"centre": np.array([1.0, 2.0, 3.0])},
        time=np.array([0.0, 0.1, 0.2]),
        dt=0.1,
        metadata={"case": "one-probe", "steps": 3},
        final_field=np.arange(4.0).reshape(2, 2),
    )

    path = tmp_path / "result.npz"
    result.save_npz(path)
    loaded = SimulationResult.load_npz(path)

    assert isinstance(loaded.time, np.ndarray)
    assert isinstance(loaded.probes["centre"], np.ndarray)
    assert isinstance(loaded.final_field, np.ndarray)
    np.testing.assert_array_equal(loaded.probes["centre"], result.probes["centre"])
    np.testing.assert_array_equal(loaded.time, result.time)
    np.testing.assert_array_equal(loaded.final_field, result.final_field)
    assert loaded.dt == result.dt
    assert loaded.metadata == result.metadata


def test_result_npz_round_trip_multiple_probes(tmp_path):
    result = SimulationResult(
        probes={
            "left": np.array([0.0, 1.0]),
            "right": np.array([2.0, 3.0]),
        },
        time=np.array([0.0, 0.5]),
        dt=0.5,
        metadata={"case": "multi-probe"},
    )

    path = tmp_path / "multi.npz"
    result.save_npz(path)
    loaded = SimulationResult.load_npz(path)

    assert set(loaded.probes) == {"left", "right"}
    for name in result.probes:
        assert isinstance(loaded.probes[name], np.ndarray)
        np.testing.assert_array_equal(loaded.probes[name], result.probes[name])
    np.testing.assert_array_equal(loaded.time, result.time)
    assert loaded.final_field is None
    assert loaded.dt == result.dt
    assert loaded.metadata == result.metadata
