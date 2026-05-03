"use client";

import { LanguageToggle } from "@/components/LanguageToggle";
import { type Language, useLanguage } from "@/lib/i18n";
import Link from "next/link";

type TutorialCopy = {
  back: string;
  eyebrow: string;
  title: string;
  intro: string;
  sections: { title: string; body: string; bullets: string[] }[];
  workflowTitle: string;
  workflow: string[];
  warningTitle: string;
  warning: string;
};

const tutorialCopy = {
  en: {
    back: "Back to dashboard",
    eyebrow: "Beginner Guide",
    title: "Understand every number before you trust a backtest.",
    intro:
      "This page explains the dashboard in plain English. You do not need to know advanced portfolio theory to start: read from top to bottom, then run the demo and compare MVSK with the mean-variance baseline.",
    sections: [
      {
        title: "1. Research Setup",
        body:
          "The left panel controls the experiment. Tickers are the stock symbols you want to study. The MVSK profile tells the optimizer what kind of portfolio you prefer: balanced, skew-focused, kurtosis-focused, or defensive.",
        bullets: [
          "Start with 8 to 20 liquid large-cap stocks so the report is easy to inspect.",
          "Use kurtosis-focused when you care more about extreme downside events.",
          "Use balanced when you want a neutral first comparison against MV."
        ]
      },
      {
        title: "2. MVSK Return and MV Return",
        body:
          "These cards show annualized return in the test period. MV is the classic mean-variance portfolio. MVSK adds skewness and kurtosis, so it can reshape the return distribution instead of only balancing mean and variance.",
        bullets: [
          "Higher return is attractive, but never judge a strategy by return alone.",
          "Compare return together with Sharpe, drawdown, CVaR, and concentration.",
          "If MVSK beats MV only by taking huge concentration risk, be skeptical."
        ]
      },
      {
        title: "3. Sharpe Lift",
        body:
          "Sharpe Lift is MVSK Sharpe minus MV Sharpe. Sharpe roughly measures how much return you got per unit of volatility. A positive value means MVSK had better risk-adjusted performance in this run.",
        bullets: [
          "A small positive lift is useful only if it survives different time windows.",
          "A very large lift should be checked for data leakage or overfitting.",
          "Sharpe does not fully capture tail risk, which is why CVaR matters."
        ]
      },
      {
        title: "4. Active Share",
        body:
          "Active Share tells you how different the MVSK portfolio is from the MV portfolio. If it is near zero, both methods picked almost the same allocation. If it is high, MVSK made a materially different bet.",
        bullets: [
          "High active share is not automatically good; it means model choice matters.",
          "Low active share means higher moments did not change the portfolio much.",
          "Use it to decide whether MVSK adds an economically meaningful difference."
        ]
      },
      {
        title: "5. Equity Curve",
        body:
          "The equity curve shows how one dollar would grow during the test period. The green line is MVSK and the violet line is MV. Smooth growth with smaller drawdowns is usually healthier than a single late spike.",
        bullets: [
          "Look for when MVSK wins: calm markets, rallies, or stress periods.",
          "Check whether outperformance comes from steady gains or one lucky jump.",
          "If curves cross often, the edge may be regime dependent."
        ]
      },
      {
        title: "6. MVSK Weights",
        body:
          "Weights show how much capital is allocated to each stock. A 20% weight means 20 cents of every dollar goes into that ticker. This project uses long-only simplex weights, so weights are non-negative and sum to 100%.",
        bullets: [
          "Too much weight in one stock means concentration risk.",
          "Effective assets in diagnostics summarizes diversification.",
          "Treat surprising weights as questions to investigate, not blind instructions."
        ]
      },
      {
        title: "7. YAND Diagnostics",
        body:
          "Diagnostics explain how the optimizer behaved. KKT residual measures how close the solution is to first-order optimality. Iterations show solver effort. The method field tells whether the run used direct or PCG reduced solves.",
        bullets: [
          "Lower KKT residual means the optimizer stopped closer to a stationary point.",
          "More iterations can be normal for larger or more anisotropic universes.",
          "Diagnostics help separate financial results from numerical accidents."
        ]
      }
    ],
    workflowTitle: "How to apply it to stock analysis",
    workflow: [
      "Choose a clear universe: for example, mega-cap tech, dividend stocks, or sector ETFs.",
      "Run the research with one MVSK profile and compare against MV.",
      "Inspect return, Sharpe, drawdown, CVaR, active share, and weights together.",
      "Repeat on different train/test windows. A robust idea should not depend on one lucky split.",
      "Add realistic trading costs before trusting any result.",
      "Write down the hypothesis before changing parameters, otherwise you are just curve-fitting."
    ],
    warningTitle: "Important warning",
    warning:
      "The dashboard is a research assistant, not an investment adviser. Backtests can fail in live markets because of data quality, liquidity, costs, regime changes, and overfitting."
  },
  zh: {
    back: "返回控制台",
    eyebrow: "新手教程",
    title: "先看懂每个数字，再相信任何回测。",
    intro:
      "这个页面用金融小白也能理解的语言解释前端里的每个区域。你不需要先懂高级组合优化：从上往下读一遍，再运行 demo，对比 MVSK 和经典均值-方差组合即可。",
    sections: [
      {
        title: "1. 研究参数",
        body:
          "左侧面板控制本次实验。股票代码就是你想研究的股票池。MVSK 偏好配置告诉优化器你更想要哪种组合：均衡型、偏度优先、峰度优先或防御型。",
        bullets: [
          "新手建议先选 8 到 20 只流动性好的大盘股，方便人工检查结果。",
          "更关心极端下跌时，可以选择峰度优先。",
          "第一次对比 MV 基线时，建议先用均衡型。"
        ]
      },
      {
        title: "2. MVSK 年化收益与 MV 年化收益",
        body:
          "这两个卡片显示测试期的年化收益。MV 是经典均值-方差组合。MVSK 额外考虑偏度和峰度，因此不只是在收益和波动之间权衡，还会尝试重塑收益分布。",
        bullets: [
          "收益更高当然好，但绝不能只看收益判断策略。",
          "要和 Sharpe、最大回撤、CVaR、持仓集中度一起看。",
          "如果 MVSK 只是靠重仓一两只股票赢了 MV，要非常谨慎。"
        ]
      },
      {
        title: "3. Sharpe 提升",
        body:
          "Sharpe 提升等于 MVSK Sharpe 减去 MV Sharpe。Sharpe 大致衡量每承受一份波动，换来了多少收益。正数表示这次实验里 MVSK 的风险调整后表现更好。",
        bullets: [
          "小幅正提升只有在多个时间窗口都稳定时才有参考价值。",
          "特别夸张的提升要排查未来函数、数据泄漏和过拟合。",
          "Sharpe 不足以描述尾部风险，所以还要看 CVaR。"
        ]
      },
      {
        title: "4. 主动份额",
        body:
          "主动份额表示 MVSK 组合和 MV 组合有多不一样。接近 0 说明两种方法选出的权重差不多；数值较高说明 MVSK 做出了明显不同的配置。",
        bullets: [
          "主动份额高不代表一定好，只代表模型选择影响很大。",
          "主动份额低说明高阶矩没有显著改变组合。",
          "它能帮助你判断 MVSK 是否带来有经济意义的差异。"
        ]
      },
      {
        title: "5. 净值曲线",
        body:
          "净值曲线展示测试期内 1 美元会如何增长。绿色线是 MVSK，紫色线是 MV。通常，持续平稳上涨且回撤更小，比最后突然暴涨一次更健康。",
        bullets: [
          "观察 MVSK 是在平稳期、上涨期还是压力期赢了 MV。",
          "检查超额收益来自持续优势，还是某一次幸运跳升。",
          "如果两条线频繁交叉，说明策略可能非常依赖市场状态。"
        ]
      },
      {
        title: "6. MVSK 持仓权重",
        body:
          "权重表示每只股票分配多少资金。20% 权重表示每 1 美元里有 20 美分投向该股票。本项目使用 long-only simplex 权重，所以权重非负且总和为 100%。",
        bullets: [
          "单只股票权重过高意味着集中度风险。",
          "诊断里的有效持仓数可以概括分散程度。",
          "看到反直觉权重时，应把它当作研究问题，而不是直接照抄下单。"
        ]
      },
      {
        title: "7. YAND 诊断",
        body:
          "诊断区解释优化器本身的运行情况。KKT residual 衡量解距离一阶最优条件有多近；iterations 表示迭代次数；method 表示本次使用 direct 还是 PCG reduced solve。",
        bullets: [
          "KKT residual 越低，说明优化器越接近稳定解。",
          "股票数更多、几何更各向异性时，迭代次数变多很正常。",
          "诊断能帮助你区分金融结果和数值求解偶然性。"
        ]
      }
    ],
    workflowTitle: "如何应用到股票量化分析",
    workflow: [
      "先定义清晰股票池，例如科技大盘股、高股息股票或某个行业 ETF。",
      "选择一个 MVSK 偏好配置，运行研究并和 MV 基线比较。",
      "同时查看收益、Sharpe、最大回撤、CVaR、主动份额和持仓权重。",
      "换不同训练/测试窗口重复实验。稳健想法不应该只依赖一次幸运切分。",
      "加入真实交易成本后再评估结果是否还有意义。",
      "改参数之前先写下假设，否则很容易变成曲线拟合。"
    ],
    warningTitle: "重要提醒",
    warning:
      "这个 dashboard 是研究助手，不是投资顾问。回测可能因为数据质量、流动性、交易成本、市场状态变化和过拟合而在实盘中失效。"
  }
} satisfies Record<Language, TutorialCopy>;

