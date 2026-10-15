"""Discrete Laplacians for supported boundaries."""

from __future__ import annotations

import numpy as np
from .state import Array


def laplacian(field: Array, boundary: str = "periodic") -> Array:
    """Return the five-point finite-difference Laplacian with unit spacing."""
    if boundary == "periodic":
        return np.roll(field, 1, 0) + np.roll(field, -1, 0) + np.roll(field, 1, 1) + np.roll(field, -1, 1) - 4.0 * field
    if boundary == "reflective":
        padded = np.pad(field, 1, mode="edge")
        return padded[:-2, 1:-1] + padded[2:, 1:-1] + padded[1:-1, :-2] + padded[1:-1, 2:] - 4.0 * field
    raise ValueError(f"unsupported boundary: {boundary}")
