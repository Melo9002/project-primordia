"""Interactive PRIMORDIA laboratory."""

from __future__ import annotations

from pathlib import Path
import pygame

from primordia.config import WorldConfig, save_config
from primordia.experiments.metrics import Observer, measure
from primordia.simulation.engine import Simulation
from .renderer import (
    ACCENT,
    BORDER,
    MUTED,
    PANEL,
    PANEL_RAISED,
    TEXT,
    draw_color_legend,
    draw_series,
    draw_world,
)

WINDOW = (1280, 840)
WORLD_RECT = pygame.Rect(24, 96, 720, 720)
SIDEBAR_X = 772
SIDEBAR_W = 484
MODES = ["COMPOSITE", "A", "B", "R", "T"]
TOOLS = [
    ("HEAT", "T", 0.45, (244, 105, 88)),
    ("COOL", "T", -0.45, (78, 164, 230)),
    ("ADD B", "B", 0.35, (208, 100, 237)),
    ("REMOVE B", "B", -0.35, (145, 112, 192)),
    ("ADD R", "R", 0.45, (91, 215, 146)),
]


def _text(surface: pygame.Surface, font: pygame.font.Font, value: str, x: int, y: int, color=TEXT) -> pygame.Rect:
    image = font.render(value, True, color)
    rect = image.get_rect(topleft=(x, y))
    surface.blit(image, rect)
    return rect


