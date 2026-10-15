import csv
import numpy as np

from primordia.config import InitialConfig, WorldConfig
from primordia.experiments.runner import Disturbance, run_experiment, run_pair
from primordia.simulation.state import WorldState


def config() -> WorldConfig:
    return WorldConfig(width=24, height=24, seed=12, initial=InitialConfig(seed_radius=3))


def test_headless_run_writes_csv_and_snapshot(tmp_path):
    csv_path, snapshot = tmp_path / "run.csv", tmp_path / "state.npz"
    simulation = run_experiment(config(), 20, csv_path, sample_every=5, snapshot_path=snapshot)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert [int(row["tick"]) for row in rows] == [0, 5, 10, 15, 20]
    assert simulation.state.tick == 20
    loaded = WorldState.load(snapshot)
    np.testing.assert_array_equal(loaded.b, simulation.state.b)


def test_paired_experiment_uses_same_baseline_but_disturbance_changes_result(tmp_path):
    run_pair(config(), 16, tmp_path, Disturbance(tick=5, field="T", amount=0.8, radius=3), sample_every=1)
    with (tmp_path / "baseline.csv").open(encoding="utf-8") as handle:
        baseline = list(csv.DictReader(handle))
    with (tmp_path / "disturbed.csv").open(encoding="utf-8") as handle:
        disturbed = list(csv.DictReader(handle))
    assert baseline[0] == disturbed[0]
    assert baseline[-1]["mean_temperature"] != disturbed[-1]["mean_temperature"]


def test_headless_import_does_not_initialize_pygame():
    import sys
    assert "pygame" not in sys.modules
