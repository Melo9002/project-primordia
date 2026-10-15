"""Interactive PRIMORDIA laboratory."""

from __future__ import annotations

from pathlib import Path
import pygame

from primordia.config import WorldConfig, save_config
from primordia.experiments.metrics import Observer
from primordia.simulation.engine import Simulation
from .renderer import draw_series, draw_world

WINDOW = (1160, 780)
WORLD_RECT = pygame.Rect(24, 72, 680, 680)
MODES = ["COMPOSITE", "A", "B", "R", "T"]
TOOLS = [
    ("HEAT", "T", 0.45),
    ("COOL", "T", -0.45),
    ("ADD B", "B", 0.35),
    ("REMOVE B", "B", -0.35),
    ("ADD R", "R", 0.45),
]


def _text(surface: pygame.Surface, font: pygame.font.Font, value: str, x: int, y: int, color=(205, 218, 226)) -> None:
    surface.blit(font.render(value, True, color), (x, y))


def run_app(config: WorldConfig, preset_path: Path | None = None) -> None:
    pygame.init()
    screen = pygame.display.set_mode(WINDOW)
    pygame.display.set_caption("PRIMORDIA — Artificial Life Laboratory")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 16)
    small = pygame.font.SysFont("consolas", 13)
    title = pygame.font.SysFont("segoeui", 24, bold=True)
    simulation, observer = Simulation(config), Observer()
    paused, mode_index, tool_index, steps_per_second, accumulator = False, 0, 0, 120, 0.0
    radius, running = 8, True
    observer.record(simulation.state)
    temperatures, totals_b = [], []

    while running:
        elapsed = min(clock.tick(60) / 1000.0, 0.1)
        single_step = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_n:
                    single_step = True
                elif event.key == pygame.K_r:
                    simulation.reset(); observer = Observer(); temperatures.clear(); totals_b.clear()
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
                elif event.key == pygame.K_s and preset_path:
                    save_config(simulation.config, preset_path)
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                active = event.type == pygame.MOUSEBUTTONDOWN or any(event.buttons)
                if active and WORLD_RECT.collidepoint(event.pos):
                    x = int((event.pos[0] - WORLD_RECT.x) / WORLD_RECT.width * config.width)
                    y = int((event.pos[1] - WORLD_RECT.y) / WORLD_RECT.height * config.height)
                    _, field, amount = TOOLS[tool_index]
                    simulation.disturb(x, y, radius, field, amount)

        accumulator += elapsed * steps_per_second
        steps = 1 if single_step else (int(accumulator) if not paused else 0)
        if steps:
            simulation.step(min(steps, 64))
            accumulator -= min(steps, 64)
            if simulation.state.tick % 5 == 0 or single_step:
                observation = observer.record(simulation.state)
                temperatures.append(observation.mean_temperature)
                totals_b.append(observation.total_b)

        screen.fill((8, 13, 20))
        _text(screen, title, "PRIMORDIA", 24, 22, (93, 222, 201))
        _text(screen, font, "field laboratory / prototype 1", 175, 29, (126, 145, 158))
        draw_world(screen, simulation.state, MODES[mode_index], WORLD_RECT)
        pygame.draw.rect(screen, (87, 218, 193), WORLD_RECT, 2)
        px, py = pygame.mouse.get_pos()
        if WORLD_RECT.collidepoint((px, py)):
            visual_radius = radius * WORLD_RECT.width / config.width
            pygame.draw.circle(screen, (245, 238, 162), (px, py), visual_radius, 1)

        x = 732
        _text(screen, title, "OBSERVATORY", x, 22, (215, 226, 232))
        status = "PAUSED" if paused else "RUNNING"
        _text(screen, font, f"{status:<8} tick {simulation.state.tick:>8}", x, 76)
        _text(screen, font, f"seed {config.seed:<8} rate {steps_per_second:>4} tick/s", x, 102)
        _text(screen, font, f"view {MODES[mode_index]:<10} tool {TOOLS[tool_index][0]}", x, 128)
        _text(screen, font, f"brush radius {radius:>2} cells", x, 154)
        _text(screen, font, f"feed {simulation.config.reaction.feed:.4f}  kill {simulation.config.reaction.kill:.4f}", x, 180)
        draw_series(screen, temperatures, pygame.Rect(x, 220, 400, 150), (245, 108, 96), "mean temperature", small)
        draw_series(screen, totals_b, pygame.Rect(x, 386, 400, 150), (202, 118, 246), "total B", small)
        _text(screen, font, "CONTROLS", x, 558, (93, 222, 201))
        controls = [
            "Space pause     N single step",
            "+/- speed       R reset seed",
            "Tab view        T disturbance tool",
            "[/] brush       mouse apply tool",
            "arrows: feed / kill",
            "E export CSV + NPZ    S save preset",
        ]
        for index, line in enumerate(controls):
            _text(screen, small, line, x, 589 + index * 23)
        pygame.display.flip()
    pygame.quit()
