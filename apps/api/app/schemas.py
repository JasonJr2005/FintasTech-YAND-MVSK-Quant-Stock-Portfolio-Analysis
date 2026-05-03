from __future__ import annotations

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    tickers: list[str] = Field(
        default_factory=lambda: [
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
        ]
    )
    start: str = "2020-01-01"
    end: str | None = None
    interval: str = "1d"
    max_assets: int = Field(default=10, ge=1, le=80)
    mvsk_preset: str = "kurtosis-focused"
    train_ratio: float = Field(default=0.7, gt=0.2, lt=0.95)
    transaction_cost_bps: float = Field(default=5.0, ge=0.0, le=200.0)


class DemoConfigResponse(BaseModel):
    tickers: list[str]
    presets: list[str]
    start: str
    interval: str
