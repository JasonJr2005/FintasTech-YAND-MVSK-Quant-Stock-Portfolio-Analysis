from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .simplex import effective_number


@dataclass(frozen=True)
class BacktestConfig:
    periods_per_year: int = 252
    transaction_cost_bps: float = 5.0


@dataclass
class BacktestResult:
    equity_curve: list[dict[str, float | str]]
    metrics: dict[str, float]


def run_static_backtest(
    returns: pd.DataFrame,
    weights: np.ndarray,
    config: BacktestConfig | None = None,
) -> BacktestResult:
    config = config or BacktestConfig()
    weights = np.asarray(weights, dtype=float)
    portfolio_returns = returns.to_numpy(dtype=float) @ weights
    one_time_cost = config.transaction_cost_bps / 10_000.0 * float(np.abs(weights).sum())
    if portfolio_returns.size:
        portfolio_returns[0] -= one_time_cost

    equity = np.cumprod(1.0 + portfolio_returns)
    drawdown = equity / np.maximum.accumulate(equity) - 1.0
    metrics = compute_metrics(portfolio_returns, config.periods_per_year)
    metrics["max_drawdown"] = float(drawdown.min()) if drawdown.size else 0.0
    metrics["effective_assets"] = effective_number(weights)
    metrics["top_5_weight"] = float(np.sort(weights)[-5:].sum()) if weights.size >= 5 else float(weights.sum())

    curve = [
        {"date": str(index.date() if hasattr(index, "date") else index), "equity": float(value)}
        for index, value in zip(returns.index, equity, strict=False)
    ]
    return BacktestResult(equity_curve=curve, metrics=metrics)


def compute_metrics(returns: np.ndarray, periods_per_year: int = 252) -> dict[str, float]:
    returns = np.asarray(returns, dtype=float)
    if returns.size == 0:
        return {
            "annual_return": 0.0,
            "annual_volatility": 0.0,
            "sharpe": 0.0,
            "sortino": 0.0,
            "cvar_1": 0.0,
            "cvar_5": 0.0,
        }
    annual_return = float((np.prod(1.0 + returns) ** (periods_per_year / returns.size)) - 1.0)
    annual_vol = float(np.std(returns, ddof=0) * np.sqrt(periods_per_year))
    downside = returns[returns < 0]
    downside_vol = float(np.std(downside, ddof=0) * np.sqrt(periods_per_year)) if downside.size else 0.0
    return {
        "annual_return": annual_return,
        "annual_volatility": annual_vol,
        "sharpe": annual_return / annual_vol if annual_vol > 1e-12 else 0.0,
        "sortino": annual_return / downside_vol if downside_vol > 1e-12 else 0.0,
        "cvar_1": _cvar(returns, 0.01),
        "cvar_5": _cvar(returns, 0.05),
    }


def _cvar(returns: np.ndarray, q: float) -> float:
    cutoff = float(np.quantile(returns, q))
    tail = returns[returns <= cutoff]
    return float(tail.mean()) if tail.size else cutoff
