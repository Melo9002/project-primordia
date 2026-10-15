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


def variable_diffusion(field: Array, diffusivity: Array, boundary: str = "periodic") -> Array:
    """Conservative divergence of flux for a spatially varying diffusivity."""
    if boundary == "periodic":
        result = np.zeros_like(field)
        for axis in (0, 1):
            neighbor = np.roll(field, -1, axis)
            face_d = 0.5 * (diffusivity + np.roll(diffusivity, -1, axis))
            flux = face_d * (neighbor - field)
            result += flux - np.roll(flux, 1, axis)
        return result
    if boundary == "reflective":
        result = np.zeros_like(field)
        vertical_d = 0.5 * (diffusivity[:-1, :] + diffusivity[1:, :])
        vertical_flux = vertical_d * (field[1:, :] - field[:-1, :])
        result[:-1, :] += vertical_flux
        result[1:, :] -= vertical_flux
        horizontal_d = 0.5 * (diffusivity[:, :-1] + diffusivity[:, 1:])
        horizontal_flux = horizontal_d * (field[:, 1:] - field[:, :-1])
        result[:, :-1] += horizontal_flux
        result[:, 1:] -= horizontal_flux
        return result
    raise ValueError(f"unsupported boundary: {boundary}")