def _pill(surface: pygame.Surface, font: pygame.font.Font, text: str, rect: pygame.Rect, color: tuple[int, int, int], active: bool = False) -> None:
    fill = tuple(min(255, channel + 7) for channel in PANEL_RAISED) if not active else tuple(max(0, int(channel * 0.22)) for channel in color)
    pygame.draw.rect(surface, fill, rect, border_radius=rect.height // 2)
    pygame.draw.rect(surface, color if active else BORDER, rect, 1, border_radius=rect.height // 2)
    image = font.render(text, True, color if active else TEXT)
    surface.blit(image, image.get_rect(center=rect.center))


def _view_rects() -> list[pygame.Rect]:
    widths = [112, 46, 46, 46, 46]
    result, x = [], SIDEBAR_X
    for width in widths:
        result.append(pygame.Rect(x, 102, width, 32))
        x += width + 7
    return result


def _tool_rects() -> list[pygame.Rect]:
    result = []
    for index in range(len(TOOLS)):
        column, row = index % 3, index // 3
        result.append(pygame.Rect(SIDEBAR_X + column * 154, 164 + row * 39, 144, 32))
    return result


def _world_position(position: tuple[int, int], config: WorldConfig) -> tuple[int, int]:
    x = min(config.width - 1, int((position[0] - WORLD_RECT.x) / WORLD_RECT.width * config.width))
    y = min(config.height - 1, int((position[1] - WORLD_RECT.y) / WORLD_RECT.height * config.height))
    return x, y


def run_app(config: WorldConfig, preset_path: Path | None = None) -> None:
    pygame.init()
    screen = pygame.display.set_mode(WINDOW)
    pygame.display.set_caption("PRIMORDIA — Artificial Life Laboratory")
    clock = pygame.time.Clock()
    ui = pygame.font.SysFont("segoeui", 15)
    ui_bold = pygame.font.SysFont("segoeui", 15, bold=True)
    small = pygame.font.SysFont("consolas", 12)
    number = pygame.font.SysFont("consolas", 16, bold=True)
    title = pygame.font.SysFont("segoeui", 25, bold=True)
    simulation, observer = Simulation(config), Observer()
    paused, mode_index, tool_index, steps_per_second, accumulator = False, 0, 0, 120, 0.0
    radius, running = 8, True
    first = observer.record(simulation.state)
    temperatures = [(first.tick, first.mean_temperature)]
    totals_b = [(first.tick, first.total_b)]
    disturbance_ticks: list[int] = []
    notice, notice_until = "", 0

    while running:
        elapsed = min(clock.tick(60) / 1000.0, 0.1)
        single_step = False
        view_rects, tool_rects = _view_rects(), _tool_rects()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_n:
                    single_step = True
                elif event.key == pygame.K_r:
                    simulation.reset()
                    observer = Observer()
                    initial = observer.record(simulation.state)
                    temperatures[:] = [(initial.tick, initial.mean_temperature)]
                    totals_b[:] = [(initial.tick, initial.total_b)]
                    disturbance_ticks.clear()
                elif event.key in (pygame.K_TAB, pygame.K_v):
                    mode_index = (mode_index + 1) % len(MODES)
                elif event.key == pygame.K_t:
                    tool_index = (tool_index + 1) % len(TOOLS)
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    steps_per_second = min(1920, steps_per_second * 2)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    steps_per_second = max(1, steps_per_second // 2)
                elif event.key == pygame.K_LEFTBRACKET:
                    radius = max(1, radius - 1)
                elif event.key == pygame.K_RIGHTBRACKET:
                    radius = min(32, radius + 1)
                elif event.key == pygame.K_UP:
                    simulation.config.reaction.feed += 0.001
                elif event.key == pygame.K_DOWN:
                    simulation.config.reaction.feed = max(0.0, simulation.config.reaction.feed - 0.001)
                elif event.key == pygame.K_RIGHT:
                    simulation.config.reaction.kill += 0.001
                elif event.key == pygame.K_LEFT:
                    simulation.config.reaction.kill = max(0.0, simulation.config.reaction.kill - 0.001)
                elif event.key == pygame.K_e:
                    observer.export_csv("outputs/interactive.csv")
                    simulation.state.save("outputs/interactive_state.npz")
                    notice, notice_until = "EXPORTED CSV + NPZ", pygame.time.get_ticks() + 2200
                elif event.key == pygame.K_s and preset_path:
                    save_config(simulation.config, preset_path)
                    notice, notice_until = "PRESET SAVED", pygame.time.get_ticks() + 2200
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                selected_ui = False
                for index, rect in enumerate(view_rects):
                    if rect.collidepoint(event.pos):
                        mode_index, selected_ui = index, True
                for index, rect in enumerate(tool_rects):
                    if rect.collidepoint(event.pos):
                        tool_index, selected_ui = index, True
                if WORLD_RECT.collidepoint(event.pos) and not selected_ui:
                    x, y = _world_position(event.pos, config)
                    _, field, amount, _ = TOOLS[tool_index]
                    simulation.disturb(x, y, radius, field, amount)
                    disturbance_ticks.append(simulation.state.tick)
            elif event.type == pygame.MOUSEMOTION and event.buttons[0] and WORLD_RECT.collidepoint(event.pos):
                x, y = _world_position(event.pos, config)
                _, field, amount, _ = TOOLS[tool_index]
                simulation.disturb(x, y, radius, field, amount)

        accumulator += elapsed * steps_per_second
        steps = 1 if single_step else (int(accumulator) if not paused else 0)
        if steps:
            advanced = min(steps, 64)
            simulation.step(advanced)
            accumulator -= advanced
            if simulation.state.tick % 5 == 0 or single_step:
                observation = observer.record(simulation.state)
                temperatures.append((observation.tick, observation.mean_temperature))
                totals_b.append((observation.tick, observation.total_b))

        screen.fill((6, 12, 19))
        pygame.draw.rect(screen, (9, 17, 25), pygame.Rect(0, 0, WINDOW[0], 72))
        pygame.draw.line(screen, BORDER, (0, 71), (WINDOW[0], 71))
        _text(screen, title, "PRIMORDIA", 24, 18, ACCENT)
        _text(screen, ui, "FIELD LABORATORY", 182, 25, MUTED)
        _pill(screen, small, "PAUSED" if paused else "RUNNING", pygame.Rect(947, 20, 86, 30), (238, 184, 81) if paused else ACCENT, True)
        _pill(screen, small, f"TICK {simulation.state.tick}", pygame.Rect(1041, 20, 104, 30), ACCENT)
        _pill(screen, small, f"{steps_per_second} Hz", pygame.Rect(1153, 20, 88, 30), ACCENT)

        pygame.draw.rect(screen, PANEL, WORLD_RECT.inflate(4, 4), border_radius=3)
        draw_world(screen, simulation.state, MODES[mode_index], WORLD_RECT)
        pygame.draw.rect(screen, ACCENT, WORLD_RECT, 1)
        legend = pygame.Rect(WORLD_RECT.x + 14, WORLD_RECT.bottom - 43, 238, 10)
        legend_back = pygame.Rect(legend.x - 9, legend.y - 8, legend.width + 18, 41)
        overlay = pygame.Surface(legend_back.size, pygame.SRCALPHA)
        pygame.draw.rect(overlay, (5, 12, 19, 205), overlay.get_rect(), border_radius=7)
        screen.blit(overlay, legend_back)
        draw_color_legend(screen, MODES[mode_index], legend, small)

        mouse = pygame.mouse.get_pos()
        if WORLD_RECT.collidepoint(mouse):
            visual_radius = radius * WORLD_RECT.width / config.width
            tool_color = TOOLS[tool_index][3]
            brush = pygame.Surface((round(visual_radius * 2 + 6), round(visual_radius * 2 + 6)), pygame.SRCALPHA)
            center = brush.get_width() // 2
            pygame.draw.circle(brush, (*tool_color, 38), (center, center), round(visual_radius))
            pygame.draw.circle(brush, (*tool_color, 225), (center, center), round(visual_radius), 2)
            screen.blit(brush, (mouse[0] - center, mouse[1] - center))
            gx, gy = _world_position(mouse, config)
            state = simulation.state
            hover_text = f"({gx:03}, {gy:03})  A {state.a[gy,gx]:.3f}  B {state.b[gy,gx]:.3f}  R {state.resource[gy,gx]:.3f}  T {state.temperature[gy,gx]:.3f}"
            hover_image = small.render(hover_text, True, TEXT)
            hover_rect = hover_image.get_rect()
            hover_rect.bottomleft = (WORLD_RECT.x + 14, WORLD_RECT.bottom - 57)
            hover_back = hover_rect.inflate(14, 8)
            pygame.draw.rect(screen, (7, 15, 23), hover_back, border_radius=5)
            pygame.draw.rect(screen, BORDER, hover_back, 1, border_radius=5)
            screen.blit(hover_image, hover_rect)

        _text(screen, ui_bold, "FIELD VIEW", SIDEBAR_X, 78, MUTED)
        for index, rect in enumerate(view_rects):
            _pill(screen, small, MODES[index], rect, ACCENT, index == mode_index)
        _text(screen, ui_bold, "DISTURBANCE TOOL", SIDEBAR_X, 143, MUTED)
        for index, rect in enumerate(tool_rects):
            _pill(screen, small, TOOLS[index][0], rect, TOOLS[index][3], index == tool_index)

        current = measure(simulation.state)
        info = pygame.Rect(SIDEBAR_X, 246, SIDEBAR_W, 66)
        pygame.draw.rect(screen, PANEL_RAISED, info, border_radius=10)
        pygame.draw.rect(screen, BORDER, info, 1, border_radius=10)
        labels = [
            ("SEED", str(config.seed)),
            ("BRUSH", f"{radius} cells"),
            ("FEED", f"{simulation.config.reaction.feed:.4f}"),
            ("KILL", f"{simulation.config.reaction.kill:.4f}"),
        ]
        for index, (label, value) in enumerate(labels):
            x = info.x + 13 + index * 117
            _text(screen, small, label, x, info.y + 9, MUTED)
            _text(screen, number, value, x, info.y + 29, TEXT)

        draw_series(screen, temperatures, pygame.Rect(SIDEBAR_X, 326, SIDEBAR_W, 145), (243, 104, 91), "mean temperature", small, number, disturbance_ticks)
        draw_series(screen, totals_b, pygame.Rect(SIDEBAR_X, 483, SIDEBAR_W, 145), (201, 103, 241), "total B", small, number, disturbance_ticks)

        _text(screen, ui_bold, "QUICK CONTROLS", SIDEBAR_X, 648, MUTED)
        controls = [
            ("SPACE", "pause / resume"), ("N", "single step"),
            ("+  −", "simulation speed"), ("R", "reset seed"),
            ("[  ]", "brush radius"), ("ARROWS", "feed / kill"),
            ("E", "export data"), ("S", "save preset"),
        ]
        for index, (key, action) in enumerate(controls):
            column, row = index % 2, index // 2
            x, y = SIDEBAR_X + column * 241, 675 + row * 31
            key_rect = pygame.Rect(x, y, 64, 23)
            pygame.draw.rect(screen, PANEL_RAISED, key_rect, border_radius=5)
            pygame.draw.rect(screen, BORDER, key_rect, 1, border_radius=5)
            key_image = small.render(key, True, ACCENT)
            screen.blit(key_image, key_image.get_rect(center=key_rect.center))
            _text(screen, small, action, x + 73, y + 4, MUTED)

        if notice and pygame.time.get_ticks() < notice_until:
            notice_image = small.render(notice, True, ACCENT)
            notice_rect = notice_image.get_rect(topright=(WINDOW[0] - 24, 78))
            screen.blit(notice_image, notice_rect)
        pygame.display.flip()
    pygame.quit()
