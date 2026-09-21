"""Regression tests.

Each test here pins either a bug that was found and fixed, or a golden result
that should only change on purpose. When a golden number moves, the right
response is to explain why in the commit message - not to update the constant
until the test goes green (Section 22: never weaken a test to pass CI).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from maysani_quant.backtest.metrics import MetricsBundle
from maysani_quant.backtest.report import render_comparison
from maysani_quant.backtest.runner import build_source, run_strategy
from maysani_quant.cli import main
from maysani_quant.config import load_config
from maysani_quant.experiments.registry import ExperimentRegistry
from maysani_quant.strategies.base import build_strategy

REPO = Path(__file__).resolve().parents[2]
CONFIG = REPO / "configs" / "v0_1.yaml"


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch) -> Path:
    """Fresh working dir with the synthetic dataset and a copy of the config."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "v0_1.yaml").write_text(CONFIG.read_text(), encoding="utf-8")
    assert main(["make-synthetic-dataset", "--out", "data/SYNTHETIC_eurusd_d1.csv"]) == 0
    return tmp_path


# --------------------------------------------------------------- fixed bugs
def test_buy_and_hold_has_a_default_stop_and_actually_trades(workspace: Path):
    """Regression: v1.0.0 had no stop, was vetoed every bar, and looked flat.

    A control that never trades is indistinguishable from no_trade_v1 and
    silently removes the drift check the baseline set exists to provide.
    """
    strategy = build_strategy("buy_and_hold_v1")
    assert strategy.params["stop_atr_multiple"] > 0

    config = load_config("configs/v0_1.yaml")
    source = build_source(config)
    registry = ExperimentRegistry("runs/experiments.jsonl")
    spec = next(s for s in config.strategies if s.id == "buy_and_hold_v1")
    output = run_strategy(config, spec, source, registry)
    assert output.metrics["trade_count"] >= 1
    assert output.result.risk_veto_counts.get("STOP_DISTANCE_INVALID", 0) == 0


def test_comparison_warns_about_strategies_that_never_traded():
    """Regression: an inert strategy used to print as a clean zero row."""
    inert = MetricsBundle(
        values={"trade_count": 0, "risk_vetoes": {"STOP_DISTANCE_INVALID": 549}}
    )
    control = MetricsBundle(values={"trade_count": 0, "risk_vetoes": {}})
    text = render_comparison([("no_trade_v1", control), ("buy_and_hold_v1", inert)])
    assert "WARNING" in text
    assert "buy_and_hold_v1: top veto STOP_DISTANCE_INVALID x549" in text
    assert "no_trade_v1:" not in text, "the no-trade control is supposed to be flat"


def test_replay_into_an_existing_journal_is_idempotent(workspace: Path):
    """Regression: record ids once included the sequence number, so a replay
    produced new ids for identical events and duplicated every fill."""
    from maysani_quant.journal.store import Journal

    journal = Journal("runs", "idem")
    journal.append("FILL", {"t": "2024-01-01", "px": 1.1})
    replay = Journal("runs", "idem")
    replay.append("FILL", {"t": "2024-01-01", "px": 1.1})
    assert len(list(replay.read_all())) == 1


# ------------------------------------------------------------ golden results
@pytest.mark.parametrize(
    "strategy_id,expected_trades",
    [("no_trade_v1", 0), ("buy_and_hold_v1", 2), ("momentum_v1", 17), ("mean_reversion_v1", 44)],
)
def test_golden_trade_counts_on_the_synthetic_fixture(
    workspace: Path, strategy_id: str, expected_trades: int
):
    """Pipeline behaviour on a fixed SYNTHETIC input. Describes the generator,
    not EUR/USD. A change here means the engine's behaviour changed."""
    config = load_config("configs/v0_1.yaml")
    source = build_source(config)
    registry = ExperimentRegistry("runs/experiments.jsonl")
    spec = next(s for s in config.strategies if s.id == strategy_id)
    output = run_strategy(config, spec, source, registry)
    assert output.metrics["trade_count"] == expected_trades


def test_synthetic_generator_is_byte_stable(workspace: Path):
    """The fixture must be identical on every machine or goldens mean nothing."""
    first = (workspace / "data" / "SYNTHETIC_eurusd_d1.csv").read_bytes()
    assert main(["make-synthetic-dataset", "--out", "data/SYNTHETIC_again.csv"]) == 0
    second = (workspace / "data" / "SYNTHETIC_again.csv").read_bytes()
    assert first == second


