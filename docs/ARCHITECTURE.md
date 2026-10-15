# Architecture

PRIMORDIA keeps the numerical world independent of display and input. The same `Simulation` class drives the pygame application, tests, and headless experiments.

## Responsibilities

- `config.py` defines nested dataclasses, validates values, and performs JSON loading/saving.
- `simulation/state.py` owns the four NumPy arrays, tick, validation, and NPZ snapshots.
- `simulation/diffusion.py` computes a five-point discrete Laplacian with periodic or reflective boundaries.
- `simulation/reactions.py` computes local Gray–Scott-derived reaction terms plus resource/temperature coupling.
- `simulation/environment.py` computes explicit resource and thermal exchange.
- `simulation/engine.py` initializes from a dedicated NumPy generator, combines derivatives, and advances all fields simultaneously.
- `experiments/metrics.py` measures a state without depending on rendering.
- `experiments/runner.py` executes single and paired headless experiments.
- `visualization/renderer.py` maps real arrays to color and draws history plots.
- `visualization/app.py` runs a fixed-timestep accumulator, handles tools, and presents the laboratory.
- `__main__.py` exposes `gui`, `run`, and `pair`.

## Tick sequence

~~~text
previous immutable field values
       │
       ├── local reaction derivatives
       ├── four diffusion derivatives
       └── explicit environmental derivatives
                         │
                  sum derivatives
                         │
             forward Euler × fixed dt
                         │
              documented safety bounds
                         │
                 validate, tick + 1
~~~

Every derivative sees the same previous arrays. No field is updated early, so iteration order cannot create a directional bias.

## Fixed simulation time

The GUI accumulates wall-clock time and converts it into logical ticks at the selected target rate. Rendering stays near 60 frames per second. A per-frame cap prevents a stalled window from attempting an unbounded catch-up. Headless runs simply execute the requested tick count.

## Reproducibility

Each `Simulation` owns `numpy.random.Generator(PCG64)` through `default_rng(seed)`. Reset reconstructs that generator and initial state. Identical dependencies, platform, configuration, and seed should reproduce arrays exactly. Floating-point order, NumPy builds, processors, or future dependency changes can prevent bit-for-bit reproducibility; CSV metrics remain the practical comparison surface.

## Design decisions

NumPy makes the model explicit and vectorized without tying it to a renderer. pygame-ce provides a lightweight desktop loop. JSON presets are diffable; CSV is easy to inspect; NPZ preserves numerical arrays. Dataclasses keep configuration discoverable without an abstraction framework.

Prototype 1 avoids an entity model because cells contain fields, not organisms. Performance improvements can later replace numerical kernels while preserving configuration, state, observation, and UI boundaries.
