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
