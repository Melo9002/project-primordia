"""Explicit environmental sources and sinks."""

from __future__ import annotations

from primordia.config import EnvironmentConfig
from .state import Array


def environment_terms(resource: Array, temperature: Array, config: EnvironmentConfig) -> tuple[Array, Array]:
    supply = config.resource_supply * (config.resource_target - resource)
    removal = config.resource_removal * resource
    thermal = config.thermal_exchange * (config.ambient_temperature - temperature) + config.external_heating
    return supply - removal, thermal