export default function TutorialPage() {
  const { language, setLanguage } = useLanguage();
  const t = tutorialCopy[language];

  return (
    <main className="grain min-h-screen px-6 py-6 text-ice md:px-10">
      <nav className="mx-auto flex max-w-7xl items-center justify-between">
        <Link className="flex items-center gap-3 text-white/80 transition hover:text-white" href="/">
          <span className="brand-logo grid h-12 w-12 place-items-center rounded-2xl border border-white/70 p-1.5">
            <img className="h-full w-full object-contain" src="/fintastech-logo-white-bg.svg" alt="FintasTech logo" />
          </span>
          <span className="hidden rounded-full border border-white/15 px-4 py-2 text-sm md:inline-flex">{t.back}</span>
        </Link>
        <div className="flex items-center gap-3">
          <Link className="rounded-full border border-white/15 px-4 py-2 text-sm text-white/70 transition hover:text-white md:hidden" href="/">
            {t.back}
          </Link>
          <LanguageToggle language={language} onChange={setLanguage} />
        </div>
      </nav>

      <section className="mx-auto max-w-5xl py-16">
        <p className="mb-5 inline-flex rounded-full border border-mint/20 bg-mint/10 px-4 py-2 text-sm text-mint">
          {t.eyebrow}
        </p>
        <h1 className="display-tight font-display text-5xl font-medium leading-[0.95] md:text-7xl">{t.title}</h1>
        <p className="mt-6 max-w-3xl text-lg leading-8 text-white/68">{t.intro}</p>
      </section>

      <section className="mx-auto grid max-w-7xl gap-5 pb-12 lg:grid-cols-[1fr_360px]">
        <div className="grid gap-5">
          {t.sections.map((section) => (
            <article key={section.title} className="glass rounded-[1.75rem] p-6">
              <h2 className="font-display text-3xl font-medium italic">{section.title}</h2>
              <p className="mt-4 leading-7 text-white/68">{section.body}</p>
              <div className="mt-5 grid gap-3">
                {section.bullets.map((bullet) => (
                  <div key={bullet} className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-sm leading-6 text-white/72">
                    {bullet}
                  </div>
                ))}
              </div>
            </article>
          ))}
        </div>

        <aside className="glass h-fit rounded-[1.75rem] p-6 lg:sticky lg:top-6">
          <h2 className="font-display text-3xl font-medium italic">{t.workflowTitle}</h2>
          <ol className="mt-5 space-y-4">
            {t.workflow.map((step, index) => (
              <li key={step} className="flex gap-3 text-sm leading-6 text-white/72">
                <span className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-mint/15 text-mint">
                  {index + 1}
                </span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
          <div className="mt-6 rounded-2xl border border-violet/25 bg-violet/10 p-4">
            <h3 className="font-semibold text-violet">{t.warningTitle}</h3>
            <p className="mt-2 text-sm leading-6 text-white/68">{t.warning}</p>
          </div>
        </aside>
      </section>
    </main>
  );
}
