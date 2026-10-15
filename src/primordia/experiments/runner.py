"""Headless experiment execution and paired baseline/disturbance runs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from primordia.config import WorldConfig
from primordia.simulation.engine import Simulation
from .metrics import Observer


@dataclass(slots=True)
class Disturbance:
    tick: int
    field: str = "T"
    amount: float = 0.7
    x: int | None = None
    y: int | None = None
    radius: int = 8


def run_experiment(config: WorldConfig, ticks: int, csv_path: str | Path, *, sample_every: int = 1, disturbance: Disturbance | None = None, snapshot_path: str | Path | None = None) -> Simulation:
    if ticks < 0 or sample_every < 1:
        raise ValueError("ticks must be nonnegative and sample_every must be positive")
    simulation, observer = Simulation(config), Observer()
    observer.record(simulation.state)
    for _ in range(ticks):
        if disturbance and simulation.state.tick == disturbance.tick:
            simulation.disturb(disturbance.x if disturbance.x is not None else config.width // 2, disturbance.y if disturbance.y is not None else config.height // 2, disturbance.radius, disturbance.field, disturbance.amount)
        simulation.step()
        if simulation.state.tick % sample_every == 0:
            observer.record(simulation.state)
    observer.export_csv(csv_path)
    if snapshot_path:
        simulation.state.save(snapshot_path)
    return simulation


def run_pair(config: WorldConfig, ticks: int, output_dir: str | Path, disturbance: Disturbance, sample_every: int = 1) -> None:
    destination = Path(output_dir)
    run_experiment(config, ticks, destination / "baseline.csv", sample_every=sample_every)
    run_experiment(config, ticks, destination / "disturbed.csv", sample_every=sample_every, disturbance=disturbance, snapshot_path=destination / "disturbed_final.npz")
