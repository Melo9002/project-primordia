import csv
import json
import numpy as np

from primordia.config import EnvironmentConfig, InitialConfig, PalimpsestConfig, ReactionConfig, WorldConfig, load_config
from primordia.experiments.metrics import enclosed_mask
from primordia.experiments.runner import run_homeostasis_controls
from primordia.simulation.diffusion import variable_diffusion
from primordia.simulation.engine import Simulation
from primordia.simulation.environment import environment_terms


def palimpsest_config() -> WorldConfig:
    return WorldConfig(
        width=24,
        height=24,
        seed=9,
        initial=InitialConfig(seed_radius=3),
        palimpsest=PalimpsestConfig(enabled=True, matrix_deposition=0.4),
    )


def test_variable_diffusion_is_conservative_and_matrix_can_suppress_flux():
    field = np.zeros((9, 9))
    field[4, 4] = 1.0
    fast = variable_diffusion(field, np.ones_like(field), "reflective")
    diffusivity = np.ones_like(field)
    diffusivity[3:6, 3:6] = 0.01
    slow = variable_diffusion(field, diffusivity, "reflective")
    assert np.isclose(fast.sum(), 0.0)
    assert np.isclose(slow.sum(), 0.0)
    assert np.abs(slow).sum() < np.abs(fast).sum()


def test_matrix_forms_from_activity_and_erodes_without_it():
    simulation = Simulation(palimpsest_config())
    simulation.step(120)
    assert simulation.state.waste.max() > 0
    assert simulation.state.matrix.max() > 0
    simulation.config.reaction = ReactionConfig(feed=0.0, kill=0.0, reaction_heat=0.0, resource_cost=0.0)
    simulation.config.palimpsest.matrix_deposition = 0.0
    simulation.config.palimpsest.matrix_dissolution = 0.0
    before = float(simulation.state.matrix.sum())
    simulation.step(20)
    assert simulation.state.matrix.sum() < before


def test_enclosure_detector_finds_cells_inside_matrix_ring():
    matrix = np.zeros((11, 11))
    matrix[3, 3:8] = 1.0
    matrix[7, 3:8] = 1.0
    matrix[3:8, 3] = 1.0
    matrix[3:8, 7] = 1.0
    interior = enclosed_mask(matrix, 0.5)
    assert interior[5, 5]
    assert np.count_nonzero(interior) == 9


def test_boundary_exchange_only_acts_at_world_edge():
    resource = np.zeros((7, 7))
    temperature = np.zeros((7, 7))
    config = EnvironmentConfig(
        ambient_temperature=1.0,
        thermal_exchange=0.1,
        resource_supply=0.2,
        resource_target=1.0,
        exchange_mode="boundary",
    )
    resource_term, temperature_term = environment_terms(resource, temperature, config)
    assert resource_term[0, 3] > 0
    assert temperature_term[-1, 3] > 0
    assert resource_term[3, 3] == 0
    assert temperature_term[3, 3] == 0


def test_homeostasis_controls_share_history_and_write_all_outputs(tmp_path):
    branches = run_homeostasis_controls(
        palimpsest_config(),
        maturation_ticks=20,
        response_ticks=8,
        output_dir=tmp_path,
        ambient_shift=0.1,
        sample_every=2,
    )
    assert set(branches) == {"dynamic", "no_matrix", "frozen", "random"}
    for name in branches:
        path = tmp_path / f"{name}.csv"
        assert path.exists()
        with path.open(encoding="utf-8") as handle:
            assert len(list(csv.DictReader(handle))) == 5
    assert (tmp_path / "metadata.json").exists()
    with (tmp_path / "metadata.json").open(encoding="utf-8") as handle:
        metadata = json.load(handle)
    assert "breach_x" in metadata and "breach_y" in metadata
    assert np.all(branches["no_matrix"].state.matrix == 0)


def test_palimpsest_preset_forms_a_measurable_enclosure():
    config = load_config("presets/palimpsest.json")
    simulation = Simulation(config)
    simulation.step(1000)
    interior = enclosed_mask(simulation.state.matrix, config.palimpsest.enclosure_threshold)
    assert np.count_nonzero(interior) >= 25
