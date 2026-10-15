"""Field color maps and small scientific plots."""

from __future__ import annotations

import numpy as np
import pygame
from primordia.simulation.state import WorldState


def _normalize(data: np.ndarray, low: float | None = None, high: float | None = None) -> np.ndarray:
    lo = float(np.percentile(data, 1)) if low is None else low
    hi = float(np.percentile(data, 99)) if high is None else high
    return np.clip((data - lo) / max(hi - lo, 1e-12), 0.0, 1.0)


def field_rgb(state: WorldState, mode: str) -> np.ndarray:
    """Map an actual world field to RGB; shape is (height, width, 3)."""
    if mode == "A":
        x = _normalize(state.a, 0.0, 1.1)
        return np.stack((30 + 40*x, 45 + 130*x, 70 + 180*x), axis=-1).astype(np.uint8)
    if mode == "B":
        x = _normalize(state.b, 0.0, 0.8)
        return np.stack((20 + 230*x, 20 + 110*x, 40 + 190*x), axis=-1).astype(np.uint8)
    if mode == "R":
        x = _normalize(state.resource, 0.0, 1.2)
        return np.stack((20 + 80*x, 35 + 200*x, 30 + 70*x), axis=-1).astype(np.uint8)
    if mode == "T":
        x = _normalize(state.temperature, 0.7, 1.3)
        return np.stack((30 + 225*x, 60 + 80*(1-abs(2*x-1)), 220 - 200*x), axis=-1).astype(np.uint8)
    b = _normalize(state.b, 0.0, 0.75)
    r = _normalize(state.resource, 0.0, 1.2)
    t = _normalize(state.temperature, 0.8, 1.2)
    return np.stack((35 + 200*b, 25 + 190*r, 45 + 170*(1-t)), axis=-1).astype(np.uint8)


def draw_world(surface: pygame.Surface, state: WorldState, mode: str, rect: pygame.Rect) -> None:
    pixels = np.transpose(field_rgb(state, mode), (1, 0, 2))
    raw = pygame.surfarray.make_surface(pixels)
    surface.blit(pygame.transform.scale(raw, rect.size), rect)


def draw_series(surface: pygame.Surface, values: list[float], rect: pygame.Rect, color: tuple[int, int, int], label: str, font: pygame.font.Font) -> None:
    pygame.draw.rect(surface, (14, 20, 29), rect, border_radius=5)
    pygame.draw.rect(surface, (52, 68, 82), rect, 1, border_radius=5)
    surface.blit(font.render(label, True, (170, 188, 202)), (rect.x + 8, rect.y + 5))
    if len(values) < 2:
        return
    recent = values[-240:]
    low, high = min(recent), max(recent)
    span = max(high - low, 1e-12)
    points = [
        (rect.x + i * (rect.width - 12) / max(len(recent) - 1, 1) + 6,
         rect.bottom - 8 - (value - low) / span * (rect.height - 28))
        for i, value in enumerate(recent)
    ]
    pygame.draw.lines(surface, color, False, points, 2)
