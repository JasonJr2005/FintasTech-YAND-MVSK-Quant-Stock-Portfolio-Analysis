"use client";

import { LanguageToggle } from "@/components/LanguageToggle";
import { formatPercent, type Language, useLanguage } from "@/lib/i18n";
import Link from "next/link";
import { useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

type Report = {
  selected_tickers: string[];
  mv_weights: Record<string, number>;
  mvsk_weights: Record<string, number>;
  mv_metrics: Record<string, number>;
  mvsk_metrics: Record<string, number>;
  diagnostics: Record<string, number | string | boolean>;
  equity_curves: {
    mv: { date: string; equity: number }[];
    mvsk: { date: string; equity: number }[];
  };
};

type MessageKey = "demo" | "running" | "live" | "error";

const copy = {
  en: {
    navConsole: "Launch Console",
    tutorial: "Tutorial",
    eyebrow: "Paper-to-product: exact higher-moment portfolio optimization",
    headline: "Quant research without tensor explosions.",
    intro:
      "This platform implements the YAND-MVSK idea: evaluate mean, variance, skewness and kurtosis directly from the return matrix, then compare higher-moment allocations against exact mean-variance baselines.",
    chips: ["Exact sample oracle", "Quartic line search", "Simplex aware", "MV baseline"],
    traceTitle: "Optimization Trace",
    traceSteps: ["Return matrix R", "Centered map A", "YAND direction", "MVSK weights"],
    setup: "Research Setup",
    tickers: "Tickers",
    tickerHint: "Enter full Yahoo Finance tickers. US: AAPL/MSFT. A-shares: 600519.SS/000001.SZ. HK: 0700.HK/9988.HK.",
    profile: "MVSK profile",
    profiles: {
      balanced: "Balanced",
      "skew-focused": "Skew focused",
      "kurtosis-focused": "Kurtosis focused",
      defensive: "Defensive"
    },
    run: "Run research",
    runningButton: "Running...",
    messages: {
      demo: "Demo report loaded. Connect the API to run live yfinance research.",
      running: "Running FastAPI research pipeline...",
      live: "Live report generated from yfinance data.",
      error: "Using built-in demo because API is unavailable"
    },
    metrics: {
      mvskReturn: "MVSK Return",
      mvReturn: "MV Return",
      sharpeLift: "Sharpe Lift",
      activeShare: "Active Share"
    },
    backtest: "Backtest",
    curveTitle: "MVSK versus MV equity curve",
    selectedAssets: "selected assets",
    weights: "MVSK Weights",
    diagnostics: "YAND Diagnostics"
  },
  zh: {
    navConsole: "进入控制台",
    tutorial: "新手教程",
    eyebrow: "论文方法产品化：精确高阶矩组合优化",
    headline: "不用张量爆炸，也能做高阶矩量化研究。",
    intro:
      "本平台实现 YAND-MVSK 思路：直接从收益率矩阵计算均值、方差、偏度和峰度，并将高阶矩组合与经典均值-方差基线进行对照。",
    chips: ["精确样本 Oracle", "精确四次线搜索", "Simplex 约束", "MV 基线"],
    traceTitle: "优化流程",
    traceSteps: ["收益矩阵 R", "中心化映射 A", "YAND 方向", "MVSK 权重"],
    setup: "研究参数",
    tickers: "股票代码",
    tickerHint: "请输入 Yahoo Finance 完整 ticker。美股：AAPL/MSFT；A股：600519.SS/000001.SZ；港股：0700.HK/9988.HK。",
    profile: "MVSK 偏好配置",
    profiles: {
      balanced: "均衡型",
      "skew-focused": "偏度优先",
      "kurtosis-focused": "峰度优先",
      defensive: "防御型"
    },
    run: "运行研究",
    runningButton: "运行中...",
    messages: {
      demo: "已加载内置演示报告。连接 API 后可运行真实 yfinance 数据研究。",
      running: "正在运行 FastAPI 研究流程...",
      live: "已基于 yfinance 数据生成实时报告。",
      error: "API 暂不可用，当前使用内置演示"
    },
    metrics: {
      mvskReturn: "MVSK 年化收益",
      mvReturn: "MV 年化收益",
      sharpeLift: "Sharpe 提升",
      activeShare: "主动份额"
    },
    backtest: "回测",
    curveTitle: "MVSK 与 MV 净值曲线对比",
    selectedAssets: "只入选资产",
    weights: "MVSK 持仓权重",
    diagnostics: "YAND 诊断"
  }
} satisfies Record<Language, Record<string, unknown>>;

const defaultReport: Report = {
  selected_tickers: ["NVDA", "MSFT", "AAPL", "AVGO", "LLY", "JPM", "COST", "META"],
  mv_weights: {
    NVDA: 0.21,
    MSFT: 0.16,
    AAPL: 0.13,
    AVGO: 0.11,
    LLY: 0.1,
    JPM: 0.1,
    COST: 0.1,
    META: 0.09
  },
  mvsk_weights: {
    NVDA: 0.18,
    MSFT: 0.17,
    AAPL: 0.12,
    AVGO: 0.14,
    LLY: 0.13,
    JPM: 0.07,
    COST: 0.11,
    META: 0.08
  },
  mv_metrics: {
    annual_return: 0.214,
    annual_volatility: 0.223,
    sharpe: 0.96,
    max_drawdown: -0.188,
    cvar_1: -0.034,
    effective_assets: 6.7
  },
  mvsk_metrics: {
    annual_return: 0.268,
    annual_volatility: 0.219,
    sharpe: 1.22,
    max_drawdown: -0.151,
    cvar_1: -0.029,
    effective_assets: 7.1
  },
  diagnostics: {
    mvsk_objective: -0.742,
    mvsk_kkt_residual: 0.000003,
    mvsk_iterations: 48,
    mvsk_converged: true,
    mvsk_method: "direct",
    active_share: 0.11,
    train_samples: 864,
    test_samples: 371
  },
  equity_curves: {
    mv: [
      { date: "2023-01", equity: 1 },
      { date: "2023-04", equity: 1.04 },
      { date: "2023-07", equity: 1.08 },
      { date: "2023-10", equity: 1.03 },
      { date: "2024-01", equity: 1.16 },
      { date: "2024-04", equity: 1.23 },
      { date: "2024-07", equity: 1.28 }
    ],
    mvsk: [
      { date: "2023-01", equity: 1 },
      { date: "2023-04", equity: 1.06 },
      { date: "2023-07", equity: 1.13 },
      { date: "2023-10", equity: 1.1 },
      { date: "2024-01", equity: 1.24 },
      { date: "2024-04", equity: 1.35 },
      { date: "2024-07", equity: 1.44 }
    ]
  }
};

export default function Home() {
  const { language, setLanguage } = useLanguage();
  const t = copy[language];
  const [tickers, setTickers] = useState("AAPL,MSFT,NVDA,AMZN,GOOGL,META,JPM,LLY,V,XOM,AVGO,COST");
  const [preset, setPreset] = useState("kurtosis-focused");
  const [report, setReport] = useState<Report>(defaultReport);
  const [loading, setLoading] = useState(false);
  const [messageKey, setMessageKey] = useState<MessageKey>("demo");
  const [errorText, setErrorText] = useState("");

  const chartData = useMemo(() => {
    const mvByDate = new Map(report.equity_curves.mv.map((point) => [point.date, point.equity]));
    return report.equity_curves.mvsk.map((point) => ({
      date: point.date,
      MVSK: point.equity,
      MV: mvByDate.get(point.date) ?? point.equity
    }));
  }, [report]);

  async function runLiveResearch() {
    setLoading(true);
    setMessageKey("running");
    setErrorText("");
    try {
      const response = await fetch("http://localhost:8000/research/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tickers: tickers.split(",").map((ticker) => ticker.trim()).filter(Boolean),
          start: "2020-01-01",
          interval: "1d",
          max_assets: 10,
          mvsk_preset: preset,
          train_ratio: 0.7,
          transaction_cost_bps: 5
        })
      });
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }
      setReport((await response.json()) as Report);
      setMessageKey("live");
    } catch (error) {
      setMessageKey("error");
      setErrorText((error as Error).message);
    } finally {
      setLoading(false);
    }
  }

  const message =
    messageKey === "error" && errorText
      ? `${t.messages.error}: ${errorText}`
      : t.messages[messageKey];

  return (
    <main className="grain min-h-screen px-6 py-6 text-ice md:px-10">
      <nav className="mx-auto flex max-w-7xl items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="brand-logo grid h-12 w-12 place-items-center rounded-2xl border border-white/70 p-1.5">
            <img className="h-full w-full object-contain" src="/fintastech-logo-white-bg.svg" alt="FintasTech logo" />
          </div>
          <div>
            <p className="brand-wordmark text-base font-semibold uppercase italic text-violet">Finta$tech</p>
            <h1 className="font-display text-xl italic text-white/92">YAND-MVSK Research OS</h1>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Link className="hidden rounded-full border border-white/15 px-4 py-2 text-sm text-white/70 transition hover:text-white md:inline-flex" href="/tutorial">
            {t.tutorial}
          </Link>
          <LanguageToggle language={language} onChange={setLanguage} />
          <a className="rounded-full border border-white/15 px-4 py-2 text-sm text-white/70 transition hover:text-white" href="#dashboard">
            {t.navConsole}
          </a>
        </div>
      </nav>

      <section className="mx-auto grid max-w-7xl gap-8 py-16 lg:grid-cols-[1.05fr_0.95fr]">
        <div>
          <p className="mb-5 inline-flex rounded-full border border-mint/20 bg-mint/10 px-4 py-2 text-sm text-mint">
            {t.eyebrow}
          </p>
          <h2 className="display-tight max-w-4xl font-display text-5xl font-medium leading-[0.95] md:text-7xl">
            {t.headline}
          </h2>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-white/68">
            {t.intro}
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            {t.chips.map((item) => (
              <span key={item} className="rounded-full border border-white/12 bg-white/[0.04] px-4 py-2 text-sm">
                {item}
              </span>
            ))}
          </div>
        </div>
        <div className="glass rounded-[2rem] p-5">
          <div className="rounded-[1.5rem] border border-white/10 bg-black/30 p-5">
            <div className="mb-6 flex items-center justify-between">
              <p className="text-sm uppercase tracking-[0.3em] text-white/45">{t.traceTitle}</p>
              <span className="rounded-full bg-mint/15 px-3 py-1 text-xs text-mint">KKT 3e-6</span>
            </div>
            <div className="grid gap-3">
              {t.traceSteps.map((item, index) => (
                <div key={item} className="flex items-center gap-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                  <span className="grid h-8 w-8 place-items-center rounded-full bg-violet/20 text-violet">
                    {index + 1}
                  </span>
                  <span className="text-white/80">{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="dashboard" className="mx-auto grid max-w-7xl gap-5 pb-12 lg:grid-cols-[320px_1fr]">
        <aside className="glass rounded-[1.75rem] p-5">
          <p className="mb-4 text-sm uppercase tracking-[0.26em] text-white/45">{t.setup}</p>
          <label className="block text-sm text-white/70">{t.tickers}</label>
          <textarea
            className="mt-2 min-h-28 w-full rounded-2xl border border-white/10 bg-black/35 p-3 text-sm outline-none focus:border-mint/50"
            value={tickers}
            onChange={(event) => setTickers(event.target.value)}
          />
          <p className="mt-2 text-xs leading-5 text-white/42">{t.tickerHint}</p>
          <label className="mt-5 block text-sm text-white/70">{t.profile}</label>
          <select
            className="mt-2 w-full rounded-2xl border border-white/10 bg-black/35 p-3 outline-none focus:border-mint/50"
            value={preset}
            onChange={(event) => setPreset(event.target.value)}
          >
            <option value="balanced">{t.profiles.balanced}</option>
            <option value="skew-focused">{t.profiles["skew-focused"]}</option>
            <option value="kurtosis-focused">{t.profiles["kurtosis-focused"]}</option>
            <option value="defensive">{t.profiles.defensive}</option>
          </select>
          <button
            className="mt-5 w-full rounded-2xl bg-mint px-5 py-3 font-semibold text-ink transition hover:scale-[1.01] disabled:opacity-60"
            disabled={loading}
            onClick={runLiveResearch}
          >
            {loading ? t.runningButton : t.run}
          </button>
          <p className="mt-4 text-sm leading-6 text-white/50">{message}</p>
        </aside>

        <div className="grid gap-5">
          <div className="grid gap-4 md:grid-cols-4">
            <Metric label={t.metrics.mvskReturn} value={percent(report.mvsk_metrics.annual_return, language)} accent />
            <Metric label={t.metrics.mvReturn} value={percent(report.mv_metrics.annual_return, language)} />
            <Metric label={t.metrics.sharpeLift} value={(report.mvsk_metrics.sharpe - report.mv_metrics.sharpe).toFixed(2)} accent />
            <Metric label={t.metrics.activeShare} value={percent(Number(report.diagnostics.active_share), language)} />
          </div>

          <div className="glass rounded-[1.75rem] p-5">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.26em] text-white/45">{t.backtest}</p>
                <h3 className="font-display text-3xl">{t.curveTitle}</h3>
              </div>
              <p className="text-sm text-white/50">
                {report.selected_tickers.length} {t.selectedAssets}
              </p>
            </div>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="mvsk" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="5%" stopColor="#7fffd4" stopOpacity={0.55} />
                      <stop offset="95%" stopColor="#7fffd4" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
                  <XAxis dataKey="date" stroke="rgba(255,255,255,0.45)" />
                  <YAxis stroke="rgba(255,255,255,0.45)" />
                  <Tooltip contentStyle={{ background: "#0d1718", border: "1px solid rgba(255,255,255,0.14)" }} />
                  <Area type="monotone" dataKey="MVSK" stroke="#7fffd4" fill="url(#mvsk)" strokeWidth={2} />
                  <Area type="monotone" dataKey="MV" stroke="#9b87ff" fill="transparent" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid gap-5 lg:grid-cols-2">
            <Weights title={t.weights} weights={report.mvsk_weights} language={language} />
            <Diagnostics title={t.diagnostics} diagnostics={report.diagnostics} />
          </div>
        </div>
      </section>
    </main>
  );
}

function Metric({ label, value, accent = false }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="glass rounded-3xl p-5">
      <p className="text-sm text-white/45">{label}</p>
      <p className={accent ? "mt-3 text-3xl font-semibold text-mint" : "mt-3 text-3xl font-semibold"}>
        {value}
      </p>
    </div>
  );
}

function Weights({ title, weights, language }: { title: string; weights: Record<string, number>; language: Language }) {
  const entries = Object.entries(weights).sort((a, b) => b[1] - a[1]);
  return (
    <div className="glass rounded-[1.75rem] p-5">
      <h3 className="mb-4 font-display text-2xl">{title}</h3>
      <div className="space-y-3">
        {entries.map(([ticker, weight]) => (
          <div key={ticker}>
            <div className="mb-1 flex justify-between text-sm">
              <span>{ticker}</span>
              <span className="text-white/55">{percent(weight, language)}</span>
            </div>
            <div className="h-2 rounded-full bg-white/10">
              <div className="h-2 rounded-full bg-mint" style={{ width: `${Math.max(2, weight * 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Diagnostics({ title, diagnostics }: { title: string; diagnostics: Report["diagnostics"] }) {
  return (
    <div className="glass rounded-[1.75rem] p-5">
      <h3 className="mb-4 font-display text-2xl">{title}</h3>
      <div className="grid grid-cols-2 gap-3">
        {Object.entries(diagnostics).map(([key, value]) => (
          <div key={key} className="rounded-2xl border border-white/10 bg-white/[0.03] p-3">
            <p className="text-xs uppercase tracking-[0.18em] text-white/35">{key.replaceAll("_", " ")}</p>
            <p className="mt-2 truncate text-sm text-white/80">{String(value)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function percent(value: number, language: Language) {
  return formatPercent(value, language);
}
