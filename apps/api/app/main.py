from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from quant_core import BacktestConfig, MarketDataConfig, ResearchConfig, ScreenerConfig, run_research

from .schemas import DemoConfigResponse, ResearchRequest

app = FastAPI(
    title="FintasTech YAND-MVSK API",
    description="Research API for YAND-MVSK higher-moment portfolio optimization.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/demo-config", response_model=DemoConfigResponse)
def demo_config() -> DemoConfigResponse:
    defaults = MarketDataConfig()
    return DemoConfigResponse(
        tickers=list(defaults.tickers),
        presets=["balanced", "skew-focused", "kurtosis-focused", "defensive"],
        start=defaults.start,
        interval=defaults.interval,
    )


@app.post("/research/run")
def run_research_endpoint(request: ResearchRequest) -> dict:
    config = ResearchConfig(
        market_data=MarketDataConfig(
            tickers=tuple(ticker.upper().strip() for ticker in request.tickers if ticker.strip()),
            start=request.start,
            end=request.end,
            interval=request.interval,
        ),
        screener=ScreenerConfig(max_assets=request.max_assets),
        backtest=BacktestConfig(transaction_cost_bps=request.transaction_cost_bps),
        mvsk_preset=request.mvsk_preset,
        train_ratio=request.train_ratio,
    )
    return run_research(config).to_dict()
