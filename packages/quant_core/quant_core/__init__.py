"""Core quantitative research engine for FintasTech."""

from .backtest import BacktestConfig, BacktestResult, run_static_backtest
from .data import MarketDataConfig, load_price_history
from .mv import solve_mean_variance
from .optimizer import YANDConfig, YANDMVSKOptimizer, YANDResult
from .oracle import MVSKCoefficients, MVSKOracle
from .research import ResearchConfig, ResearchReport, run_research
from .screening import ScreenerConfig, screen_universe

__all__ = [
    "BacktestConfig",
    "BacktestResult",
    "MarketDataConfig",
    "MVSKCoefficients",
    "MVSKOracle",
    "ResearchConfig",
    "ResearchReport",
    "ScreenerConfig",
    "YANDConfig",
    "YANDMVSKOptimizer",
    "YANDResult",
    "load_price_history",
    "run_research",
    "run_static_backtest",
    "screen_universe",
    "solve_mean_variance",
]
