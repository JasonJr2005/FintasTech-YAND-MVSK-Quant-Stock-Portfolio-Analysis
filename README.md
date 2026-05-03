# FintasTech YAND-MVSK

<p align="center">
  <img src="logo/logo.svg" alt="FintasTech logo" width="132" />
</p>

<p align="center">
  <strong>把丘成桐团队的大规模高阶矩组合优化思想，变成一个开箱即用的量化研究系统。</strong>
</p>

<p align="center">
  <a href="#english">English</a> ·
  <a href="https://arxiv.org/abs/2604.25378">Paper</a> ·
  <a href="./docs/paper-to-code.md">Paper-to-Code</a> ·
  <a href="LICENSE">MIT License</a>
</p>

> FintasTech 是研究与教育工具，不是投资顾问，也不提供投资建议。它的价值在于帮助你更快发现、比较和验证可能具有盈利潜力的组合配置，而不是承诺任何收益。



输入一组股票 ticker，FintasTech 会自动完成数据下载、股票筛选、MV/MVSK 权重优化、基线对比、回测曲线和风险指标展示，让你用几分钟完成一次原本需要大量手工拼接的量化组合研究。

## 出发点

很多量化工具只做“均值-方差”或普通回测。FintasTech 更进一步：它把
[Yau’s Affine-Normal Descent for Large-Scale Unrestricted Higher-Moment Portfolio Optimization](https://arxiv.org/abs/2604.25378)
中的核心思想工程化，试图让高阶矩组合优化真正可用。

传统 MVSK 很强，但难落地：偏度和峰度能捕捉非对称收益与尾部风险，可显式协偏度/协峰度张量会随资产数量爆炸。论文的关键突破是直接在收益矩阵上做精确 sample-oracle 计算，避免构造巨大高阶张量。FintasTech 将这个思路变成可运行系统。

它可以帮助你回答这些更接近实战的问题：

- 这组股票按高阶矩优化后，历史上是否比经典 MV 组合更好？
- 收益提升来自真实分布改善，还是只是重仓某几只股票？
- Sharpe、最大回撤、CVaR、有效持仓数是否同时改善？
- MVSK 给出的权重和 MV 差异有多大，是否值得进一步研究？
- 换成美股、A 股或港股 ticker 后，结果是否仍然稳健？

## 核心功能

- **多市场研究**：支持 Yahoo Finance ticker，例如 `AAPL`、`MSFT`、`600519.SS`、`000001.SZ`、`0700.HK`、`9988.HK`。
- **自动数据管线**：下载价格数据，转成收益率矩阵，并缓存到本地 Parquet。
- **可解释股票筛选**：基于缺失率、均值、波动率、动量等指标筛选股票池。
- **YAND-MVSK 权重优化**：实现 MVSK sample oracle、simplex 约束、direct/PCG reduced solve、精确四次线搜索。
- **MV 基线对照**：同一训练/测试切分下比较经典 mean-variance 和 MVSK。
- **收益与风险报告**：年化收益、波动率、Sharpe、Sortino、最大回撤、CVaR、active share、有效持仓数、KKT residual。
- **精美双语前端**：英文默认，可切换中文；包含 dashboard 和新手教程页。
- **API 可集成**：FastAPI `/research/run`，便于后续接入任务调度、批量研究或自定义数据源。

## 使用场景

- 个人投资者：快速比较一组候选股票的组合权重和历史风险收益。
- 量化研究者：把 MVSK 高阶矩优化加入自己的研究流程。
- 金融学生：用可视化 dashboard 理解均值、方差、偏度、峰度和回测指标。
- 开源开发者：基于清晰的 Python core + FastAPI + Next.js 架构继续扩展。

## 快速开始

第一次安装依赖：

```bash
make setup
```

之后日常启动只需要：

```bash
make dev
```

打开 `http://localhost:3000`，点击 **Run research** 即可运行完整研究流程。

常用命令：

```bash
make api    # 只启动 FastAPI
make web    # 只启动前端
make test   # Python tests + Next.js build
```

没有 `make` 时：

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
npm --prefix apps/web install
.venv/bin/uvicorn apps.api.app.main:app --reload
npm --prefix apps/web run dev
```

## 输入格式

请直接输入 Yahoo Finance 完整 ticker：

- 美股：`AAPL`, `MSFT`, `NVDA`
- A 股：`600519.SS`, `000001.SZ`
- 港股：`0700.HK`, `9988.HK`

## 项目结构

```text
apps/
  api/                 FastAPI research service
  web/                 Next.js bilingual dashboard
packages/
  quant_core/          Python quant engine and YAND-MVSK solver
docs/                  Paper-to-code notes and usage guides
tests/                 Core verification tests
logo/                  Original FintasTech logo assets
```

## 学术来源与引用

本项目受以下论文启发，非论文作者官方实现。请优先引用原论文：

```bibtex
@article{wang2026yandmvsk,
  title   = {Yau's Affine-Normal Descent for Large-Scale Unrestricted Higher-Moment Portfolio Optimization},
  author  = {Wang, Ya-Juan and Niu, Yi-Shuai and Sheshmani, Artan and Yau, Shing-Tung},
  journal = {arXiv preprint arXiv:2604.25378},
  year    = {2026},
  url     = {https://arxiv.org/abs/2604.25378}
}
```

相关背景：

- Niu, Yi-Shuai, Artan Sheshmani, and Shing-Tung Yau. *Yau’s Affine Normal Descent: Algorithmic Framework and Convergence Analysis*. arXiv:2603.28448.
- Niu, Yi-Shuai, Artan Sheshmani, and Shing-Tung Yau. *Affine Normal Directions via Log-Determinant Geometry: Scalable Computation under Sparse Polynomial Structure*. arXiv:2604.01163.

## License

代码与文档采用 MIT License，见 [`LICENSE`](LICENSE)。

FintasTech logo和品牌素材为本项目原创品牌资产，不包含在 MIT License 中。未经项目所有者明确许可，不得复制、改作、再分发或用于其他项目品牌；引用本项目时的合理展示除外。

## 免责声明

本项目可能帮助用户更高效地发现和验证具有盈利潜力的组合配置，但它不是投资顾问，也不提供投资建议。回测结果可能受到数据质量、幸存者偏差、未来函数、交易成本、流动性、过拟合和市场状态变化影响。任何真实资金决策都应经过独立验证、压力测试和风险控制。

---

## English

**Turn large-scale higher-moment portfolio optimization into a usable quant research system.**

[中文](#fintastech-yand-mvsk) · [Paper](https://arxiv.org/abs/2604.25378) · [Paper-to-Code](docs/paper-to-code.md) · [MIT License](LICENSE)

> FintasTech is a research and education tool. It is not an investment adviser and does not provide investment advice. Its value is to help users discover, compare, and validate portfolio configurations with potential profit relevance faster, not to promise returns.

Enter a list of stock tickers. FintasTech downloads market data, screens the universe, optimizes MV/MVSK weights, compares against a baseline, generates backtest curves, and displays risk diagnostics so that a portfolio research run that used to require manual stitching can be completed in minutes.

## Motivation

Many quant tools stop at mean-variance optimization or generic backtesting. FintasTech goes further:
it turns the core ideas from
[Yau’s Affine-Normal Descent for Large-Scale Unrestricted Higher-Moment Portfolio Optimization](https://arxiv.org/abs/2604.25378)
into an engineering system, making higher-moment portfolio research easier to use.

MVSK is powerful but hard to scale. Skewness and kurtosis can capture asymmetric returns and tail behavior, while explicit coskewness and cokurtosis tensors explode as the asset universe grows. The paper's key breakthrough is to compute exact sample oracles directly from the return matrix, avoiding huge higher-order tensors. FintasTech turns that idea into a runnable system.

It helps answer practical research questions:

- Does a higher-moment optimized portfolio beat the classic MV portfolio historically?
- Did the return improvement come from a better distribution shape or just a few concentrated bets?
- Did Sharpe, max drawdown, CVaR, and effective number of assets improve together?
- How different are MVSK weights from MV weights, and is the difference worth deeper research?
- Do results remain stable when you switch between US, A-share, and Hong Kong tickers?

## Core Features

- **Multi-market research**: supports Yahoo Finance tickers such as `AAPL`, `MSFT`, `600519.SS`, `000001.SZ`, `0700.HK`, and `9988.HK`.
- **Automated data pipeline**: downloads price data, converts it into a return matrix, and caches data locally as Parquet.
- **Explainable stock screening**: screens the universe using missing ratio, mean return, volatility, and momentum.
- **YAND-MVSK optimizer** with exact sample oracles, simplex constraints, direct/PCG reduced solves, and exact quartic line search.
- **MV baseline comparison**: compares classic mean-variance and MVSK under the same train/test split.
- **Return and risk report**: annual return, volatility, Sharpe, Sortino, max drawdown, CVaR, active share, effective assets, and KKT residual.
- **Polished bilingual frontend**: English by default, Chinese toggle available; includes a dashboard and beginner tutorial.
- **Composable API**: FastAPI `/research/run`, ready for task schedulers, batch research, or custom data sources.

## Use Cases

- Individual investors: quickly compare portfolio weights and historical risk/return for a candidate stock list.
- Quant researchers: add MVSK higher-moment optimization to an existing research process.
- Finance students: use a visual dashboard to understand mean, variance, skewness, kurtosis, and backtest metrics.
- Open-source developers: extend a clean Python core + FastAPI + Next.js architecture.

## Quick Start

Install dependencies once:

```bash
make setup
```

After that, start daily development with:

```bash
make dev
```

Open `http://localhost:3000` and click **Run research** to run the full workflow.

Common commands:

```bash
make api    # FastAPI only
make web    # Frontend only
make test   # Python tests + Next.js build
```

Without `make`:

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
npm --prefix apps/web install
.venv/bin/uvicorn apps.api.app.main:app --reload
npm --prefix apps/web run dev
```

## Ticker Format

Enter full Yahoo Finance tickers directly:

- US stocks: `AAPL`, `MSFT`, `NVDA`
- A-shares: `600519.SS`, `000001.SZ`
- Hong Kong stocks: `0700.HK`, `9988.HK`

## Project Layout

```text
apps/
  api/                 FastAPI research service
  web/                 Next.js bilingual dashboard
packages/
  quant_core/          Python quant engine and YAND-MVSK solver
docs/                  Paper-to-code notes and usage guides
tests/                 Core verification tests
logo/                  Original FintasTech logo assets
```

## Citation

This project is inspired by the following paper and is not the authors' official implementation. Please cite the original paper first:

```bibtex
@article{wang2026yandmvsk,
  title   = {Yau's Affine-Normal Descent for Large-Scale Unrestricted Higher-Moment Portfolio Optimization},
  author  = {Wang, Ya-Juan and Niu, Yi-Shuai and Sheshmani, Artan and Yau, Shing-Tung},
  journal = {arXiv preprint arXiv:2604.25378},
  year    = {2026},
  url     = {https://arxiv.org/abs/2604.25378}
}
```

Related background:

- Niu, Yi-Shuai, Artan Sheshmani, and Shing-Tung Yau. *Yau’s Affine Normal Descent: Algorithmic Framework and Convergence Analysis*. arXiv:2603.28448.
- Niu, Yi-Shuai, Artan Sheshmani, and Shing-Tung Yau. *Affine Normal Directions via Log-Determinant Geometry: Scalable Computation under Sparse Polynomial Structure*. arXiv:2604.01163.

## License

Code and documentation are released under the MIT License. See [`LICENSE`](LICENSE).

The FintasTech logo and brand assets are original project assets and are not covered by the MIT License. They may not be copied, modified, redistributed, or used as another project's brand without explicit permission from the project owner, except for reasonable references to this project.

## Disclaimer

This project can help users research portfolio configurations with potential profit relevance, but it
is not an investment adviser, does not provide investment advice, and is not a live trading system. Backtest results can be distorted by data quality, survivorship bias, look-ahead bias, transaction costs, liquidity, overfitting, and regime changes. Any real-money decision should be made only after independent validation, stress testing, and risk control.