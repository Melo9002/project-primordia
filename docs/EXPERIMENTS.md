# Experiments

## Reproducible procedure

Choose a versioned JSON preset, seed, tick count, sampling interval, and disturbance before running. Record dependency versions and Git commit. The pair command constructs two identical worlds; only the disturbed run receives the event.

~~~powershell
python -m primordia --preset presets/coral.json pair --ticks 2000 --disturb-at 800 --field T --amount 0.7 --radius 8 --sample-every 10 --output-dir outputs/temperature-7
~~~

The folder contains `baseline.csv`, `disturbed.csv`, and the disturbed final state. Metrics include tick, mean and variance of temperature, total A/B/resource, and spatial variance of B.

## Questions the data can answer

- Did the disturbance measurably alter a field?
- Does the difference shrink, persist, oscillate, or settle elsewhere?
- Does B spatial variance persist after a local disruption?
- Are observations consistent over seeds and nearby parameters?
- Does the coupled system differ from a feedback-disabled control?

Define recovery before inspecting the result. One useful operational definition is the first post-disturbance tick at which a metric returns within a chosen fraction of the baseline trajectory and stays there for a fixed window. Report the threshold and window.

## Controls

1. Set `temperature_sensitivity = 0` and `reaction_heat = 0` to disable thermal feedback.
2. Set `resource_cost = 0` to remove resource consumption feedback.
3. Disable reactions and retain thermal exchange/diffusion to measure passive relaxation.
4. Repeat across multiple seeds with identical parameters.
5. Apply an equal disturbance at several locations and times.

Returning toward ambient temperature is expected from environmental exchange. A homeostasis hypothesis needs behavior beyond that control, ideally tied to persistent spatial organization.

## Interactive work

Use the GUI to generate hypotheses, inspect spatial dynamics, and choose disturbance scales. Export with `E`. Treat hand-selected interesting runs as exploratory evidence. Confirm them with scripted headless pairs.

## Suggested next experiment

Run a factorial comparison across 20 seeds with thermal feedback enabled and disabled, using the same localized heat pulse. Measure integrated deviation from each matching baseline and time-to-recovery for mean temperature and B variance. This tests whether the interacting pattern changes disturbance response beyond passive thermal relaxation.

## Honest interpretation

Do not infer adaptation from a single trajectory, homeostasis from equilibrium, or organism status from an organic appearance. Report null and unstable results. Preserve raw CSV, preset, seed, version, and code commit.
