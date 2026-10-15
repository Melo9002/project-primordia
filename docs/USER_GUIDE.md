# User guide

## Starting

Install with `python -m pip install -e ".[dev]"`, then launch `python -m primordia` from the repository root. Select another preset with `--preset presets/instability.json`.

## Display

The large panel renders the selected field. The composite maps B through a dark-cyan-gold chemistry palette, uses resource as illumination, adds a restrained warm/cool temperature tint, and highlights B gradients at reaction fronts. Single-field views use dedicated perceptual palettes and documented ranges. The legend shows the active scale.

Hovering over the world shows grid coordinates and exact A/B/R/T values. The translucent colored circle previews the selected disturbance and brush radius. Metric cards report current values, recent ranges, and amber event lines for applied disturbances.

## Controls

| Input | Effect |
|---|---|
| `Space` | pause/resume |
| `N` | advance one fixed tick |
| `R` | reset arrays and RNG to the original seed |
| `Tab` or `V` | cycle composite, A, B, R, T |
| `T` | cycle heat, cool, add B, remove B, add resource |
| click view/tool pills | select a field view or disturbance directly |
| mouse click/drag | apply the selected tool to actual state |
| `[` / `]` | change brush radius |
| `+` / `-` | double/halve target tick rate |
| up/down | increase/decrease feed by 0.001 |
| right/left | increase/decrease kill by 0.001 |
| `E` | export `outputs/interactive.csv` and NPZ state |
| `S` | save current parameters over the selected preset |

The yellow circle previews the disturbance footprint. Tool changes are bounded to safe field ranges.

## Configuration

Top-level keys set dimensions, fixed `dt`, seed, dtype, and boundary. `initial` controls base fields, noise, and central perturbation. `reaction` controls Gray–Scott and experimental coupling. `diffusion` has one coefficient per field. `environment` contains ambient temperature, exchange, heating, resource supply/removal, and supplied concentration.

Unknown keys fail loudly. GUI parameter changes affect the live world; reset returns to the initially loaded configuration. Pressing `S` intentionally replaces the selected JSON preset.

## Headless commands

Use `run` for one trajectory and `pair` for matched baseline/disturbance output. Run `python -m primordia --help` and each subcommand with `--help` for options. Headless modules never import or initialize pygame.

## Files

CSV files are UTF-8 tables. NPZ snapshots contain `a`, `b`, `resource`, `temperature`, and `tick`. Load a snapshot with `WorldState.load(path)`.
