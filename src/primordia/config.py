"""Configuration models and JSON preset loading."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
import json
from typing import Any, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class InitialConfig:
    a: float = 1.0
    b: float = 0.0
    resource: float = 1.0
    temperature: float = 1.0
    waste: float = 0.0
    matrix: float = 0.0
    noise: float = 0.015
    seed_radius: int = 8
    seed_b: float = 0.85


@dataclass(slots=True)
class ReactionConfig:
    feed: float = 0.0367
    kill: float = 0.0649
    resource_half_saturation: float = 0.20
    temperature_sensitivity: float = 1.2
    reaction_heat: float = 0.012
    resource_cost: float = 0.55


@dataclass(slots=True)
class DiffusionConfig:
    a: float = 0.16
    b: float = 0.08
    resource: float = 0.10
    temperature: float = 0.12


@dataclass(slots=True)
class EnvironmentConfig:
    ambient_temperature: float = 1.0
    thermal_exchange: float = 0.015
    external_heating: float = 0.0
    resource_supply: float = 0.018
    resource_removal: float = 0.002
    resource_target: float = 1.0
    exchange_mode: str = "uniform"


@dataclass(slots=True)
class PalimpsestConfig:
    enabled: bool = False
    matrix_dynamic: bool = True
    waste_production: float = 0.35
    waste_decay: float = 0.012
    waste_diffusion: float = 0.11
    matrix_deposition: float = 1.2
    matrix_erosion: float = 0.0015
    matrix_dissolution: float = 0.006
    permeability_a: float = 2.0
    permeability_b: float = 4.0
    permeability_resource: float = 1.2
    permeability_temperature: float = 2.5
    permeability_waste: float = 1.0
    enclosure_threshold: float = 0.28


@dataclass(slots=True)
class WorldConfig:
    width: int = 128
    height: int = 128
    dt: float = 0.5
    seed: int = 7
    boundary: str = "periodic"
    dtype: str = "float64"
    initial: InitialConfig = field(default_factory=InitialConfig)
    reaction: ReactionConfig = field(default_factory=ReactionConfig)
    diffusion: DiffusionConfig = field(default_factory=DiffusionConfig)
    environment: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    palimpsest: PalimpsestConfig = field(default_factory=PalimpsestConfig)

    def validate(self) -> None:
        if self.width < 8 or self.height < 8:
            raise ValueError("world dimensions must be at least 8 x 8")
        if not 0 < self.dt <= 1:
            raise ValueError("dt must be in (0, 1]")
        if self.boundary not in {"periodic", "reflective"}:
            raise ValueError("boundary must be periodic or reflective")
        if self.environment.exchange_mode not in {"uniform", "boundary"}:
            raise ValueError("exchange_mode must be uniform or boundary")
        for group in (self.diffusion, self.environment, self.reaction, self.palimpsest):
            for item in fields(group):
                value = getattr(group, item.name)
                if isinstance(value, (int, float)) and not isinstance(value, bool) and "heating" not in item.name and value < 0:
                    raise ValueError(f"{item.name} must be nonnegative")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorldConfig":
        known = {item.name for item in fields(cls)}
        extra = set(data) - known
        if extra:
            raise ValueError(f"unknown configuration keys: {sorted(extra)}")
        flat = {k: v for k, v in data.items() if k not in {"initial", "reaction", "diffusion", "environment", "palimpsest"}}
        config = cls(
            **flat,
            initial=_load_group(InitialConfig, data.get("initial", {})),
            reaction=_load_group(ReactionConfig, data.get("reaction", {})),
            diffusion=_load_group(DiffusionConfig, data.get("diffusion", {})),
            environment=_load_group(EnvironmentConfig, data.get("environment", {})),
            palimpsest=_load_group(PalimpsestConfig, data.get("palimpsest", {})),
        )
        config.validate()
        return config


def _load_group(group_type: type[T], data: dict[str, Any]) -> T:
    allowed = {item.name for item in fields(group_type)}
    extra = set(data) - allowed
    if extra:
        raise ValueError(f"unknown {group_type.__name__} keys: {sorted(extra)}")
    return group_type(**data)


def load_config(path: str | Path) -> WorldConfig:
    with Path(path).open(encoding="utf-8") as handle:
        return WorldConfig.from_dict(json.load(handle))


def save_config(config: WorldConfig, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(config.to_dict(), handle, indent=2)
        handle.write("\n")
