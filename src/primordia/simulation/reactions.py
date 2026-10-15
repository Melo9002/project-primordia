"""Local reaction terms for the modified Gray-Scott universe."""

from __future__ import annotations

import numpy as np
from primordia.config import ReactionConfig
from .state import Array


def reaction_terms(a: Array, b: Array, resource: Array, temperature: Array, config: ReactionConfig) -> tuple[Array, Array, Array, Array]:
    resource_factor = resource / (config.resource_half_saturation + resource)
    temperature_factor = np.exp(np.clip(config.temperature_sensitivity * (temperature - 1.0), -3.0, 3.0))
    conversion = a * b * b * resource_factor * temperature_factor
    return -conversion + config.feed * (1.0 - a), conversion - (config.feed + config.kill) * b, -config.resource_cost * conversion, config.reaction_heat * conversion
