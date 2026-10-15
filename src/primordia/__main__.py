"""Command-line entry points for the GUI and headless experiments."""

from __future__ import annotations

import argparse
from pathlib import Path
from primordia.config import WorldConfig, load_config
from primordia.experiments.runner import Disturbance, run_experiment, run_homeostasis_controls, run_pair


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="primordia")
    parser.add_argument("--preset", type=Path, default=Path("presets/coral.json"))
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("gui", help="launch the interactive laboratory")
    run = subparsers.add_parser("run", help="run one headless experiment")
    run.add_argument("--ticks", type=int, default=1000)
    run.add_argument("--output", type=Path, default=Path("outputs/run.csv"))
    run.add_argument("--sample-every", type=int, default=10)
    run.add_argument("--snapshot", type=Path)
    pair = subparsers.add_parser("pair", help="run matched baseline and disturbed worlds")
    pair.add_argument("--ticks", type=int, default=1000)
    pair.add_argument("--output-dir", type=Path, default=Path("outputs/pair"))
    pair.add_argument("--disturb-at", type=int, default=400)
    pair.add_argument("--field", choices=["A", "B", "R", "T"], default="T")
    pair.add_argument("--amount", type=float, default=0.7)
    pair.add_argument("--radius", type=int, default=8)
    pair.add_argument("--sample-every", type=int, default=10)
    homeostasis = subparsers.add_parser("homeostasis", help="run four matched Palimpsest controls")
    homeostasis.add_argument("--maturation-ticks", type=int, default=2000)
    homeostasis.add_argument("--response-ticks", type=int, default=1000)
    homeostasis.add_argument("--ambient-shift", type=float, default=0.2)
    homeostasis.add_argument("--breach-radius", type=int, default=0)
    homeostasis.add_argument("--sample-every", type=int, default=10)
    homeostasis.add_argument("--output-dir", type=Path, default=Path("outputs/homeostasis"))
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    config = load_config(args.preset) if args.preset.exists() else WorldConfig()
    if args.command in {None, "gui"}:
        from primordia.visualization.app import run_app
        run_app(config, args.preset)
    elif args.command == "run":
        run_experiment(config, args.ticks, args.output, sample_every=args.sample_every, snapshot_path=args.snapshot)
        print(f"wrote {args.output}")
    elif args.command == "pair":
        run_pair(config, args.ticks, args.output_dir, Disturbance(args.disturb_at, args.field, args.amount, radius=args.radius), args.sample_every)
        print(f"wrote paired experiment to {args.output_dir}")
    elif args.command == "homeostasis":
        run_homeostasis_controls(
            config,
            args.maturation_ticks,
            args.response_ticks,
            args.output_dir,
            ambient_shift=args.ambient_shift,
            breach_radius=args.breach_radius,
            sample_every=args.sample_every,
        )
        print(f"wrote Palimpsest controls to {args.output_dir}")


if __name__ == "__main__":
    main()
