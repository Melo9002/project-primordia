"""Deterministic fixed-step simulation engine."""

from __future__ import annotations

from copy import deepcopy
import numpy as np

from primordia.config import WorldConfig
from .diffusion import laplacian, variable_diffusion
from .environment import environment_terms
from .reactions import reaction_terms
from .state import WorldState


class Simulation:
    """Own a world and advance every field from one consistent previous state."""

    def __init__(self, config: WorldConfig):
        config.validate()
        self.config = deepcopy(config)
        self._initial_config = deepcopy(config)
        self.rng = np.random.default_rng(config.seed)
        self.state = self._initialize()

    def _initialize(self) -> WorldState:
        cfg = self.config
        shape = (cfg.height, cfg.width)
        dtype = np.dtype(cfg.dtype)
        a = np.full(shape, cfg.initial.a, dtype=dtype)
        b = np.full(shape, cfg.initial.b, dtype=dtype)
        resource = np.full(shape, cfg.initial.resource, dtype=dtype)
        temperature = np.full(shape, cfg.initial.temperature, dtype=dtype)
        waste = np.full(shape, cfg.initial.waste, dtype=dtype)
        matrix = np.full(shape, cfg.initial.matrix, dtype=dtype)
        noise = cfg.initial.noise
        if noise:
            a += self.rng.normal(0.0, noise, shape)
            b += self.rng.normal(0.0, noise * 0.35, shape)
            resource += self.rng.normal(0.0, noise * 0.25, shape)
            temperature += self.rng.normal(0.0, noise * 0.08, shape)
        radius = max(1, min(cfg.initial.seed_radius, min(shape) // 3))
        cy, cx = shape[0] // 2, shape[1] // 2
        b[cy-radius:cy+radius, cx-radius:cx+radius] = cfg.initial.seed_b
        a[cy-radius:cy+radius, cx-radius:cx+radius] *= 0.45
        state = WorldState(
            np.clip(a, 0.0, 1.5),
            np.clip(b, 0.0, 1.5),
            np.clip(resource, 0.0, 2.0),
            np.clip(temperature, 0.0, 3.0),
            np.clip(waste, 0.0, 2.0),
            np.clip(matrix, 0.0, 1.0),
        )
        state.validate()
        return state

    def reset(self) -> None:
        self.config = deepcopy(self._initial_config)
        self.rng = np.random.default_rng(self.config.seed)
        self.state = self._initialize()

    def clone(self) -> "Simulation":
        """Copy a running world so controlled branches share an exact history."""
        duplicate = object.__new__(Simulation)
        duplicate.config = deepcopy(self.config)
        duplicate._initial_config = deepcopy(self._initial_config)
        duplicate.rng = np.random.default_rng()
        duplicate.rng.bit_generator.state = deepcopy(self.rng.bit_generator.state)
        duplicate.state = self.state.copy()
        return duplicate

    def step(self, count: int = 1) -> WorldState:
        if count < 0:
            raise ValueError("count must be nonnegative")
        for _ in range(count):
            self._step_once()
        return self.state

    def _step_once(self) -> None:
        c, old = self.config, self.state
        da, db, dr, dtemp, conversion = reaction_terms(old.a, old.b, old.resource, old.temperature, c.reaction)
        env_r, env_t = environment_terms(old.resource, old.temperature, c.environment)
        p = c.palimpsest
        if p.enabled:
            da += variable_diffusion(old.a, c.diffusion.a * np.exp(-p.permeability_a * old.matrix), c.boundary)
            db += variable_diffusion(old.b, c.diffusion.b * np.exp(-p.permeability_b * old.matrix), c.boundary)
            dr += env_r + variable_diffusion(old.resource, c.diffusion.resource * np.exp(-p.permeability_resource * old.matrix), c.boundary)
            dtemp += env_t + variable_diffusion(old.temperature, c.diffusion.temperature * np.exp(-p.permeability_temperature * old.matrix), c.boundary)
            dwaste = p.waste_production * conversion - p.waste_decay * old.waste
            dwaste += variable_diffusion(old.waste, p.waste_diffusion * np.exp(-p.permeability_waste * old.matrix), c.boundary)
            gradient_x = 0.5 * (np.roll(old.b, -1, 1) - np.roll(old.b, 1, 1))
            gradient_y = 0.5 * (np.roll(old.b, -1, 0) - np.roll(old.b, 1, 0))
            reaction_front = np.hypot(gradient_x, gradient_y)
            dmatrix = p.matrix_deposition * old.waste * (reaction_front + 0.02 * old.b)
            dmatrix -= p.matrix_erosion * old.matrix + p.matrix_dissolution * old.waste * old.matrix
            if not p.matrix_dynamic:
                dmatrix = np.zeros_like(old.matrix)
        else:
            da += c.diffusion.a * laplacian(old.a, c.boundary)
            db += c.diffusion.b * laplacian(old.b, c.boundary)
            dr += env_r + c.diffusion.resource * laplacian(old.resource, c.boundary)
            dtemp += env_t + c.diffusion.temperature * laplacian(old.temperature, c.boundary)
            dwaste = np.zeros_like(old.waste)
            dmatrix = np.zeros_like(old.matrix)
        # These safety clamps can create or destroy quantity after Euler overshoot.
        self.state = WorldState(
            np.clip(old.a + c.dt * da, 0.0, 1.5),
            np.clip(old.b + c.dt * db, 0.0, 1.5),
            np.clip(old.resource + c.dt * dr, 0.0, 2.0),
            np.clip(old.temperature + c.dt * dtemp, 0.0, 3.0),
            np.clip(old.waste + c.dt * dwaste, 0.0, 2.0),
            np.clip(old.matrix + c.dt * dmatrix, 0.0, 1.0),
            old.tick + 1,
        )
        self.state.validate()

    def disturb(self, x: int, y: int, radius: int, field: str, amount: float) -> None:
        yy, xx = np.ogrid[:self.config.height, :self.config.width]
        if self.config.boundary == "periodic":
            dx = np.minimum(abs(xx - x), self.config.width - abs(xx - x))
            dy = np.minimum(abs(yy - y), self.config.height - abs(yy - y))
        else:
            dx, dy = abs(xx - x), abs(yy - y)
        mask = dx * dx + dy * dy <= radius * radius
        name = {"A": "a", "B": "b", "R": "resource", "T": "temperature", "W": "waste", "M": "matrix"}.get(field.upper(), field.lower())
        array = getattr(self.state, name)
        array[mask] += amount
        upper = 3.0 if name == "temperature" else (1.0 if name == "matrix" else (2.0 if name in {"resource", "waste"} else 1.5))
        np.clip(array, 0.0, upper, out=array)
        self.state.validate()
