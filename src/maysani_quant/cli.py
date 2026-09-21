"""Command line interface.

    maysani-quant backtest --config configs/v0_1.yaml
    maysani-quant validate-data --config configs/v0_1.yaml
    maysani-quant show-experiment --id <experiment_id>
    maysani-quant make-synthetic-dataset --out data/SYNTHETIC_...csv
    maysani-quant strategies

`make-synthetic-dataset` exists so the pipeline is runnable before a licensed
EUR/USD dataset is in place. Its output is named SYNTHETIC_*, flagged in every
bar's quality flags, and banner-warned in the report. It is a test fixture for
the plumbing - it is not market data and nothing measured on it says anything
about EUR/USD (Section 22: never fabricate market data).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from maysani_quant import __version__
from maysani_quant.backtest.report import render_comparison, render_run_report
from maysani_quant.backtest.runner import build_source, ensure_dir, run_strategy
from maysani_quant.config import load_config
from maysani_quant.experiments.registry import ExperimentRegistry, code_version
from maysani_quant.strategies.base import registered_strategies

REGISTRY_PATH = "runs/experiments.jsonl"


def cmd_backtest(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    source = build_source(config, args.dataset)
    registry = ExperimentRegistry(args.registry)
    ensure_dir(config.report_dir)

    if not source.validation.ok and not args.allow_bad_data:
        print("DATA VALIDATION FAILED - refusing to run.", file=sys.stderr)
        print(f"  {source.validation.summary()}", file=sys.stderr)
        print("  Fix the dataset, or pass --allow-bad-data to run anyway", file=sys.stderr)
        print("  (the risk engine will then reject new risk on every bar).", file=sys.stderr)
        return 2

    outputs = []
    for spec in config.strategies:
        output = run_strategy(config, spec, source, registry)
        outputs.append((spec.id, output))

    primary_id = args.strategy or config.strategies[-1].id
    primary = dict(outputs).get(primary_id)
    if primary is None:
        print(f"strategy '{primary_id}' not in config", file=sys.stderr)
        return 2

    report = render_run_report(
        result=primary.result,
        metrics=primary.metrics,
        cost_model=config.costs.describe(),
        risk_config_version=config.risk.config_version,
        code_version=code_version(),
        dataset_path=source.dataset_path,
        timeframe=config.timeframe,
        trial_count=registry.trial_count(),
    )
    comparison = render_comparison([(name, out.metrics) for name, out in outputs])
    text = report + "\n" + comparison
    print(text)

    report_path = Path(config.report_dir) / f"report_{primary.result.run_id}.txt"
    report_path.write_text(text, encoding="utf-8")
    if args.json:
        payload = {
            name: {
                "experiment_id": out.experiment_id,
                "run_id": out.result.run_id,
                **out.metrics.to_dict(),
            }
            for name, out in outputs
        }
        Path(args.json).write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"[written] {report_path}")
    return 0


def cmd_validate_data(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    source = build_source(config, args.dataset)
    report = source.validation
    print(f"dataset      : {source.dataset_path}")
    print(f"file_sha256  : {source.file_hash}")
    print(f"data_hash    : {source.data_hash}")
    print(f"synthetic    : {source.is_synthetic}")
    print(f"price_kind   : {source.price_kind}")
    print(f"avail policy : {source.available_time_policy}")
    print(f"bars         : {report.bar_count}")
    print(f"first / last : {report.first_time} -> {report.last_time}")
    print(f"validation   : {report.summary()}")
    for issue in report.issues[:20]:
        print(f"  - {issue.timestamp} {issue.flag.value}: {issue.detail}")
    if len(report.issues) > 20:
        print(f"  ... {len(report.issues) - 20} more")
    return 0 if report.ok else 2


def cmd_show_experiment(args: argparse.Namespace) -> int:
    registry = ExperimentRegistry(args.registry)
    found = registry.find(args.id)
    if found is None:
        print(f"no experiment '{args.id}' in {args.registry}", file=sys.stderr)
        return 2
    print(json.dumps(found, indent=2, default=str))
    return 0


def cmd_strategies(_: argparse.Namespace) -> int:
    for name in registered_strategies():
        print(name)
    return 0


def cmd_make_synthetic(args: argparse.Namespace) -> int:
    """Deterministic synthetic bars for pipeline testing. NOT market data."""
    path = Path(args.out)
    if "SYNTHETIC" not in path.name.upper():
        print("refusing to write: filename must contain 'SYNTHETIC'", file=sys.stderr)
        return 2
    path.parent.mkdir(parents=True, exist_ok=True)

    # A fixed LCG, so the file is byte-identical on every machine.
    seed = args.seed
    def rand() -> float:
        nonlocal seed
        seed = (1103515245 * seed + 12345) % (2 ** 31)
        return seed / (2 ** 31)

    start = datetime(2020, 1, 1, tzinfo=UTC)
    price = 1.10
    rows = ["timestamp,open,high,low,close,volume"]
    for i in range(args.bars):
        drift = 0.00002 * math.sin(i / 40.0)
        shock = (rand() - 0.5) * 0.004
        open_px = price
        close_px = max(0.5, open_px * (1 + drift + shock))
        high = max(open_px, close_px) * (1 + rand() * 0.0015)
        low = min(open_px, close_px) * (1 - rand() * 0.0015)
        ts = (start + timedelta(days=i)).isoformat()
        rows.append(
            f"{ts},{open_px:.5f},{high:.5f},{low:.5f},{close_px:.5f},{int(1000 + rand() * 5000)}"
        )
        price = close_px
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"[written] {path} ({args.bars} SYNTHETIC bars - not market data)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="maysani-quant", description=__doc__)
    parser.add_argument("--version", action="version", version=f"maysani-quant {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    bt = sub.add_parser("backtest", help="run the configured backtest and baselines")
    bt.add_argument("--config", default="configs/v0_1.yaml")
    bt.add_argument("--dataset", default=None, help="override the configured dataset path")
    bt.add_argument("--strategy", default=None, help="which strategy the detail report covers")
    bt.add_argument("--registry", default=REGISTRY_PATH)
    bt.add_argument("--json", default=None, help="also write metrics to this JSON path")
    bt.add_argument("--allow-bad-data", action="store_true")
    bt.set_defaults(func=cmd_backtest)

    vd = sub.add_parser("validate-data", help="inspect and fingerprint a dataset")
    vd.add_argument("--config", default="configs/v0_1.yaml")
    vd.add_argument("--dataset", default=None)
    vd.set_defaults(func=cmd_validate_data)

    se = sub.add_parser("show-experiment", help="print one experiment record")
    se.add_argument("--id", required=True)
    se.add_argument("--registry", default=REGISTRY_PATH)
    se.set_defaults(func=cmd_show_experiment)

    st = sub.add_parser("strategies", help="list registered strategies")
    st.set_defaults(func=cmd_strategies)

    ms = sub.add_parser(
        "make-synthetic-dataset",
        help="write deterministic SYNTHETIC bars for pipeline testing (not market data)",
    )
    ms.add_argument("--out", default="data/SYNTHETIC_eurusd_d1.csv")
    ms.add_argument("--bars", type=int, default=600)
    ms.add_argument("--seed", type=int, default=20260920)
    ms.set_defaults(func=cmd_make_synthetic)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
