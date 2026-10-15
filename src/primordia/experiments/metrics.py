"""Measurements independent of rendering."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
import numpy as np
from primordia.simulation.state import WorldState


@dataclass(frozen=True, slots=True)
class Observation:
    tick: int
    mean_temperature: float
    temperature_variance: float
    total_a: float
    total_b: float
    total_resource: float
    spatial_variability_b: float


def measure(state: WorldState) -> Observation:
    return Observation(state.tick, float(np.mean(state.temperature)), float(np.var(state.temperature)), float(np.sum(state.a)), float(np.sum(state.b)), float(np.sum(state.resource)), float(np.var(state.b)))


class Observer:
    def __init__(self) -> None:
        self.records: list[Observation] = []

    def record(self, state: WorldState) -> Observation:
        observation = measure(state)
        self.records.append(observation)
        return observation

    def export_csv(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(Observation.__dataclass_fields__))
            writer.writeheader()
            writer.writerows(asdict(record) for record in self.records)
