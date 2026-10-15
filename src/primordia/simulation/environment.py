"""Explicit environmental sources and sinks."""

from __future__ import annotations

import numpy as np
from primordia.config import EnvironmentConfig
from .state import Array


def environment_terms(resource: Array, temperature: Array, config: EnvironmentConfig) -> tuple[Array, Array]:
    supply = config.resource_supply * (config.resource_target - resource)
    removal = config.resource_removal * resource
    thermal = config.thermal_exchange * (config.ambient_temperature - temperature) + config.external_heating
    resource_term, thermal_term = supply - removal, thermal
    if config.exchange_mode == "boundary":
        mask = np.zeros_like(resource)
        mask[[0, -1], :] = 1.0
        mask[:, [0, -1]] = 1.0
        resource_term = resource_term * mask
        thermal_term = thermal_term * mask
    return resource_term, thermal_term
