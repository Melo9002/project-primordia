"""Measurements independent of rendering."""

from __future__ import annotations

from collections import deque
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
    total_waste: float
    total_matrix: float
    spatial_variability_b: float
    spatial_variability_matrix: float
    enclosed_cells: int
    interior_temperature: float
    exterior_temperature: float
    interior_resource: float


def enclosed_mask(matrix: np.ndarray, threshold: float = 0.28) -> np.ndarray:
    """Return non-barrier cells disconnected from the rectangular boundary."""
    barrier = matrix >= threshold
    reachable = np.zeros(matrix.shape, dtype=bool)
    queue: deque[tuple[int, int]] = deque()
    height, width = matrix.shape
    for x in range(width):
        if not barrier[0, x]:
            queue.append((0, x))
        if not barrier[-1, x]:
            queue.append((height - 1, x))
    for y in range(height):
        if not barrier[y, 0]:
            queue.append((y, 0))
        if not barrier[y, -1]:
            queue.append((y, width - 1))
    while queue:
        y, x = queue.popleft()
        if reachable[y, x]:
            continue
        reachable[y, x] = True
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < height and 0 <= nx < width and not barrier[ny, nx] and not reachable[ny, nx]:
                queue.append((ny, nx))
    return ~barrier & ~reachable


def measure(state: WorldState, enclosure_threshold: float = 0.28) -> Observation:
    interior = enclosed_mask(state.matrix, enclosure_threshold)
    exterior = ~interior & (state.matrix < enclosure_threshold)
    enclosed = int(np.count_nonzero(interior))
    interior_temperature = float(np.mean(state.temperature[interior])) if enclosed else float("nan")
    interior_resource = float(np.mean(state.resource[interior])) if enclosed else float("nan")
    exterior_temperature = float(np.mean(state.temperature[exterior])) if np.any(exterior) else float("nan")
    return Observation(
        state.tick,
        float(np.mean(state.temperature)),
        float(np.var(state.temperature)),
        float(np.sum(state.a)),
        float(np.sum(state.b)),
        float(np.sum(state.resource)),
        float(np.sum(state.waste)),
        float(np.sum(state.matrix)),
        float(np.var(state.b)),
        float(np.var(state.matrix)),
        enclosed,
        interior_temperature,
        exterior_temperature,
        interior_resource,
    )


class Observer:
    def __init__(self, enclosure_threshold: float = 0.28) -> None:
        self.records: list[Observation] = []
        self.enclosure_threshold = enclosure_threshold

    def record(self, state: WorldState) -> Observation:
        observation = measure(state, self.enclosure_threshold)
        self.records.append(observation)
        return observation

    def export_csv(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(Observation.__dataclass_fields__))
            writer.writeheader()
            writer.writerows(asdict(record) for record in self.records)
