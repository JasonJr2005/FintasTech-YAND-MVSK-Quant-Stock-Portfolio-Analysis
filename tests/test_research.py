from __future__ import annotations

import numpy as np
import pandas as pd

from quant_core.data import MarketDataConfig, prices_to_returns
from quant_core.backtest import run_static_backtest
from quant_core.mv import solve_mean_variance
from quant_core.optimizer import YANDConfig, YANDMVSKOptimizer
from quant_core.oracle import MVSKCoefficients, MVSKOracle
from quant_core.research import ResearchConfig, run_research
from quant_core.screening import ScreenerConfig, screen_universe


def test_optimizer_returns_simplex_weights() -> None:
    rng = np.random.default_rng(21)
    returns = rng.normal(0.0005, 0.012, size=(120, 8))
    oracle = MVSKOracle(returns, MVSKCoefficients.preset("balanced"))
    result = YANDMVSKOptimizer(oracle, YANDConfig(max_iter=20)).solve()
    assert np.isclose(result.weights.sum(), 1.0)
    assert np.all(result.weights >= -1e-8)
    assert np.isfinite(result.objective)


def test_screen_mv_and_backtest_pipeline() -> None:
    rng = np.random.default_rng(42)
    frame = pd.DataFrame(
        rng.normal(0.0008, 0.02, size=(160, 10)),
        columns=[f"T{i}" for i in range(10)],
        index=pd.date_range("2022-01-01", periods=160, freq="B"),
    )
    selected = screen_universe(frame, ScreenerConfig(max_assets=6))
    assert len(selected) >= 2
    train = frame[selected].iloc[:100]
    test = frame[selected].iloc[100:]
    weights = solve_mean_variance(train.to_numpy())
    result = run_static_backtest(test, weights)
    assert result.equity_curve
    assert "sharpe" in result.metrics


def test_screen_keeps_two_asset_universe() -> None:
    frame = pd.DataFrame(
        {
            "MSFT": [0.01, 0.002, -0.004, 0.006, 0.003, 0.005],
            "NVDA": [0.02, -0.01, 0.015, -0.004, 0.007, 0.012],
        },
        index=pd.date_range("2024-01-01", periods=6, freq="B"),
    )
    selected = screen_universe(frame, ScreenerConfig(max_assets=2))
    assert set(selected) == {"MSFT", "NVDA"}


def test_research_supports_single_asset(monkeypatch) -> None:
    prices = pd.DataFrame(
        {"MSFT": np.linspace(100.0, 125.0, 80)},
        index=pd.date_range("2023-01-01", periods=80, freq="B"),
    )

    def fake_loader(_config: MarketDataConfig) -> pd.DataFrame:
        return prices

    monkeypatch.setattr("quant_core.research.load_price_history", fake_loader)
    report = run_research(
        ResearchConfig(
            market_data=MarketDataConfig(tickers=("MSFT",)),
            screener=ScreenerConfig(max_assets=1),
        )
    )
    assert report.selected_tickers == ["MSFT"]
    assert report.mv_weights == {"MSFT": 1.0}
    assert report.mvsk_weights == {"MSFT": 1.0}
    assert report.diagnostics["mvsk_method"] == "single_asset_no_optimization"
    assert report.equity_curves["mvsk"]


def test_returns_are_percent_changes_for_full_market_tickers() -> None:
    prices = pd.DataFrame(
        {"600519.SS": [100.0, 110.0, 99.0], "0700.HK": [200.0, 220.0, 242.0]},
        index=pd.date_range("2024-01-01", periods=3, freq="B"),
    )
    returns = prices_to_returns(prices)
    assert np.isclose(returns.loc[returns.index[0], "600519.SS"], 0.10)
    assert np.isclose(returns.loc[returns.index[1], "600519.SS"], -0.10)
    assert np.isclose(returns.loc[returns.index[1], "0700.HK"], 0.10)
