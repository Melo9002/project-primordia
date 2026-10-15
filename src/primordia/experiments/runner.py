"""Headless experiment execution and paired baseline/disturbance runs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import numpy as np
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


def _observe_existing(simulation: Simulation, ticks: int, path: Path, sample_every: int) -> None:
    observer = Observer(simulation.config.palimpsest.enclosure_threshold)
    observer.record(simulation.state)
    for _ in range(ticks):
        simulation.step()
        if simulation.state.tick % sample_every == 0:
            observer.record(simulation.state)
    observer.export_csv(path)


def run_homeostasis_controls(
    config: WorldConfig,
    maturation_ticks: int,
    response_ticks: int,
    output_dir: str | Path,
    *,
    ambient_shift: float = 0.20,
    breach_radius: int = 0,
    sample_every: int = 10,
) -> dict[str, Simulation]:
    """Branch one mature world into four matched transport controls."""
    if not config.palimpsest.enabled:
        raise ValueError("homeostasis controls require palimpsest.enabled")
    mature = Simulation(config)
    mature.step(maturation_ticks)
    branches = {name: mature.clone() for name in ("dynamic", "no_matrix", "frozen", "random")}
    branches["no_matrix"].state.matrix.fill(0.0)
    branches["no_matrix"].config.palimpsest.enabled = False
    branches["frozen"].config.palimpsest.matrix_dynamic = False
    shuffled = branches["random"].state.matrix.ravel().copy()
    np.random.default_rng(config.seed + 7919).shuffle(shuffled)
    branches["random"].state.matrix[:] = shuffled.reshape(branches["random"].state.matrix.shape)
    branches["random"].config.palimpsest.matrix_dynamic = False

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    breach_x = breach_y = None
    if breach_radius:
        candidates = np.argwhere(mature.state.matrix >= config.palimpsest.enclosure_threshold)
        if candidates.size:
            center = np.array((config.height / 2, config.width / 2))
            breach_y, breach_x = candidates[np.argmin(np.sum((candidates - center) ** 2, axis=1))]
            breach_y, breach_x = int(breach_y), int(breach_x)
    for name, simulation in branches.items():
        simulation.config.environment.ambient_temperature += ambient_shift
        if breach_x is not None and name != "no_matrix":
            simulation.disturb(breach_x, breach_y, breach_radius, "M", -1.0)
        _observe_existing(simulation, response_ticks, destination / f"{name}.csv", sample_every)
        simulation.state.save(destination / f"{name}_final.npz")
    metadata = {
        "seed": config.seed,
        "maturation_ticks": maturation_ticks,
        "response_ticks": response_ticks,
        "ambient_shift": ambient_shift,
        "breach_radius": breach_radius,
        "breach_x": breach_x,
        "breach_y": breach_y,
        "controls": ["dynamic", "no_matrix", "frozen", "random"],
        "interpretation": "Compare trajectories; recovery alone is not proof of homeostasis.",
    }
    with (destination / "metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
        handle.write("\n")
    return branches
