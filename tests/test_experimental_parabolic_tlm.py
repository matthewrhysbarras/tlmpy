import numpy as np
import pytest

from tlmpy import Grid2D
from tlmpy.experimental import ParabolicTLMDiffusion2D, TLMStateEstimator, parabolic_ys


def _model() -> ParabolicTLMDiffusion2D:
    grid = Grid2D((9, 9), (0.001, 0.001))
    return ParabolicTLMDiffusion2D(
        grid,
        dt=0.001,
        thermal_conductivity=300.0,
        specific_heat=300.0,
        density=8930.0,
    )


def test_parabolic_ys_calculation_and_validation():
    ys = parabolic_ys(
        spacing=0.001,
        dt=0.001,
        thermal_conductivity=300.0,
        specific_heat=300.0,
        density=8930.0,
    )

    assert ys == pytest.approx(4.93)

    with pytest.raises(ValueError, match="Ys"):
        parabolic_ys(
            spacing=0.001,
            dt=0.01,
            thermal_conductivity=300.0,
            specific_heat=300.0,
            density=8930.0,
        )


def test_parabolic_tlm_shapes_and_equal_pulse_temperature():
    model = _model()
    target = np.ones(model.grid.shape)

    model.set_equal_pulse_temperature(target)

    assert model.v1.shape == model.grid.shape
    assert model.vs.shape == model.grid.shape
    np.testing.assert_allclose(model.temperature(), target)


def test_parabolic_tlm_step_remains_finite_and_bounded_for_closed_domain():
    model = _model()
    rng = np.random.default_rng(1234)
    initial = rng.random(model.grid.shape)
    model.set_equal_pulse_temperature(initial)
    initial_proxy = model.pulse_energy_proxy()

    for _ in range(20):
        model.step()

    assert np.isfinite(model.temperature()).all()
    assert model.pulse_energy_proxy() <= initial_proxy * 1.01


def test_estimator_rejects_unstable_ld_and_reduces_target_error():
    model = _model()
    target = np.zeros(model.grid.shape)
    target[4, 4] = 1.0
    model.set_equal_pulse_temperature(np.zeros(model.grid.shape))

    with pytest.raises(ValueError, match="greater than 2"):
        TLMStateEstimator(model, ld=2.0)

    estimator = TLMStateEstimator(model, ld=10.32)
    initial_error = np.sqrt(np.mean((target - model.temperature()) ** 2))
    history = estimator.converge_to_target(target, max_iterations=40, tolerance=1e-4)
    final_error = np.sqrt(np.mean((target - model.temperature()) ** 2))

    assert history.iterations > 0
    assert final_error < initial_error
