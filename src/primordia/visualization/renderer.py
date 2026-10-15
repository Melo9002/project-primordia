"""Scientific color maps, legends, and compact metric plots."""

from __future__ import annotations

from collections.abc import Sequence
import numpy as np
import pygame
from primordia.simulation.state import WorldState

PANEL = (13, 21, 31)
PANEL_RAISED = (18, 29, 41)
BORDER = (43, 63, 78)
TEXT = (218, 229, 235)
MUTED = (126, 151, 166)
ACCENT = (79, 224, 196)

PALETTES: dict[str, tuple[tuple[int, int, int], ...]] = {
    "A": ((7, 16, 31), (21, 71, 109), (40, 156, 175), (189, 238, 218)),
    "B": ((10, 12, 29), (58, 31, 111), (193, 62, 166), (255, 195, 98)),
    "R": ((10, 19, 25), (21, 76, 71), (50, 166, 116), (210, 238, 162)),
    "T": ((18, 27, 65), (48, 122, 181), (239, 215, 127), (237, 77, 87)),
    "W": ((9, 15, 28), (54, 39, 100), (177, 80, 164), (243, 181, 107)),
    "M": ((7, 15, 20), (53, 64, 66), (149, 119, 89), (236, 221, 181)),
}


def _normalize(data: np.ndarray, low: float | None = None, high: float | None = None, gamma: float = 1.0) -> np.ndarray:
    lo = float(np.percentile(data, 1)) if low is None else low
    hi = float(np.percentile(data, 99)) if high is None else high
    normalized = np.clip((data - lo) / max(hi - lo, 1e-12), 0.0, 1.0)
    return normalized ** gamma


def _palette(values: np.ndarray, colors: Sequence[tuple[int, int, int]]) -> np.ndarray:
    """Linearly interpolate an arbitrary RGB palette."""
    scaled = np.clip(values, 0.0, 1.0) * (len(colors) - 1)
    left = np.floor(scaled).astype(np.int16)
    right = np.minimum(left + 1, len(colors) - 1)
    fraction = (scaled - left)[..., None]
    table = np.asarray(colors, dtype=np.float64)
    return table[left] * (1.0 - fraction) + table[right] * fraction


def _gradient_strength(field: np.ndarray) -> np.ndarray:
    dx = np.roll(field, -1, 1) - np.roll(field, 1, 1)
    dy = np.roll(field, -1, 0) - np.roll(field, 1, 0)
    return _normalize(np.hypot(dx, dy), gamma=0.65)


def field_rgb(state: WorldState, mode: str) -> np.ndarray:
    """Map actual field values to an RGB image with perceptual contrast."""
    if mode in PALETTES:
        ranges = {"A": (0.0, 1.1), "B": (0.0, 0.55), "R": (0.75, 1.05), "T": (0.96, 1.06), "W": (0.0, 0.25), "M": (0.0, 0.5)}
        source = {"A": state.a, "B": state.b, "R": state.resource, "T": state.temperature, "W": state.waste, "M": state.matrix}[mode]
        low, high = ranges[mode]
        return np.clip(_palette(_normalize(source, low, high, 0.82), PALETTES[mode]), 0, 255).astype(np.uint8)

    # Composite: chemistry controls hue/luminance while temperature adds a
    # restrained blue/orange deviation. A gradient highlight reveals fronts.
    b = _normalize(state.b, 0.0, 0.45, 0.72)
    resource = _normalize(state.resource, 0.78, 1.02, 0.9)
    heat = np.clip((state.temperature - 1.0) / 0.045, -1.0, 1.0)
    chemistry = _palette(b, ((7, 18, 35), (17, 99, 111), (77, 213, 165), (245, 190, 91)))
    illumination = (0.58 + 0.42 * resource)[..., None]
    rgb = chemistry * illumination
    rgb += np.maximum(heat, 0.0)[..., None] * np.array((58.0, 10.0, -20.0))
    rgb += np.maximum(-heat, 0.0)[..., None] * np.array((-12.0, 13.0, 48.0))
    waste = _normalize(state.waste, 0.0, 0.22)[..., None]
    rgb += waste * np.array((22.0, -8.0, 24.0))
    matrix = _normalize(state.matrix, 0.0, 0.45)[..., None]
    rgb = rgb * (1.0 - 0.48 * matrix) + matrix * np.array((198.0, 167.0, 119.0)) * 0.48
    edge = _gradient_strength(state.b)[..., None]
    rgb += edge * np.array((25.0, 33.0, 35.0))
    return np.clip(rgb, 0, 255).astype(np.uint8)


