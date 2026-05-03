from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ScreenerConfig:
    max_assets: int = 10
    min_assets: int = 2
    min_history_ratio: float = 0.85
    min_mean_quantile: float = 0.25
    max_vol_quantile: float = 0.95
    momentum_window: int = 63


def screen_universe(returns: pd.DataFrame, config: ScreenerConfig) -> list[str]:
    """Rank tickers with simple, explainable research filters."""

    if returns.empty:
        return []
    history_ratio = returns.notna().mean()
    mean_return = returns.mean()
    volatility = returns.std(ddof=0)
    momentum = returns.tail(config.momentum_window).sum()

    eligible = history_ratio >= config.min_history_ratio
    eligible &= mean_return >= mean_return.quantile(config.min_mean_quantile)
    eligible &= volatility <= volatility.quantile(config.max_vol_quantile)

    score = (
        0.45 * _zscore(mean_return)
        + 0.35 * _zscore(momentum)
        - 0.20 * _zscore(volatility)
    )
    ranked_all = score.sort_values(ascending=False)
    ranked_eligible = score[eligible].sort_values(ascending=False)

    # For tiny user-supplied universes, quantile filters can accidentally remove one side of a
    # two-stock comparison. Keep enough ranked names for the optimizer, then let diagnostics show
    # whether the resulting portfolio is useful.
    if len(ranked_eligible) < config.min_assets:
        ranked_eligible = ranked_all.head(max(config.min_assets, min(config.max_assets, len(ranked_all))))

    return list(ranked_eligible.head(config.max_assets).index)


def _zscore(series: pd.Series) -> pd.Series:
    std = float(series.std(ddof=0))
    if std <= 1e-12 or not np.isfinite(std):
        return series * 0.0
    return (series - series.mean()) / std
