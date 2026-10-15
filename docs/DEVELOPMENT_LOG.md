# Development log

## 2026-10-15 — Prototype 1

Implemented the first complete numerical universe:

- four continuous NumPy fields with deterministic seeded initialization;
- modified Gray–Scott kinetics, resource gating/consumption, and two-way thermal coupling;
- periodic and reflective five-point diffusion;
- simultaneous fixed-step Euler updates with explicit bounds and validation;
- pygame-ce laboratory with field/composite views, plots, controls, live parameters, and real-state disturbances;
- rendering-independent metrics, CSV export, NPZ snapshots, headless runs, and paired experiments;
- homogeneous, pattern-oriented, and instability-oriented presets;
- tests for determinism, reproducibility, boundaries, conservation in a closed control, disturbances, snapshots, paired runs, and headless independence;
- architecture, mathematics, experiment, and user documentation.

Known limitations: forward Euler and clamps restrict safe parameter exploration; metrics are global and do not track individual structures; the GUI has keyboard parameter controls rather than text widgets; no experiment has yet established active homeostasis. The highest-value next work is a multi-seed feedback-disabled comparison with predeclared recovery metrics.

## 2026-10-15 — Visual laboratory pass

Reworked the pygame interface around a higher-contrast scientific dashboard. Added chemistry/resource/temperature composite shading, reaction-front highlights, perceptual single-field palettes, live legends, clickable field and disturbance pills, parameter cards, antialiased metric plots, disturbance event markers, cell-value hover readouts, and a translucent brush preview. Every visual channel remains derived from simulation state or recorded interaction history.

Added zero-activation launchers for Windows and POSIX systems. They reuse the repository virtual environment and create/install it automatically on a fresh checkout.

## 2026-10-15 — Palimpsest Prototype 2

Added waste and structural-memory fields, reaction-front matrix deposition, erosion/dissolution, conservative matrix-dependent transport, boundary-fed environments, enclosure detection, interior/exterior metrics, W/M visualization, a matrix breach tool, and matched dynamic/no-matrix/frozen/random control experiments. The first preset forms a measurable matrix enclosure, but no homeostasis result is claimed.

Validation smoke run: seed 31 matured for 2,000 ticks, then received a +0.2 ambient-temperature change and a radius-4 automatically wall-targeted breach. After 200 response ticks, the dynamic branch detected 102 enclosed cells while frozen, shuffled, and no-matrix controls detected zero. This confirms that the experiment can distinguish active matrix reconstruction from those controls in one run; it is not evidence of robust homeostasis and requires preregistered multi-seed analysis.
