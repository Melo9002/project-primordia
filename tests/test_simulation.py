from dataclasses import replace
import numpy as np

from primordia.config import EnvironmentConfig, InitialConfig, ReactionConfig, WorldConfig
from primordia.config import load_config
from primordia.simulation.diffusion import laplacian
from primordia.simulation.engine import Simulation


def small(seed: int = 5) -> WorldConfig:
    return WorldConfig(width=32, height=24, seed=seed, initial=InitialConfig(seed_radius=3))


def test_deterministic_initialization_and_reset():
    first, second = Simulation(small()), Simulation(small())
    for left, right in zip(first.state.arrays(), second.state.arrays()):
        np.testing.assert_array_equal(left, right)
    first.step(9)
    first.reset()
    for left, right in zip(first.state.arrays(), second.state.arrays()):
        np.testing.assert_array_equal(left, right)


def test_identical_runs_are_reproducible_and_finite():
    first, second = Simulation(small(99)), Simulation(small(99))
    first.step(120)
    second.step(120)
    assert first.state.tick == 120
    for left, right in zip(first.state.arrays(), second.state.arrays()):
        np.testing.assert_array_equal(left, right)
        assert np.isfinite(left).all()
    assert min(array.min() for array in first.state.arrays()[:3]) >= 0


def test_periodic_laplacian_matches_impulse_and_conserves_sum():
    field = np.zeros((5, 5))
    field[0, 0] = 1.0
    result = laplacian(field, "periodic")
    assert result[0, 0] == -4.0
    assert result[0, -1] == result[-1, 0] == 1.0
    assert np.isclose(result.sum(), 0.0)


def test_reflective_laplacian_conserves_sum():
    rng = np.random.default_rng(4)
    assert np.isclose(laplacian(rng.random((9, 7)), "reflective").sum(), 0.0)


def test_closed_diffusion_only_world_conserves_each_field():
    cfg = small()
    cfg.initial = InitialConfig(a=0.7, b=0.0, resource=0.4, temperature=1.2, noise=0.0, seed_b=0.0)
    cfg.reaction = ReactionConfig(feed=0.0, kill=0.0, resource_half_saturation=0.2, temperature_sensitivity=0.0, reaction_heat=0.0, resource_cost=0.0)
    cfg.environment = EnvironmentConfig(ambient_temperature=1.0, thermal_exchange=0.0, external_heating=0.0, resource_supply=0.0, resource_removal=0.0, resource_target=1.0)
    simulation = Simulation(cfg)
    rng = np.random.default_rng(81)
    simulation.state.a[:] = 0.25 + 0.5 * rng.random(simulation.state.a.shape)
    simulation.state.resource[:] = 0.2 + 0.4 * rng.random(simulation.state.resource.shape)
    simulation.state.temperature[:] = 0.8 + 0.4 * rng.random(simulation.state.temperature.shape)
    totals = [array.sum() for array in simulation.state.arrays()]
    simulation.step(30)
    np.testing.assert_allclose([array.sum() for array in simulation.state.arrays()], totals, rtol=1e-12, atol=1e-12)


def test_disturbance_changes_real_state_locally():
    simulation = Simulation(small())
    before = simulation.state.temperature.copy()
    simulation.disturb(4, 5, 2, "T", 0.5)
    assert simulation.state.temperature[5, 4] > before[5, 4]
    assert np.count_nonzero(simulation.state.temperature != before) < before.size


def test_coral_preset_retains_spatial_pattern_after_long_run():
    simulation = Simulation(load_config("presets/coral.json"))
    simulation.step(1000)
    assert np.var(simulation.state.b) > 1e-4
    assert np.mean(simulation.state.b) > 1e-3
