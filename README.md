<div align="center">

# PRIMORDIA

### Artificial Life & Emergent Homeostasis Laboratory

**Build a universe. Disturb it. Measure what its rules permit.**

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-55d6c2)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/core-NumPy-4d77cf)](https://numpy.org/)
[![pygame-ce](https://img.shields.io/badge/interface-pygame--ce-a77bf3)](https://pyga.me/)
[![tests-pytest](https://img.shields.io/badge/tests-pytest-f0c75e)](https://pytest.org/)

</div>

PRIMORDIA is a working two-dimensional numerical laboratory for studying pattern formation, persistence, disturbance, and environmental feedback. Its world contains four continuous fields—reactants **A** and **B**, resource **R**, and temperature **T**—with no creatures, goals, health values, or programmed survival behavior.

Prototype 1 uses a modified Gray–Scott reaction–diffusion system. Resource availability gates the autocatalytic reaction, the reaction releases heat, and the environment supplies/removes resource and exchanges heat with an ambient reservoir. These additions create feedback worth measuring. They do not establish life, intelligence, adaptation, or homeostasis.

## What you can do

- Watch real field dynamics through five high-contrast visualization modes with live legends.
- Pause, single-step, change speed, and reset exactly to the original seed.
- Heat, cool, add/remove B, or add resource through local disturbances.
- Adjust feed and kill parameters while the simulation runs.
- Inspect exact A/B/R/T values under the cursor and see disturbance markers in live metric cards.
- Export observations as CSV and state snapshots as compressed NPZ.
- Run the same configuration headlessly.
- Compare a baseline world and disturbed world from the same initial seed.

## Install on Windows

Python 3.12 or newer is required. From PowerShell in the repository:

~~~powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
~~~

If PowerShell blocks activation, use Command Prompt:

~~~cmd
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
~~~

Python 3.13 and 3.14 are also supported when compatible wheels are available.

## Launch the laboratory

~~~powershell
python -m primordia --preset presets/coral.json gui
~~~

The default command also launches the GUI:

~~~powershell
python -m primordia
~~~

Field views and disturbance tools are clickable. Core shortcuts: `Space` pauses, `N` advances one tick, `R` resets, `Tab` changes view, `T` changes the disturbance tool, mouse dragging applies it, `+`/`-` changes speed, arrow keys alter feed/kill, and `E` exports observations and a snapshot.

## Run reproducible experiments

One headless run:

~~~powershell
python -m primordia --preset presets/coral.json run --ticks 1000 --sample-every 10 --output outputs/run.csv --snapshot outputs/run.npz
~~~

Matched baseline and heated world:

~~~powershell
python -m primordia --preset presets/coral.json pair --ticks 1000 --disturb-at 400 --field T --amount 0.7 --radius 8 --output-dir outputs/heat-pair
~~~

Run the test suite:

~~~powershell
python -m pytest
~~~

## Presets

| Preset | Purpose |
|---|---|
| `coral.json` | A reliable pattern-oriented starting regime with moderate feedback |
| `homogeneous.json` | A deliberately uniform control |
| `instability.json` | Stronger coupling and reflective boundaries for parameter sensitivity |

Preset names describe intended regimes, not experimental findings. Exact appearances depend on duration and numerical parameters.

## Project map

~~~text
src/primordia/
├── config.py                 central validated configuration
├── simulation/              arrays, reactions, diffusion, environment, engine
├── experiments/             metrics and reproducible headless runs
├── visualization/           pygame renderer and interactive application
└── __main__.py              GUI and experiment command line
presets/                      JSON starting configurations
tests/                        numerical and integration checks
docs/                         mathematics, architecture, experiments, user guide, log
~~~

Read [MATHEMATICS.md](docs/MATHEMATICS.md) for every equation and approximation, [ARCHITECTURE.md](docs/ARCHITECTURE.md) for data flow, [EXPERIMENTS.md](docs/EXPERIMENTS.md) for careful interpretation, and [USER_GUIDE.md](docs/USER_GUIDE.md) for all controls.

## Current scientific status

The prototype can produce spatially structured reaction–diffusion behavior and measurable responses to local disturbance. A return toward a prior temperature or concentration can arise from passive diffusion and environmental exchange. Calling that active homeostasis would require controls, recovery criteria, repeated seeds, and evidence that interacting structures contribute something beyond passive relaxation.

## License

MIT. See [LICENSE](LICENSE).