# ---------------------------------------------------- reproducibility / CLI
@pytest.mark.invariant
def test_experiment_id_is_reproducible_across_runs(workspace: Path):
    """Same config + data + code -> same experiment id (Section 21.9)."""
    config = load_config("configs/v0_1.yaml")
    source = build_source(config)
    spec = config.strategies[2]
    a = run_strategy(config, spec, source, ExperimentRegistry("runs/a.jsonl"))
    b = run_strategy(config, spec, source, ExperimentRegistry("runs/b.jsonl"))
    assert a.experiment_id == b.experiment_id

    record = ExperimentRegistry("runs/a.jsonl").find(a.experiment_id)
    assert record is not None
    opened = record["open"]
    assert opened["data_hash"] == source.data_hash
    assert opened["config_hash"] == config.config_hash
    assert opened["code_version"]
    assert record["close"]["status"] == "COMPLETED"


@pytest.mark.invariant
def test_every_trial_is_recorded_including_controls(workspace: Path):
    assert main(["backtest", "--config", "configs/v0_1.yaml"]) == 0
    registry = ExperimentRegistry("runs/experiments.jsonl")
    assert registry.trial_count() == 4
    assert main(["backtest", "--config", "configs/v0_1.yaml"]) == 0
    assert registry.trial_count() == 8, "re-runs are new trials and must be counted"


def test_cli_backtest_writes_report_and_json(workspace: Path):
    assert main(["backtest", "--config", "configs/v0_1.yaml", "--json", "runs/m.json"]) == 0
    reports = list(Path("runs").glob("report_*.txt"))
    assert reports
    text = reports[0].read_text()
    assert "SYNTHETIC DATASET - NOT MARKET DATA" in text
    assert "no_trade_v1" in text and "momentum_v1" in text and "mean_reversion_v1" in text
    payload = json.loads(Path("runs/m.json").read_text())
    assert set(payload) == {"no_trade_v1", "buy_and_hold_v1", "momentum_v1", "mean_reversion_v1"}


@pytest.mark.invariant
def test_report_makes_no_profitability_claim(workspace: Path):
    assert main(["backtest", "--config", "configs/v0_1.yaml"]) == 0
    text = next(Path("runs").glob("report_*.txt")).read_text().lower()
    for claim in ("profitable strategy", "guaranteed", "proven edge", "winning strategy"):
        assert claim not in text
    assert "not evidence of profitability" in text


def test_synthetic_generator_refuses_an_unlabelled_filename(workspace: Path):
    assert main(["make-synthetic-dataset", "--out", "data/eurusd_d1.csv"]) == 2
    assert not Path("data/eurusd_d1.csv").exists()


def test_backtest_refuses_invalid_data(workspace: Path):
    bad = Path("data/SYNTHETIC_bad.csv")
    bad.write_text(
        "timestamp,open,high,low,close\n"
        "2024-01-01T00:00:00+00:00,1.1,1.0,1.2,1.1\n",   # high < low
        encoding="utf-8",
    )
    assert main(["backtest", "--config", "configs/v0_1.yaml", "--dataset", str(bad)]) == 2


def test_missing_dataset_fails_with_a_pointer_to_the_docs(workspace: Path):
    with pytest.raises(FileNotFoundError, match="data/README.md"):
        main(["validate-data", "--config", "configs/v0_1.yaml", "--dataset", "data/nope.csv"])


# ------------------------------------------------------------------ config
@pytest.mark.invariant
def test_unknown_config_key_is_refused(tmp_path: Path):
    """A typo in a risk key must not silently run the default (Section 21.8)."""
    text = CONFIG.read_text() + "\nrsik:\n  max_leverage: 500\n"
    path = tmp_path / "typo.yaml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="unknown config keys"):
        load_config(path)


def test_config_hash_changes_when_a_risk_limit_changes(tmp_path: Path):
    base = load_config(CONFIG)
    changed = tmp_path / "changed.yaml"
    changed.write_text(
        CONFIG.read_text().replace("max_leverage: 5.0", "max_leverage: 4.0"), encoding="utf-8"
    )
    assert load_config(changed).config_hash != base.config_hash


def test_no_llm_or_network_dependency_in_v0_1():
    """Section 21.1: V0.1 has no LLM dependency. Checked at the import level."""
    import maysani_quant  # noqa: F401

    source_root = REPO / "src" / "maysani_quant"
    forbidden = ("anthropic", "openai", "requests", "httpx", "langchain", "urllib.request")
    for path in source_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for name in forbidden:
            assert f"import {name}" not in text and f"from {name}" not in text, (
                f"{path.relative_to(REPO)} imports {name}"
            )
