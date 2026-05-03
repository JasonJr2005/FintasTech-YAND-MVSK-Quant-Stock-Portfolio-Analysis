from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class MarketDataConfig:
    tickers: tuple[str, ...] = (
        "AAPL",
        "MSFT",
        "NVDA",
        "AMZN",
        "GOOGL",
        "META",
        "JPM",
        "LLY",
        "V",
        "XOM",
        "AVGO",
        "COST",
    )
    start: str = "2020-01-01"
    end: str | None = None
    interval: str = "1d"
    cache_dir: str = "data/cache"
    auto_adjust: bool = True


def load_price_history(config: MarketDataConfig) -> pd.DataFrame:
    """Load adjusted close prices from cache or yfinance."""

    tickers = tuple(dict.fromkeys(ticker.strip().upper() for ticker in config.tickers if ticker.strip()))
    cache_dir = Path(config.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    end_part = config.end or "latest"
    key = "_".join(tickers)[:120].replace("/", "-")
    cache_file = cache_dir / f"{key}_{config.start}_{end_part}_{config.interval}.parquet"
    if cache_file.exists():
        return pd.read_parquet(cache_file)

    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError("Install yfinance to download market data") from exc

    raw = yf.download(
        list(tickers),
        start=config.start,
        end=config.end,
        interval=config.interval,
        auto_adjust=config.auto_adjust,
        progress=False,
        threads=True,
    )
    if raw.empty:
        raise RuntimeError("No market data returned from yfinance")

    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" in raw.columns.get_level_values(0):
            prices = raw["Close"]
        elif "Adj Close" in raw.columns.get_level_values(0):
            prices = raw["Adj Close"]
        else:
            prices = raw.xs(raw.columns.levels[0][0], axis=1, level=0)
    else:
        prices = raw.to_frame(name=tickers[0]) if isinstance(raw, pd.Series) else raw[["Close"]]
        prices.columns = [tickers[0]]

    prices = prices.sort_index().dropna(axis=1, how="all")
    prices.to_parquet(cache_file)
    return prices


def prices_to_returns(prices: pd.DataFrame) -> pd.DataFrame:
    returns = prices.pct_change(fill_method=None).replace([float("inf"), float("-inf")], pd.NA)
    return returns.dropna(how="all").fillna(0.0)