def draw_world(surface: pygame.Surface, state: WorldState, mode: str, rect: pygame.Rect) -> None:
    pixels = np.transpose(field_rgb(state, mode), (1, 0, 2))
    raw = pygame.surfarray.make_surface(pixels)
    surface.blit(pygame.transform.smoothscale(raw, rect.size), rect)


def draw_color_legend(surface: pygame.Surface, mode: str, rect: pygame.Rect, font: pygame.font.Font) -> None:
    palette = PALETTES.get(mode, ((7, 18, 35), (17, 99, 111), (77, 213, 165), (245, 190, 91)))
    for x in range(rect.width):
        value = np.asarray([[x / max(rect.width - 1, 1)]])
        color = tuple(_palette(value, palette)[0, 0].astype(int))
        pygame.draw.line(surface, color, (rect.x + x, rect.y), (rect.x + x, rect.bottom))
    pygame.draw.rect(surface, (93, 119, 133), rect, 1, border_radius=3)
    labels = {"COMPOSITE": ("low activity", "structured activity"), "A": ("0.0", "1.1"), "B": ("0.0", "0.55"), "R": ("0.75", "1.05"), "T": ("0.96", "1.06"), "W": ("0.0", "0.25"), "M": ("0.0", "0.5")}
    left, right = labels[mode]
    surface.blit(font.render(left, True, MUTED), (rect.x, rect.bottom + 4))
    right_image = font.render(right, True, MUTED)
    surface.blit(right_image, (rect.right - right_image.get_width(), rect.bottom + 4))


def draw_series(
    surface: pygame.Surface,
    samples: list[tuple[int, float]],
    rect: pygame.Rect,
    color: tuple[int, int, int],
    label: str,
    font: pygame.font.Font,
    value_font: pygame.font.Font,
    event_ticks: Sequence[int] = (),
) -> None:
    pygame.draw.rect(surface, PANEL_RAISED, rect, border_radius=10)
    pygame.draw.rect(surface, BORDER, rect, 1, border_radius=10)
    surface.blit(font.render(label.upper(), True, MUTED), (rect.x + 12, rect.y + 10))
    if not samples:
        return
    recent = samples[-240:]
    ticks = [item[0] for item in recent]
    values = [item[1] for item in recent]
    value_image = value_font.render(f"{values[-1]:.5g}", True, TEXT)
    surface.blit(value_image, (rect.right - value_image.get_width() - 12, rect.y + 7))
    plot = pygame.Rect(rect.x + 12, rect.y + 37, rect.width - 24, rect.height - 52)
    for fraction in (0.0, 0.5, 1.0):
        y = round(plot.y + plot.height * fraction)
        pygame.draw.line(surface, (29, 45, 58), (plot.x, y), (plot.right, y), 1)
    low, high = min(values), max(values)
    span = max(high - low, 1e-12)
    first_tick, last_tick = ticks[0], max(ticks[-1], ticks[0] + 1)
    for tick in event_ticks:
        if first_tick <= tick <= last_tick:
            x = plot.x + (tick - first_tick) / (last_tick - first_tick) * plot.width
            pygame.draw.line(surface, (238, 184, 81), (x, plot.y), (x, plot.bottom), 1)
    points = [
        (plot.x + (tick - first_tick) / (last_tick - first_tick) * plot.width,
         plot.bottom - (value - low) / span * plot.height)
        for tick, value in recent
    ]
    if len(points) > 1:
        pygame.draw.aalines(surface, color, False, points)
    pygame.draw.circle(surface, color, (round(points[-1][0]), round(points[-1][1])), 3)
    range_text = font.render(f"{low:.3g} — {high:.3g}", True, MUTED)
    surface.blit(range_text, (plot.x, rect.bottom - 14))
