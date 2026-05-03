from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from .backtest import BacktestConfig, run_static_backtest
from .data import MarketDataConfig, load_price_history, prices_to_returns
from .mv import solve_mean_variance
from .optimizer import YANDConfig, YANDMVSKOptimizer
from .oracle import MVSKCoefficients, MVSKOracle
from .screening import ScreenerConfig, screen_universe
from .simplex import effective_number


@dataclass(frozen=True)
class ResearchConfig:
    market_data: MarketDataConfig = MarketDataConfig()
    screener: ScreenerConfig = ScreenerConfig()
    backtest: BacktestConfig = BacktestConfig()
    mvsk_preset: str = "kurtosis-focused"
    train_ratio: float = 0.7


@dataclass
class ResearchReport:
    selected_tickers: list[str]
    mv_weights: dict[str, float]
    mvsk_weights: dict[str, float]
    mv_metrics: dict[str, float]
    mvsk_metrics: dict[str, float]
    diagnostics: dict[str, float | int | str | bool]
    equity_curves: dict[str, list[dict[str, float | str]]]

    def to_dict(self) -> dict:
        return asdict(self)


def run_research(config: ResearchConfig) -> ResearchReport:
    prices = load_price_history(config.market_data)
    returns = prices_to_returns(prices)
    selected = screen_universe(returns, config.screener)
    if len(selected) < 1:
        raise RuntimeError("Screening left no assets")

    selected_returns = returns[selected].dropna(how="all").fillna(0.0)
    split = _train_test_split_index(len(selected_returns), config.train_ratio)
    train = selected_returns.iloc[:split]
    test = selected_returns.iloc[split:]

    if len(selected) == 1:
        return _single_asset_report(selected, train, test, config)

    coefficients = _scale_coefficients(train, MVSKCoefficients.preset(config.mvsk_preset))
    oracle = MVSKOracle(train.to_numpy(dtype=float), coefficients)
    optimizer = YANDMVSKOptimizer(oracle, YANDConfig(max_iter=100))
    mvsk_result = optimizer.solve()
    mv_weights = solve_mean_variance(train.to_numpy(dtype=float))

    mv_backtest = run_static_backtest(test, mv_weights, config.backtest)
    mvsk_backtest = run_static_backtest(test, mvsk_result.weights, config.backtest)
    mv_weight_map = _weight_map(selected, mv_weights)
    mvsk_weight_map = _weight_map(selected, mvsk_result.weights)

    diagnostics: dict[str, float | int | str | bool] = {
        "mvsk_objective": mvsk_result.objective,
        "mvsk_kkt_residual": mvsk_result.kkt_residual,
        "mvsk_iterations": mvsk_result.iterations,
        "mvsk_converged": mvsk_result.converged,
        "mvsk_method": mvsk_result.method,
        "mv_effective_assets": effective_number(mv_weights),
        "mvsk_effective_assets": effective_number(mvsk_result.weights),
        "active_share": 0.5 * float(np.abs(mvsk_result.weights - mv_weights).sum()),
        "train_samples": int(len(train)),
        "test_samples": int(len(test)),
    }

    return ResearchReport(
        selected_tickers=selected,
        mv_weights=mv_weight_map,
        mvsk_weights=mvsk_weight_map,
        mv_metrics=mv_backtest.metrics,
        mvsk_metrics=mvsk_backtest.metrics,
        diagnostics=diagnostics,
        equity_curves={"mv": mv_backtest.equity_curve, "mvsk": mvsk_backtest.equity_curve},
    )


def _single_asset_report(
    selected: list[str],
    train: pd.DataFrame,
    test: pd.DataFrame,
    config: ResearchConfig,
) -> ResearchReport:
    weights = np.ones(1, dtype=float)
    mv_backtest = run_static_backtest(test, weights, config.backtest)
    mvsk_backtest = run_static_backtest(test, weights, config.backtest)
    weight_map = _weight_map(selected, weights)
    diagnostics: dict[str, float | int | str | bool] = {
        "mvsk_objective": 0.0,
        "mvsk_kkt_residual": 0.0,
        "mvsk_iterations": 0,
        "mvsk_converged": True,
        "mvsk_method": "single_asset_no_optimization",
        "mv_effective_assets": 1.0,
        "mvsk_effective_assets": 1.0,
        "active_share": 0.0,
        "train_samples": int(len(train)),
        "test_samples": int(len(test)),
    }
    return ResearchReport(
        selected_tickers=selected,
        mv_weights=weight_map,
        mvsk_weights=weight_map,
        mv_metrics=mv_backtest.metrics,
        mvsk_metrics=mvsk_backtest.metrics,
        diagnostics=diagnostics,
        equity_curves={"mv": mv_backtest.equity_curve, "mvsk": mvsk_backtest.equity_curve},
    )


def _train_test_split_index(length: int, train_ratio: float) -> int:
    if length < 2:
        raise RuntimeError("Not enough return samples for a train/test split")
    return max(1, min(int(length * train_ratio), length - 1))


def _scale_coefficients(returns: pd.DataFrame, base: MVSKCoefficients) -> MVSKCoefficients:
    equal = np.ones(returns.shape[1]) / returns.shape[1]
    oracle = MVSKOracle(returns.to_numpy(dtype=float), MVSKCoefficients())
    moments = oracle.moments(equal)
    eps = 1e-10
    return MVSKCoefficients(
        mean=base.mean / max(abs(moments["mean"]), eps),
        variance=base.variance / max(abs(moments["variance"]), eps),
        skewness=base.skewness / max(abs(moments["skewness"]), eps),
        kurtosis=base.kurtosis / max(abs(moments["kurtosis"]), eps),
    )


def _weight_map(tickers: list[str], weights: np.ndarray) -> dict[str, float]:
    return {ticker: float(weight) for ticker, weight in zip(tickers, weights, strict=False)}
