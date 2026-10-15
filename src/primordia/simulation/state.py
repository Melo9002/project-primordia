"""Array-backed simulation state."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.floating]


@dataclass(slots=True)
class WorldState:
    a: Array
    b: Array
    resource: Array
    temperature: Array
    waste: Array
    matrix: Array
    tick: int = 0

    def copy(self) -> "WorldState":
        return WorldState(self.a.copy(), self.b.copy(), self.resource.copy(), self.temperature.copy(), self.waste.copy(), self.matrix.copy(), self.tick)

    def arrays(self) -> tuple[Array, Array, Array, Array, Array, Array]:
        return self.a, self.b, self.resource, self.temperature, self.waste, self.matrix

    def validate(self) -> None:
        if len({array.shape for array in self.arrays()}) != 1:
            raise ValueError("all fields must have the same shape")
        if not all(np.isfinite(array).all() for array in self.arrays()):
            raise FloatingPointError("world contains non-finite values")
        if any((array < 0).any() for array in (self.a, self.b, self.resource, self.waste, self.matrix)):
            raise FloatingPointError("concentrations and structure fields must be nonnegative")

    def save(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(destination, a=self.a, b=self.b, resource=self.resource, temperature=self.temperature, waste=self.waste, matrix=self.matrix, tick=np.asarray(self.tick))

    @classmethod
    def load(cls, path: str | Path) -> "WorldState":
        with np.load(path) as data:
            shape = data["a"].shape
            waste = data["waste"].copy() if "waste" in data else np.zeros(shape)
            matrix = data["matrix"].copy() if "matrix" in data else np.zeros(shape)
            state = cls(data["a"].copy(), data["b"].copy(), data["resource"].copy(), data["temperature"].copy(), waste, matrix, int(data["tick"]))
        state.validate()
        return state
