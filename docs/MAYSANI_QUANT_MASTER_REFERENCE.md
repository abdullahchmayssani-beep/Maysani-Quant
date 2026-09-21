**MAYSANI QUANT  |  MASTER TECHNICAL REFERENCE**

# **MAYSANI QUANT / AI TRADING**

## Master Technical Reference for Claude and Future Engineering Agents

**Document purpose:** one traceable reference for the Maysani Quant research thesis, source evidence, architecture, engineering rules, roadmap, and V0.1 implementation contract.

**Prepared from:** uploaded repository snapshots, finance course files, project research artifacts, the 129-source evidence audit, prior source-level analysis, and the project decisions recorded in this workstream.

**Status:** design and research dossier; it is not evidence that any strategy is profitable and is not an authorization to trade real capital.

### Core operating principle

**AI interprets and proposes. Mathematics determines edge. Hard-coded risk determines permission. The market determines correctness.**

## Evidence and provenance legend

This document deliberately separates evidence from design opinion. Claude should preserve these distinctions in code comments, architecture decisions, and future research notes.

| **Tag** | **Meaning** | **Engineering consequence** |
| --- | --- | --- |
| **[SOURCE]** | Directly supported by an uploaded source snapshot, course file, evidence-audit record, official documentation, or inspected repository. | May be used as factual input, subject to the stated inspection depth. |
| **[SYNTHESIS]** | A Maysani Quant design decision derived from combining sources and project objectives. | Implement only where the specification says it is current architecture. |
| **[PROPOSED]** | A future idea or parameter that has not yet earned empirical validation. | Must remain configurable/testable; do not describe as proven. |
| **[REJECT]** | A known weakness or design pattern intentionally excluded. | Do not reintroduce without a documented architecture decision and evidence. |
| **[UNVERIFIED]** | A prior claim or external detail that could not be fully verified from the available snapshot. | Treat as a research item, not as a dependency or factual guarantee. |

### Literature-review depth disclosure

[SOURCE] The evidence workbook contains **129 traceable entries**. It is an evidence audit, not a claim that 129 papers were read cover-to-cover. Recorded review depth is: **48** Primary abstract/official page reviewed directly; **61** Abstract/search/official summary assessed; full text not always directly accessible; **4** Abstract/official summary assessed; **16** Official publication/guidance reviewed directly. Each appendix entry preserves the recorded review depth and URL.

## Source inventory completed before drafting

The requested pre-writing inventory was completed first. The following are the primary project artifacts used. Duplicate rendered page images and duplicate generated copies were not treated as independent evidence. SHA-256 hashes are included so a future agent can confirm it is reading the same snapshot.

| **File** | **Role** | **Size** | **SHA-256 (first 16)** |
| --- | --- | --- | --- |
| AgenticTrading-main.zip | Repository ZIP snapshot | 18,947,746 B | 18b9e9a535623806 |
| AI-Trader-main.zip | Repository ZIP snapshot | 1,111,480 B | f6b689ff86cd3aa2 |
| FinCon-main.zip | Repository ZIP snapshot | 1,885 B | 7528db5244b3dbff |
| FINMEM-main.zip | Repository ZIP snapshot | 25,951,858 B | 0f086e4566ee022f |
| FinRL-master.zip | Repository ZIP snapshot | 15,170,439 B | 13860748ae00a40f |
| FinRobot-master.zip | Repository ZIP snapshot | 11,509,640 B | b428a07a95ade072 |
| qlib-main.zip | Repository ZIP snapshot | 5,250,376 B | 32f3da76915542ab |
| QuantDinger-main.zip | Repository ZIP snapshot | 14,147,739 B | 68725dcf1c8cfb50 |
| stockbench-main.zip | Repository ZIP snapshot | 14,029,238 B | 5ba6393890584180 |
| TradingAgents-main.zip | Repository ZIP snapshot | 3,571,877 B | 675b7ab55a920864 |
| Vibe-Trading-main.zip | Repository ZIP snapshot | 49,628,066 B | a8ecc353700133ab |
| FIN826_Foundation I(1).pdf | Course material | 384,434 B | 9e48ba386c545d82 |
| FIN826_Foundation II(1).pdf | Course material | 370,931 B | 0f6d6de0e8865f34 |
| Finance_Python_Notebook_1_BASICS(1).ipynb | Course material | 34,842 B | d3563c50ca893eeb |
| Finance_Python_Notebook_2_LIBRARIES(1).ipynb | Course material | 227,466 B | abcaf15a4b69e568 |
| AI_Trading_Agent_Research_Dossier.md | Prior project research / audit | 10,606 B | 6b96446e2a2dd927 |
| AI_Trading_100plus_Literature_Review.pdf | Prior project research / audit | 35,507 B | 7ac1b957a5ba5fe9 |
| AI_Trading_129_Source_Evidence_Audit.xlsx | Prior project research / audit | 26,100 B | 1d0234dd333a4649 |
| AI_Trading_129_Source_Evidence_Audit_Summary.pdf | Prior project research / audit | 36,939 B | 3a501bd20c4ee1b7 |
| AI_Trading_Repository_Deep_Analysis.docx | Prior project research / audit | 55,129 B | 56ec554a362bf761 |
| AI_Trading_Repository_Deep_Analysis.pdf | Prior project research / audit | 327,116 B | 27569bf042c2d7de |
| AI-Trading-100plus-Research-Synthesis.md | Prior project research / audit | 7,570 B | 00ab87eaf2be1fba |
| AI-Trading-100plus-Source-Catalog.csv | Prior project research / audit | 2,684 B | 744035bc9341788e |

### Repository snapshot inventory

[SOURCE] Eleven repository ZIPs were available locally and unpacked for source-level inspection. LEAN, NautilusTrader, and vectorbt were reviewed through their official public documentation/repositories because local ZIP snapshots were not available. FinCon is a special case: the supplied ZIP contains only a README, so its implementation cannot be source-audited.

| **Snapshot** | **Approx. files inspected/indexed** | **Important top-level areas** |
| --- | --- | --- |
| AI-Trader-main | 149 | assets, docs, research, service, skills |
| AgenticTrading-main | 1,508 | dashboard, docs, orchestration, packaging, credentials/config |
| FINMEM-main | 59 | config, data, data-pipeline, puppy, figures |
| FinCon-main | 1 | README only |
| FinRL-master | 195 | finrl, examples, docs, unit_tests, docker |
| FinRobot-master | 145 | finrobot, experiments, FinNLP, finrobot_equity, tutorials |
| QuantDinger-main | 958 | backend_api_python, mcp_server, docs, ops, scripts |
| TradingAgents-main | 181 | tradingagents, tests, cli, assets |
| Vibe-Trading-main | 2,549 | agent, frontend, desktop, tools, wiki, scripts |
| qlib-main | 626 | qlib, examples, tests, docs, scripts |
| stockbench-main | 12,673 | stockbench, scripts, storage, assets |

## Table of contents

- Executive Overview

- Project Philosophy and Non-Negotiable Principles

- Original Organism Concept

- Complete Repository Research

- Academic / Literature Research

- Key Research Conclusions

- My Finance Course Knowledge

- FX-Specific Knowledge Layer

- Final Maysani Quant Architecture

- Agent Specifications

- Mathematical Decision Framework

- Risk Engine

- Backtesting and Scientific Validation

- Memory and Learning Architecture

- Evolution / Champion-Challenger System

- Multi-Organism Experiment

- Technology Stack

- Development Architecture

- Mobile Control Center

- Full Build Roadmap

- V0.1 Exact Specification

- Things Claude Must Never Do

- Open Questions / Research Backlog

- Source Catalog

Appendices: A. Primary project files and repository traceability; B. Full 129-source evidence audit.

# 1. Executive Overview

**[SYNTHESIS] Maysani Quant is not a generic “AI trading bot.”** It is an autonomous, falsifiable FX research-and-execution system whose intelligence is deliberately split into research, statistical decision-making, deterministic risk control, execution, memory, and evaluation. The first organism begins with a simulated USD 50 account so the system has a concrete survival constraint: capital is scarce, transaction costs matter, and mistakes have consequences. The small account is an experimental identity, not proof that USD 50 is an economically ideal live account size.

The long-term product is an always-on FX organism that observes market and economic information, produces structured evidence, decides BUY / SELL / WAIT through reproducible mathematical logic, sizes and vetoes risk through deterministic code, executes through a controlled broker adapter, learns from resolved outcomes, and records every step in an immutable audit trail. Development and production remain separate so an AI coding agent can continuously research and build without silently changing the live trading system.

**[SOURCE] The research base consistently pushes the architecture away from unconstrained LLM action-taking.** The 129-source review found that financial reasoning ability does not reliably translate into trading alpha; that multi-agent debate is not equivalent to independent evidence; that backtest leakage and repeated trials can manufacture attractive results; and that FX execution, market microstructure, rate expectations, order flow, spread, rollover, and broker rules are first-class concerns. The repository review reaches the same engineering conclusion: no single repository is a safe base unchanged.

**[SYNTHESIS] The project therefore adopts a layered authority model:** specialist AI systems may retrieve, interpret, criticize, summarize, and generate hypotheses; Python/statistical modules calculate forecasts and net expected edge; the risk engine alone determines whether a position is permitted and at what maximum size; the execution layer alone mutates order state; and the market provides the final empirical verdict. Profitability is a hypothesis. It must survive unseen data, realistic costs, walk-forward evaluation, forward paper trading, broker-shadow testing, and eventually controlled live evidence.

# 2. Project Philosophy and Non-Negotiable Principles

- **BUY / SELL / WAIT are explicit actions.** WAIT is not failure; it is the correct action whenever expected net edge does not clear uncertainty and cost thresholds.

- **LLMs never receive unrestricted capital authority.** They can propose structured factors and hypotheses, but they do not choose unbounded position size or bypass portfolio controls.

- **Mathematical/statistical code owns final signal calculation.** The signal must be reproducible from stored inputs, model versions, and configuration.

- **The deterministic risk engine has absolute veto.** No prompt, agent, research result, or coding agent can override it at runtime.

- **Point-in-time integrity is mandatory.** Historical decisions may use only information that was actually available at the decision timestamp; event time and availability time must be distinguished.

- **Costs are part of the strategy.** Spread, slippage, commission, rollover/swap, minimum size, price precision, leverage, margin, rejects, and fill assumptions are not optional post-processing.

- **Every experiment is recorded, including failures.** Hidden discarded trials create a factor zoo and destroy statistical credibility.

- **Validation is promotion, not decoration.** A strategy that cannot survive walk-forward and unseen testing cannot advance because it looked attractive in one backtest.

- **Development and production are different trust domains.** A coding agent can build continuously on branches, but production changes require tests, promotion gates, versioning, and rollback.

- **Semantic memory is context; statistical memory is authority.** Narrative recollection may inform research, but automatic signal weighting must use resolved, measurable performance evidence.

- **Independence must be measured.** Multiple agents using the same model/data are not counted as independent votes; correlation and incremental predictive information must be measured.

- **Simple baselines are permanent controls.** Every sophisticated model must be compared with no-trade, simple deterministic factors, and other relevant controls.

- **Live evidence can invalidate backtest confidence.** Persistent paper/live degradation is a reason to reduce exposure, stop, or re-investigate rather than rationalize the model.

- **Reproducibility beats narrative.** A decision is not considered scientifically useful unless the system can reconstruct the data snapshot, features, model version, costs, risk checks, order intent, fill assumptions, and outcome.

### Explicitly rejected patterns

- **[REJECT]** Final BUY/SELL and size produced only from LLM prose.

- **[REJECT]** Majority vote among correlated AI personas as a substitute for measured forecast skill.

- **[REJECT]** Backtests on midpoint/close prices that ignore executable bid/ask and financing assumptions.

- **[REJECT]** Revised macroeconomic data used as though the revision were known historically.

- **[REJECT]** Optimizing repeatedly on the final holdout set.

- **[REJECT]** Deleting failed experiments, cherry-picking parameter runs, or hiding test failures.

- **[REJECT]** Reinforcement learning before the environment and deterministic baselines are good enough to falsify it.

- **[REJECT]** Letting development agents deploy trading code directly to production without promotion gates.

# 3. Original Organism Concept

**[SYNTHESIS] The organism metaphor is an engineering constraint, not branding.** Each organism has a birth event, initial capital, state, observations, actions, memory, damage, adaptation rules, and a terminal/dead state. This forces the system to reason in terms of wealth paths and survival rather than isolated prediction accuracy.

### Organism state model

| **Concept** | **System meaning** |
| --- | --- |
| Birth capital | Initial simulated equity, USD 50 for the canonical experiment. |
| Equity | Marked account value after realized/unrealized P&L and modeled costs. |
| Food | Genuine net risk-adjusted edge that survives costs and uncertainty. |
| Damage | Trading losses, transaction costs, adverse gaps, financing costs, and drawdowns. |
| Action | BUY, SELL, WAIT plus order-management actions at the execution layer. |
| Memory | Immutable decision/outcome records plus semantic and statistical memory. |
| Evolution | Validated changes to features, weights, risk policies, or models through champion/challenger promotion. |
| Death | A deterministic terminal condition when configured equity/capital constraints are breached. |
| Reproduction / population | Multiple independent organisms running identical information environments with different validated policies. |

Compounding means position sizing and risk constraints use current equity rather than pretending the initial account size never changes. The objective is therefore path-sensitive. A strategy that produces the same arithmetic average return with a catastrophic drawdown is not equivalent to one that preserves the organism.

**[SOURCE] The finance course reinforces this point:** multi-period returns compound multiplicatively, and the geometric growth rate can diverge materially from the arithmetic mean when volatility is high. A +50% period followed by -50% does not restore wealth; the path ends at 75% of the starting value. This is directly relevant to a survival-oriented organism.

### Why USD 50 is useful - and why it can mislead

The USD 50 account is useful because it exposes operational frictions early: minimum trade size, spread, rollover, price precision, margin, and broker constraints can dominate thin expected edges. But it is not a fair way to judge the statistical brain if broker mechanics make a strategy infeasible solely because of account size. The development lab should therefore replay the same brain at multiple simulated capital levels (for example USD 50, 100, 500, and 1,000) to separate **strategy quality** from **capital-scale friction**. This is a proposed experimental design, not a claim that any amount is optimal.

The death threshold remains configurable. In pure V0.1 research it can be zero or a configured minimum equity; before any real-money experiment, the live definition must include broker margin/liquidation mechanics and an earlier protective shutdown threshold. Claude must not hard-code an arbitrary live death threshold as if it were validated.

# 4. Complete Repository Research

This section treats repositories as architecture evidence, not proof of profitable alpha. The local snapshots were inspected directly where available. Online-only items are labeled separately. Licensing notes are planning aids, not legal advice; file-level obligations must be checked before copying code.

## 4.1 TradingAgents - LLM multi-agent research/orchestration

**Inspection basis [SOURCE]:** Local ZIP snapshot v0.5.0: source tree, README, tests, configuration, backtest, portfolio, graph, schemas, market-data validation and point-in-time tests.

**Repository:** [https://github.com/TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
**Paper:** [https://arxiv.org/abs/2412.20138](https://arxiv.org/abs/2412.20138)
**License note:** Apache-2.0 (verified in snapshot).

### Structure and important modules

tradingagents/graph/trading_graph.py, conditional_logic.py, analyst_execution.py, signal_processing.py, checkpointer.py, reflection.py, tradingagents/backtest.py, portfolio.py, agents/schemas.py, dataflows including FRED/SEC/news/symbol utilities and market_data_validator.py; tests include memory point-in-time, market-data validator and portfolio context.

### How the project works

A LangGraph investment-firm workflow routes a dated market state through technical/market, sentiment, news and fundamentals analysts, bull/bear researchers, a trader, risk personas and a portfolio manager. Provider abstraction and Pydantic-style structured outputs improve interface discipline. Recent code includes canonical/verified market snapshots, symbol normalization, portfolio context, checkpointing, and an append-only decision memory with outcome-resolution dates.

### How it runs

Install/configure LLM and data credentials, run CLI or instantiate the graph, then propagate a ticker/date state across analyst and debate nodes. Checkpoints can persist node state. Backtest mode reruns decisions over dates/holding windows rather than simulating an exchange.

### Strengths worth preserving

- Clear role boundaries and graph orchestration.

- Strong point-in-time safeguards, including an important rule that a resolved outcome is not exposed before its resolution date.

- Typed outputs, provider abstraction, symbol normalization, checkpoints and portfolio context.

- Useful audit/memory patterns for reproducible agent research.

### Weaknesses / limitations

- Final recommendation and sizing remain substantially LLM-driven.

- Risk is argumentative/debate-based rather than an absolute quantitative veto.

- Bull/bear agreement can create false confidence because agents often share data/model families.

- Backtest evaluates decisions but does not fully model FX spread, swap, margin, liquidation, order states, and compounding.

### Maysani Quant decision

**[SYNTHESIS]** Reuse orchestration, typed schemas, PIT safeguards, vendor abstraction, checkpointing and outcome-resolution memory. Replace bull-vs-bear theater with hypothesis/falsification and measured independence. Replace final LLM authority with numeric factors -> statistical ensemble -> deterministic risk/execution.

## 4.2 AgenticTrading - Agentic trading infrastructure / execution lab

**Inspection basis [SOURCE]:** Local ZIP: roughly 1,500 files; backend, orchestration, backtest scripts, agent pools, transaction-cost/risk modules, integrations and broad tests inspected.

**Repository:** [https://github.com/Open-Finance-Lab/AgenticTrading](https://github.com/Open-Finance-Lab/AgenticTrading)
**Paper:** [https://arxiv.org/abs/2512.02227](https://arxiv.org/abs/2512.02227)
**License note:** OpenMDW-1.0 (verified); specific reuse should be checked file-by-file.

### Structure and important modules

orchestration/run_simple_backtest.py, run_real_backtest.py, agent-environment/protocol code, portfolio/account layers, transaction-cost and execution-quality modules, risk/alpha agent pools, memory integrations, dashboard/backend, analytics/observability, broker/paper tooling, and hundreds of tests.

### How the project works

A broad Python platform spanning orchestration, agent pools, memory, backtests, transaction-cost modeling, portfolio/account handling, execution-quality analysis, broker/paper integrations, dashboard/auth/database services and protocol boundaries for external agents. It is much closer to a platform than a research notebook.

### How it runs

Environment/config starts backend and orchestration processes; scripts run backtests and agent-vs-baseline experiments. Agents communicate through defined protocols; persistence and analytics record results. Broker/data modules support paper/live-like workflows.

### Strengths worth preserving

- Operational completeness: audit, auth, retries, persistence, analytics, CI and observability.

- Execution-cost concepts such as spread, commission, slippage, market impact/execution quality and cost attribution.

- Portfolio ledgering and protocol separation between intelligence and environment.

- Large test surface exposes engineering failure modes that smaller projects often omit.

### Weaknesses / limitations

- Very large surface area makes correctness harder to reason about.

- Some advertised modules are uneven; documentation may be ahead of implementation in places.

- Equity/crypto orientation dominates; FX is not the center of the domain model.

- Copying the platform wholesale would slow a falsifiable V0.1.

### Maysani Quant decision

**[SYNTHESIS]** Borrow execution-cost accounting, audit/provenance, portfolio ledger and protocol separation. Use it as an operational checklist, not as the base codebase. Keep Maysani Quant much smaller until the science works.

## 4.3 FinRobot - Financial agent platform / RAG / tool use

**Inspection basis [SOURCE]:** Local ZIP: core agents, financial data sources, functional modules, experiments and tutorials inspected.

**Repository:** [https://github.com/AI4Finance-Foundation/FinRobot](https://github.com/AI4Finance-Foundation/FinRobot)
**License note:** Apache-2.0 (verified).

### Structure and important modules

finrobot/agents/workflow.py, agent_library.py, prompts.py, utils.py; data sources for yfinance/FMP/Finnhub/SEC/earnings/Reddit/FinNLP; finrobot/functional/quantitative.py, coding/RAG/charting/reporting utilities; experiments such as multi_factor_agents.py, portfolio_optimization.py, investment_group.py.

### How the project works

AutoGen-style leader/specialist workflows combine financial retrieval, RAG, quantitative tools and Python execution. The most relevant pattern is an LLM that proposes a calculation or research task while deterministic Python performs the computation and returns a structured result.

### How it runs

Configure APIs and model providers, compose agents/workflows or run experiments/tutorials. Specialist agents delegate research and calculations to tools/Python. Outputs are research syntheses rather than a production broker loop.

### Strengths worth preserving

- Excellent AI -> Python computation separation.

- Broad financial tooling and RAG surface.

- Hierarchical specialist teams make domain separation explicit.

- Prompt-level awareness of dated analysis in some experiments.

### Weaknesses / limitations

- Execution and realistic exchange simulation are not the core strength.

- Point-in-time protection is not consistently enforced end-to-end.

- FX is not first-class.

- Agent synthesis can still become an unverified final authority.

### Maysani Quant decision

**[SYNTHESIS]** Adopt the pattern “AI proposes calculation -> Python computes -> structured result returns,” plus RAG and financial-tool ideas. Keep all execution permission in deterministic modules.

## 4.4 FINMEM - Memory architecture for financial agents

**Inspection basis [SOURCE]:** Local ZIP: BrainDB/memory scoring, agent loop, simplified portfolio, data pipeline and train/test structure inspected.

**Repository:** [https://github.com/wilfrid51/FINMEM](https://github.com/wilfrid51/FINMEM)
**Paper:** [https://arxiv.org/abs/2311.13743](https://arxiv.org/abs/2311.13743)
**License note:** MIT (verified).

### Structure and important modules

puppy/agent.py, puppy/portfolio.py, puppy/memorydb.py; scoring modules compound_score.py, importance_score.py, decay.py, access_counter.py, recency.py; data pipeline for filings/news/sentiment/metrics.

### How the project works

Layered short-, mid-, long-term and reflection memories are retrieved with embedding similarity plus importance/recency/access/compound scores. Memories decay, move and are cleaned. The agent consumes filings/news/price, retrieves memory, reflects, trades in a simplified portfolio, receives feedback and updates memory.

### How it runs

Prepare/configure data and model settings, then run the agent loop. Each step retrieves scored memories, forms an action/reflection, updates a simplified portfolio and feeds outcomes back into memory.

### Strengths worth preserving

- Concrete layered memory architecture rather than an abstract “memory” label.

- Recency/importance/access scoring and decay offer useful retrieval mechanics.

- Outcome feedback creates a natural place for post-trade learning.

### Weaknesses / limitations

- Simplified portfolio/execution is not realistic FX accounting.

- Embedding/relevance scores are not evidence that a memory predicts returns.

- Narrative reflection can amplify a mistaken story if allowed to control capital.

### Maysani Quant decision

**[SYNTHESIS]** Keep layered semantic retrieval, but make statistical memory authoritative. Extend memory scores with predictive value, sample size, confidence interval, regime similarity, calibration error and failure rate; never let embedding similarity alone alter position size.

## 4.5 FinCon - Research concept: risk-aware multi-agent learning

**Inspection basis [SOURCE]:** Uploaded ZIP contains only README.md; official public repository inspected previously also exposed README-level material. Full runnable implementation was not available for source audit.

**Repository:** [https://github.com/The-FinAI/FinCon](https://github.com/The-FinAI/FinCon)
**Paper:** [https://arxiv.org/abs/2407.06567](https://arxiv.org/abs/2407.06567)
**License note:** [UNVERIFIED] No reusable implementation/license evidence in supplied ZIP; verify paper/repository terms before reuse.

### Structure and important modules

Supplied snapshot: README only. Any implementation claims must therefore come from the paper/repository description, not local source code.

### How the project works

The published concept describes hierarchical financial agents, risk-aware reasoning, reflection/feedback and conceptual verbal reinforcement. Because implementation was unavailable, the relationship between described architecture and code cannot be verified.

### How it runs

No runnable supplied implementation could be verified.

### Strengths worth preserving

- Useful conceptual emphasis on feedback, risk awareness and specialized agents.

- Promotes learning from prior decisions rather than static prompting.

### Weaknesses / limitations

- No code audit is possible from the supplied snapshot.

- Verbal reinforcement can reinforce narrative errors if disconnected from resolved statistical evidence.

- Commercial-data dependencies can weaken reproducibility.

### Maysani Quant decision

**[SYNTHESIS]** Treat FinCon only as an idea source. Reflection may generate hypotheses, but all weight changes must be predefined, measurable and validated out of sample.

## 4.6 AI-Trader - Live/sequential AI-agent evaluation platform

**Inspection basis [SOURCE]:** Local ZIP: service backend, trading routes, experiment system, research schemas/scripts and tests inspected.

**Repository:** [https://github.com/HKUDS/AI-Trader](https://github.com/HKUDS/AI-Trader)
**Paper:** [https://arxiv.org/abs/2512.10971](https://arxiv.org/abs/2512.10971)
**License note:** [UNVERIFIED] README badge indicates MIT, but the supplied ZIP contained no root LICENSE file; confirm upstream before code reuse.

### Structure and important modules

Server routes for agents, market/trading/signals/challenges/experiments/teams; persistent schemas for positions, predictions, trades, rewards, profit history, quality/experiment assignments and network edges; research scripts for metrics, features and exports.

### How the project works

A service/product environment continuously records agent behavior, trading events and experimental assignments. Challenge/leaderboard machinery makes sequential performance measurable and exportable for research.

### How it runs

Launch the web/service stack, register agents, expose market/trading APIs, record their actions and score experiments/challenges. Research scripts convert the event history into evaluation datasets.

### Strengths worth preserving

- Strong continuous/forward evaluation mindset.

- Rich experiment/event schemas and immutable behavioral data.

- Good separation between agent interfaces and evaluation service.

### Weaknesses / limitations

- More evaluation/product platform than FX execution engine.

- Leaderboard incentives can reward the wrong behavior if survival/risk/calibration are not encoded.

- Realism still depends on underlying market/execution adapters.

### Maysani Quant decision

**[SYNTHESIS]** Adopt experiment/event schema thinking and continuous forward evaluation; replace leaderboard goals with survival, risk-adjusted compounding, calibration and baseline-relative evidence.

## 4.7 Vibe-Trading - Productized agentic research + trading workspace

**Inspection basis [SOURCE]:** Local ZIP: roughly 2,500 files; agent/backtest/live/governance/memory/connectors and extensive tests inspected.

**Repository:** [https://github.com/HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading)
**License note:** MIT at root (verified), with additional attribution/license notes for bundled/re-expressed factor libraries; inspect component provenance before reuse.

### Structure and important modules

Agent core/provider/skills/factor-zoo/portfolio/memory/governance/security modules; backtest engine with perpetual_risk.py, factor_costs.py, correlation.py, validation.py, regime.py, metrics/runner; live/shadow/connectors; large test suite and frontend/desktop product surface.

### How the project works

An agent-rich research workspace spanning factor discovery, backtesting, shadow accounts, governance, live mandates, connectors and product interfaces. It explicitly represents a research -> evidence -> shadow -> live progression.

### How it runs

Configure providers/data connectors, run agent/CLI/API/MCP, let agents invoke research/strategy skills, validate through backtest/shadow layers, then use governed live connectors for permitted workflows.

### Strengths worth preserving

- Promotion ladder from research to shadow to live.

- Governance, security and tool-permission ideas.

- Factor-cost, correlation/regime and attribution modules are directly relevant.

- Strong shadow-account concept and broad testing.

### Weaknesses / limitations

- Huge capability surface increases attack/debug/maintenance burden.

- Many research skills can create uncontrolled hypothesis proliferation and factor-zoo overfitting.

- Cross-asset breadth can dilute FX-specific correctness.

- Agent richness can obscure whether P&L is explained by simple factors.

### Maysani Quant decision

**[SYNTHESIS]** Adopt shadow-account, promotion, governance, factor-cost and attribution ideas. Enforce experiment budgets, trial accounting and one-feature-at-a-time promotion to prevent agentic overfitting.

## 4.8 QuantDinger - Full-stack quant/agent backend

**Inspection basis [SOURCE]:** Local ZIP: backend services/providers/runtime/workers, MCP server, Docker/ops, release-gate and integration tests inspected.

**Repository:** [https://github.com/OpenByteInc/QuantDinger](https://github.com/OpenByteInc/QuantDinger)
**License note:** Apache-2.0 for root/backend and MCP server in supplied snapshot; README notes separate licensing for some frontend/mobile source. Verify component terms.

### Structure and important modules

backend_api_python routes/services/data providers/markets/runtime/workers/observability, mcp_server, ops, Docker compose, scripts, tests for backtest/live execution/risk/timestamps/broker execution/release gates.

### How the project works

A deployment-oriented Python backend normalizes providers and market services, exposes agent-accessible tools through MCP-style boundaries, separates runtime/workers, and includes observability and release-gate infrastructure.

### How it runs

Environment variables plus Docker/local services start backend/runtime; MCP exposes controlled quantitative tools; asynchronous workers run tasks; provider/market abstractions normalize upstream sources.

### Strengths worth preserving

- Clean provider/market/service/runtime separation.

- Tool protocol can keep AI away from raw credentials and implementation internals.

- Strong testing, deployment and release-gate patterns.

- Useful observability/operations examples.

### Weaknesses / limitations

- Full-stack scope is larger than the initial scientific problem.

- Provider breadth risks inconsistent semantics without a canonical data contract.

- UI/product stack should not become a dependency of the core engine.

### Maysani Quant decision

**[SYNTHESIS]** Adopt provider normalization, tool boundaries, observability and release gates. Keep Maysani Quant core independent of UI/product code.

## 4.9 Qlib - Quantitative ML research platform

**Inspection basis [SOURCE]:** Local ZIP: PIT/data, workflow/recorder, backtest/exchange/account, strategy, rolling ML, RL examples and tests inspected.

**Repository:** [https://github.com/microsoft/qlib](https://github.com/microsoft/qlib)
**License note:** MIT (verified).

### Structure and important modules

qlib/data/pit.py; data/cache/operators; backtest account/exchange/decision/executor/position/signal/report/profit attribution; workflow recorder/experiment manager; rolling, high-frequency, order-book and RL examples.

### How the project works

A modular quantitative research platform with explicit point-in-time support, dataset/model workflows, experiment recording, rolling evaluation and a backtest package that separates account, exchange, decision, executor, positions and reporting.

### How it runs

Initialize a data provider, define dataset/model/strategy configuration, run workflows in Python/YAML, record models/results, and route strategy decisions through exchange/executor/account components. Rolling processes update models/predictions over time.

### Strengths worth preserving

- Research discipline and modular ML workflow.

- Explicit PIT support relevant to macro/news integrity.

- Experiment recorder, rolling evaluation and attribution concepts.

- Useful backtest/account/exchange separation.

### Weaknesses / limitations

- Primarily equity/quant-research oriented rather than FX/broker-microstructure native.

- Flexible ML makes massive over-testing easy unless an external trial ledger controls it.

- Production execution is not the comparative strength.

### Maysani Quant decision

**[SYNTHESIS]** Borrow PIT, experiment-recording, rolling-ML and attribution ideas; use stricter multiple-testing controls and a dedicated event-driven execution layer.

## 4.10 StockBench - LLM trading benchmark

**Inspection basis [SOURCE]:** Local ZIP: benchmark engine, agents, data hub, schemas, slippage, reports and packaged benchmark data inspected.

**Repository:** [https://github.com/ChenYXxxx/stockbench](https://github.com/ChenYXxxx/stockbench)
**Paper:** [https://arxiv.org/abs/2510.02209](https://arxiv.org/abs/2510.02209)
**License note:** Apache-2.0 (verified).

### Structure and important modules

stockbench/core/data_hub.py; agent variants; backtest engine/pipeline/datasets/slippage/metrics/reports/visualization; scripts and large stored benchmark dataset.

### How the project works

A benchmark-first pipeline separates dated data/features, agents, executor, backtest and reporting. Sequential evaluation and deterministic/simple baselines make model comparisons more meaningful than anecdotal backtests.

### How it runs

Configure model/data APIs and benchmark scripts; feed dated information sequentially to agents; execute decisions under benchmark assumptions; save metrics/reports. Custom agents can be swapped into the same comparison budget.

### Strengths worth preserving

- Benchmark discipline and controlled comparisons.

- Strong reminder to compare against simple/no-LLM baselines.

- Sequential evaluation reduces some hindsight errors.

- Slippage-aware reporting is better than recommendation-only scoring.

### Weaknesses / limitations

- Stock benchmark, not an FX broker simulator.

- Historical LLM evaluation can still suffer pretraining contamination.

- No complete FX margin/swap/order-state semantics.

- Benchmark success is not proof of live deployable alpha.

### Maysani Quant decision

**[SYNTHESIS]** Build an internal FXBench with identical information budgets, masked dates/provenance checks where relevant, deterministic baselines, cost-aware execution and promotion only on unseen/live-paper evidence.

## 4.11 FinRL - Deep reinforcement learning framework

**Inspection basis [SOURCE]:** Local ZIP: agents, environments, data processor, train/test/trade pipeline, examples and unit tests inspected.

**Repository:** [https://github.com/AI4Finance-Foundation/FinRL](https://github.com/AI4Finance-Foundation/FinRL)
**License note:** MIT (verified).

### Structure and important modules

finrl/agents, finrl/meta/data_processor.py, finrl/trade.py, environments, training/testing scripts and examples.

### How the project works

A Gym-style financial environment plus DRL agents (e.g., A2C/DDPG/PPO/SAC/TD3 through common libraries) supports train -> test/backtest -> trade workflows and market-data integrations.

### How it runs

Prepare data/environment, train policies against a reward function, save models, backtest against controls, then optionally paper/live trade through separate scripts.

### Strengths worth preserving

- Useful framework for formal state/action/reward thinking.

- Makes controlled comparisons across RL algorithms easier.

- Potential later use for bounded execution or policy-selection tasks.

### Weaknesses / limitations

- Reward design can produce pathological behavior that appears profitable in-sample.

- Environment realism is the bottleneck; simplified fills/liquidity make results fragile.

- Adds large complexity before simpler baselines are proved.

### Maysani Quant decision

**[SYNTHESIS]** Postpone RL. Revisit only when the simulator, baselines and cost model are mature; initially restrict RL to bounded tasks such as execution scheduling or regime/policy selection and require it to beat deterministic controls.

## 4.12 QuantConnect LEAN - Mature algorithmic trading engine

**Inspection basis [SOURCE]:** Official QuantConnect/Lean GitHub and documentation reviewed online; local ZIP was not available. Official Engine/Engine.cs and launcher configuration were among the verified references.

**Repository:** [https://github.com/QuantConnect/Lean](https://github.com/QuantConnect/Lean)
**License note:** Apache-2.0 in official repository (verify current version before redistribution).

### Structure and important modules

Official architecture separates setup, data feed, transaction handling, real-time events and result handling; brokerage/fill models isolate venue behavior. Launcher/config.json exposes brokerage-mode configuration including FX-related providers such as OANDA/FXCM in the inspected version.

### How the project works

A plugin-oriented engine with separate DataFeed, strategy/algorithm state, Transaction/Execution, portfolio and Result responsibilities. Backtest/live use different handlers/adapters while retaining consistent algorithm semantics.

### How it runs

Algorithm declares data and logic; setup initializes portfolio/subscriptions; historical data feed and simulated fill/transaction handlers run in backtest; streaming/brokerage handlers replace them in live mode.

### Strengths worth preserving

- Mature separation of concerns and broker/data plugins.

- Proven backtest/live architecture.

- Transaction/fill abstraction and portfolio accounting are important references.

- Rich operational handling of calendars/orders/corporate events.

### Weaknesses / limitations

- Large C# ecosystem is heavy for a small Python-first project.

- Adopting it wholesale would slow AI/quant research iteration.

- Generic multi-asset abstractions may hide FX-specific rules.

### Maysani Quant decision

**[SYNTHESIS]** Copy architectural boundaries, not the entire engine: data feed -> signal/strategy -> transaction/execution -> portfolio -> results, with swappable historical/paper/live adapters.

## 4.13 NautilusTrader - Production-grade event-driven trading engine

**Inspection basis [SOURCE]:** Official NautilusTrader docs/repository reviewed online; local ZIP was not available. Reviewed current concepts, high-level backtesting and live configuration documentation.

**Repository:** [https://github.com/nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader)
**License note:** LGPL-3.0 per official project; verify integration/distribution obligations before adopting.

### Structure and important modules

Rust-native deterministic event core with Python control plane; Strategy/Actor/ExecAlgorithm components; BacktestEngine/BacktestNode, Parquet catalog, normalized domain events, data/execution adapters, LiveNode and reconciliation/persistence concerns.

### How the project works

A deterministic event-driven engine intended to preserve strategy/execution semantics across backtest, sandbox and live. Normalized prices, quantities, orders, positions and events flow through a message bus/cache and venue adapters.

### How it runs

Load historical quotes/trades/bars/order-book data into BacktestEngine or catalog/BacktestNode; register strategies and simulated venues. For live, configure LiveNode and real data/execution adapters while keeping strategy semantics.

### Strengths worth preserving

- Best reviewed reference for research-to-live parity and deterministic event ordering.

- Rich order/domain model and explicit backtest-vs-live differences.

- Rust core offers performance/safety with productive Python control.

- Makes uncertain broker/network outcomes and reconciliation first-class.

### Weaknesses / limitations

- Steep framework complexity if adopted before alpha requirements are known.

- Chosen FX broker may still require custom adapter work.

- Simulation remains limited by historical data granularity; bars cannot reconstruct queue/order-book behavior.

### Maysani Quant decision

**[SYNTHESIS]** Use as the strongest execution-kernel reference. Do not embed it in V0.1 by default; evaluate later once the trading science is stable and the cost of maintaining a custom order-state engine exceeds integration cost.

## 4.14 vectorbt - High-speed vectorized research/backtesting

**Inspection basis [SOURCE]:** Official vectorbt documentation/repository reviewed online; local ZIP was not available.

**Repository:** [https://github.com/polakowo/vectorbt](https://github.com/polakowo/vectorbt)
**License note:** Open-source/community license should be verified from the current upstream repository before redistribution; prior review recorded Apache-2.0, but treat current terms as a pre-reuse check.

### Structure and important modules

Pandas/NumPy vectorized research API, parameter broadcasting, Numba/optional accelerated kernels, indicators/signals/portfolio analytics/drawdowns/visualization, with richer capabilities in commercial editions.

### How the project works

Represents many strategy configurations as multidimensional arrays and evaluates them quickly. This is ideal for hypothesis screening and parameter-sensitivity maps, but it is not the desired live execution kernel.

### How it runs

Load pandas data, generate vectorized signals and parameter grids, broadcast simulations, then compare portfolio/trade/drawdown statistics.

### Strengths worth preserving

- Very fast baseline generation and robustness/sensitivity analysis.

- Composable Python API fits deterministic experiments requested by a research agent.

- Good way to visualize parameter stability rather than one selected optimum.

### Weaknesses / limitations

- Speed makes data snooping dangerously easy.

- Vectorized assumptions are less natural for detailed event/broker state.

- Should not be the production execution engine.

### Maysani Quant decision

**[SYNTHESIS]** Use as a research accelerator only behind the experiment ledger. Promote promising hypotheses into the event-driven simulator before any conclusion about deployable edge.

## 4.15 Repository synthesis: what belongs in Maysani Quant

No reviewed repository is selected as the entire base system. The useful parts form a layered hybrid:

- **TradingAgents:** orchestration, typed outputs, point-in-time safeguards, model/provider abstraction, checkpointing, outcome-resolution memory.

- **FINMEM:** layered semantic memory, upgraded with statistical evidence as the authoritative learning layer.

- **FinRobot:** RAG/financial tools and the “agent asks, Python computes” pattern.

- **AgenticTrading:** execution-cost accounting, protocol boundaries, audit/operational completeness.

- **Vibe-Trading:** shadow-account promotion ladder, governance, factor-cost/correlation/attribution ideas.

- **AI-Trader + StockBench:** continuous/sequential evaluation, experiment schemas and strict baseline comparisons.

- **Qlib + vectorbt:** point-in-time/rolling ML and fast controlled research, respectively.

- **LEAN + NautilusTrader:** clean event-driven data/transaction/portfolio boundaries; Nautilus is the strongest later execution-kernel candidate.

- **FinRL:** later-stage bounded RL experiments only after simulator realism is established.

- **Custom Maysani Quant code:** deterministic FX-specific feature library, statistical ensemble, hard risk, experiment ledger, point-in-time macro/news contracts, survival objective and broker-specific safeguards.

# 5. Academic / Literature Research

The following synthesis is drawn from the 129-entry evidence audit and the previously generated literature review. It is intentionally skeptical: source inclusion does not mean the source is correct, and a published result is not assumed to transfer to our FX universe, horizon, broker, or cost model. The complete audit appears in Appendix B.

## 5.1 LLMs and financial agents

**[SOURCE-derived synthesis]** The evidence is mixed but architecturally useful. Live/sequential benchmarks and contamination-aware studies challenge the assumption that general financial knowledge becomes trading alpha. The strongest project implication is to use LLMs as researchers, event interpreters, structured feature extractors, hypothesis generators and critics. Agent numeracy, retrieval faithfulness and historical contamination must be tested separately from P&L. StockBench-like controls and memory masking/provenance checks are especially relevant.

**Representative evidence-audit entries:**

- **S1: When Agents Trade: Live Multi-Market Trading Benchmark for LLM Agents.** Live multi-market benchmark: architecture/risk style can drive behavior more than model backbone. Project implication: Benchmark agent architecture and risk policy separately from LLM model choice; use live paper evaluation. [[https://arxiv.org/abs/2510.11695](https://arxiv.org/abs/2510.11695)](https://arxiv.org/abs/2510.11695](https://arxiv.org/abs/2510.11695))

- **S3: StockBench: Can LLM Agents Trade Stocks Profitably In Real-world Markets?.** Contamination-aware sequential trading benchmark; most models struggle versus simple baselines. Project implication: Every AI feature must beat no-LLM and simple trading baselines on unseen periods. [[https://arxiv.org/abs/2510.02209](https://arxiv.org/abs/2510.02209)](https://arxiv.org/abs/2510.02209](https://arxiv.org/abs/2510.02209))

- **S5: From Knowing to Doing: A Memory-Controlled Benchmark for LLM Trading Agents on Stock Markets.** Memory-controlled benchmark designed to separate memorized knowledge from actual sequential trading skill. Project implication: Use date/ticker masking and provenance checks when evaluating agent memory or historical reasoning. [[https://arxiv.org/abs/2605.28359](https://arxiv.org/abs/2605.28359)](https://arxiv.org/abs/2605.28359](https://arxiv.org/abs/2605.28359))

- **S6: AlphaForgeBench: Benchmarking End-to-End Trading Strategy Design with Large Language Models.** Reframes LLMs as strategy/factor designers whose outputs are executable and testable. Project implication: Use AI to generate hypotheses/features; deterministic code measures edge and decides whether a factor survives. [[https://arxiv.org/abs/2602.18481](https://arxiv.org/abs/2602.18481)](https://arxiv.org/abs/2602.18481](https://arxiv.org/abs/2602.18481))

- **S7: Finance Agent Benchmark: Benchmarking LLMs on Real-world Financial Research Tasks.** Measures financial research capability rather than assuming trading P&L from general reasoning skill. Project implication: Evaluate research quality separately from trading quality; good analysis is not sufficient evidence of alpha. [[https://arxiv.org/abs/2508.00828](https://arxiv.org/abs/2508.00828)](https://arxiv.org/abs/2508.00828](https://arxiv.org/abs/2508.00828))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.2 Multi-agent systems

**[SOURCE-derived synthesis]** Role specialization can improve decomposition and auditing, but multiple personas do not create independent evidence when they share model families, prompts, inputs or retrieval. Debate can be useful as a falsification mechanism, not as a vote count. Maysani Quant should measure pairwise signal correlation, incremental information, calibration and conditional skill before assigning weight.

**Representative evidence-audit entries:**

- **S1: When Agents Trade: Live Multi-Market Trading Benchmark for LLM Agents.** Live multi-market benchmark: architecture/risk style can drive behavior more than model backbone. Project implication: Benchmark agent architecture and risk policy separately from LLM model choice; use live paper evaluation. [[https://arxiv.org/abs/2510.11695](https://arxiv.org/abs/2510.11695)](https://arxiv.org/abs/2510.11695](https://arxiv.org/abs/2510.11695))

- **S3: StockBench: Can LLM Agents Trade Stocks Profitably In Real-world Markets?.** Contamination-aware sequential trading benchmark; most models struggle versus simple baselines. Project implication: Every AI feature must beat no-LLM and simple trading baselines on unseen periods. [[https://arxiv.org/abs/2510.02209](https://arxiv.org/abs/2510.02209)](https://arxiv.org/abs/2510.02209](https://arxiv.org/abs/2510.02209))

- **S5: From Knowing to Doing: A Memory-Controlled Benchmark for LLM Trading Agents on Stock Markets.** Memory-controlled benchmark designed to separate memorized knowledge from actual sequential trading skill. Project implication: Use date/ticker masking and provenance checks when evaluating agent memory or historical reasoning. [[https://arxiv.org/abs/2605.28359](https://arxiv.org/abs/2605.28359)](https://arxiv.org/abs/2605.28359](https://arxiv.org/abs/2605.28359))

- **S6: AlphaForgeBench: Benchmarking End-to-End Trading Strategy Design with Large Language Models.** Reframes LLMs as strategy/factor designers whose outputs are executable and testable. Project implication: Use AI to generate hypotheses/features; deterministic code measures edge and decides whether a factor survives. [[https://arxiv.org/abs/2602.18481](https://arxiv.org/abs/2602.18481)](https://arxiv.org/abs/2602.18481](https://arxiv.org/abs/2602.18481))

- **S7: Finance Agent Benchmark: Benchmarking LLMs on Real-world Financial Research Tasks.** Measures financial research capability rather than assuming trading P&L from general reasoning skill. Project implication: Evaluate research quality separately from trading quality; good analysis is not sufficient evidence of alpha. [[https://arxiv.org/abs/2508.00828](https://arxiv.org/abs/2508.00828)](https://arxiv.org/abs/2508.00828](https://arxiv.org/abs/2508.00828))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.3 Quantitative finance / machine learning

**[SOURCE-derived synthesis]** Machine-learning research supports nonlinear prediction and representation learning in some financial settings, but predictive improvement is highly sensitive to data splits, costs, market regime and feature design. Complex models must remain downstream of a clean point-in-time feature store and must beat simple baselines under identical walk-forward budgets.

**Representative evidence-audit entries:**

- **S42: Empirical Asset Pricing via Machine Learning.** High-quality ML asset-pricing evidence that nonlinear models can capture predictive structure. Project implication: Use as methodological reference, not direct FX proof; compare nonlinear models to transparent baselines. [[https://www.nber.org/papers/w25398](https://www.nber.org/papers/w25398)](https://www.nber.org/papers/w25398](https://www.nber.org/papers/w25398))

- **S43: Artificial Intelligence Asset Pricing Models.** Modern AI asset-pricing models show flexible models can capture pricing relationships. Project implication: Treat as model-class evidence; require FX-specific replication and interpretability. [[https://www.nber.org/papers/w33351](https://www.nber.org/papers/w33351)](https://www.nber.org/papers/w33351](https://www.nber.org/papers/w33351))

- **S45: Combining Deep Learning and GARCH Models for Financial Volatility and Risk Forecasting.** Hybrid GARCH/deep models improve point volatility in some assets, but risk forecasts do not automatically improve. Project implication: Keep classical GARCH baselines and evaluate volatility forecasts separately from VaR/ES usefulness. [[https://arxiv.org/abs/2310.01063](https://arxiv.org/abs/2310.01063)](https://arxiv.org/abs/2310.01063](https://arxiv.org/abs/2310.01063))

- **S46: GARCH-Informed Neural Networks for Volatility Prediction in Financial Markets.** Hybrid GARCH-informed neural model reports OOS volatility improvements. Project implication: Candidate later model; benchmark against GARCH/EGARCH with FX data before use. [[https://arxiv.org/abs/2410.00288](https://arxiv.org/abs/2410.00288)](https://arxiv.org/abs/2410.00288](https://arxiv.org/abs/2410.00288))

- **S48: A Deep Reinforcement Learning Framework for the Financial Portfolio Management Problem.** Influential DRL portfolio framework but environment assumptions are simplified. Project implication: Study later after realistic deterministic simulator is established. [[https://arxiv.org/abs/1706.10059](https://arxiv.org/abs/1706.10059)](https://arxiv.org/abs/1706.10059](https://arxiv.org/abs/1706.10059))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.4 Backtest validation and overfitting

**[SOURCE-derived synthesis]** This is the strongest cross-cutting body of evidence. PBO, Deflated Sharpe, White/Hansen-style data-snooping work and the multiple-testing literature show that repeated research trials can manufacture attractive statistics. The experiment registry must therefore retain failed trials, track hypothesis families, reserve untouched holdouts, use walk-forward evaluation, and apply corrected inference before promotion.

**Representative evidence-audit entries:**

- **S21: The Probability of Backtest Overfitting.** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability. Project implication: Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253))

- **S22: Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance.** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability. Project implication: Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659))

- **S24: Backtest Overfitting in Financial Markets.** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability. Project implication: Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2731886](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2731886)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2731886](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2731886))

- **S25: The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality.** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability. Project implication: Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551))

- **S26: Stock Portfolio Design and Backtest Overfitting.** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability. Project implication: Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2739335](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2739335)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2739335](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2739335))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.5 FX anomalies and factors

**[SOURCE-derived synthesis]** Currency carry, momentum, value and economic/macro momentum provide economically interpretable baseline families. They should be treated as controls/candidate features, not promised alpha. Expected behavior can decay after publication, vary across regimes and interact with funding/liquidity conditions.

**Representative evidence-audit entries:**

- **S55: Carry Trade and Momentum in Currency Markets.** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum. Project implication: Use as transparent FX baselines and candidate features; never assume persistence after costs or publication. [[https://www.nber.org/papers/w16942](https://www.nber.org/papers/w16942)](https://www.nber.org/papers/w16942](https://www.nber.org/papers/w16942))

- **S56: Currency Carry Trades.** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum. Project implication: Use as transparent FX baselines and candidate features; never assume persistence after costs or publication. [[https://www.nber.org/papers/w16491](https://www.nber.org/papers/w16491)](https://www.nber.org/papers/w16491](https://www.nber.org/papers/w16491))

- **S57: Carry Trades and Currency Crashes.** Carry strategies can exhibit crash risk and negative skew. Project implication: Carry signal must include volatility/liquidity/crash-state controls and strict leverage limits. [[https://www.nber.org/papers/w14473](https://www.nber.org/papers/w14473)](https://www.nber.org/papers/w14473](https://www.nber.org/papers/w14473))

- **S58: The Carry Trade and Fundamentals: Nothing to Fear But FEER Itself.** Conditioning carry on fundamentals can improve risk-adjusted behavior in historical tests. Project implication: Test FEER/value conditioning as a candidate state feature, not a rule. [[https://www.nber.org/papers/w15518](https://www.nber.org/papers/w15518)](https://www.nber.org/papers/w15518](https://www.nber.org/papers/w15518))

- **S59: The Cross-Section of Currency Risk Premia and US Consumption Growth Risk.** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum. Project implication: Use as transparent FX baselines and candidate features; never assume persistence after costs or publication. [[https://www.nber.org/papers/w11104](https://www.nber.org/papers/w11104)](https://www.nber.org/papers/w11104](https://www.nber.org/papers/w11104))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.6 Carry

**[SOURCE-derived synthesis]** Carry is grounded in rate differentials and a long literature on currency risk premia, but crash episodes and funding/liquidity state dependence are central. A carry module should use contemporaneously available rate information, include financing/rollover in net returns, and expose crash-risk/regime variables rather than blindly buying the high-yield currency.

**Representative evidence-audit entries:**

- **S55: Carry Trade and Momentum in Currency Markets.** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum. Project implication: Use as transparent FX baselines and candidate features; never assume persistence after costs or publication. [[https://www.nber.org/papers/w16942](https://www.nber.org/papers/w16942)](https://www.nber.org/papers/w16942](https://www.nber.org/papers/w16942))

- **S56: Currency Carry Trades.** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum. Project implication: Use as transparent FX baselines and candidate features; never assume persistence after costs or publication. [[https://www.nber.org/papers/w16491](https://www.nber.org/papers/w16491)](https://www.nber.org/papers/w16491](https://www.nber.org/papers/w16491))

- **S57: Carry Trades and Currency Crashes.** Carry strategies can exhibit crash risk and negative skew. Project implication: Carry signal must include volatility/liquidity/crash-state controls and strict leverage limits. [[https://www.nber.org/papers/w14473](https://www.nber.org/papers/w14473)](https://www.nber.org/papers/w14473](https://www.nber.org/papers/w14473))

- **S58: The Carry Trade and Fundamentals: Nothing to Fear But FEER Itself.** Conditioning carry on fundamentals can improve risk-adjusted behavior in historical tests. Project implication: Test FEER/value conditioning as a candidate state feature, not a rule. [[https://www.nber.org/papers/w15518](https://www.nber.org/papers/w15518)](https://www.nber.org/papers/w15518](https://www.nber.org/papers/w15518))

- **S59: The Cross-Section of Currency Risk Premia and US Consumption Growth Risk.** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum. Project implication: Use as transparent FX baselines and candidate features; never assume persistence after costs or publication. [[https://www.nber.org/papers/w11104](https://www.nber.org/papers/w11104)](https://www.nber.org/papers/w11104](https://www.nber.org/papers/w11104))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.7 Momentum

**[SOURCE-derived synthesis]** Time-series and cross-sectional currency momentum are useful baseline hypotheses. The implementation should test multiple economically justified horizons under a pre-registered budget, avoid parameter mining, and report turnover/cost sensitivity. Momentum should not be assumed to work in every volatility or mean-reverting regime.

**Representative evidence-audit entries:**

- **S55: Carry Trade and Momentum in Currency Markets.** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum. Project implication: Use as transparent FX baselines and candidate features; never assume persistence after costs or publication. [[https://www.nber.org/papers/w16942](https://www.nber.org/papers/w16942)](https://www.nber.org/papers/w16942](https://www.nber.org/papers/w16942))

- **S56: Currency Carry Trades.** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum. Project implication: Use as transparent FX baselines and candidate features; never assume persistence after costs or publication. [[https://www.nber.org/papers/w16491](https://www.nber.org/papers/w16491)](https://www.nber.org/papers/w16491](https://www.nber.org/papers/w16491))

- **S57: Carry Trades and Currency Crashes.** Carry strategies can exhibit crash risk and negative skew. Project implication: Carry signal must include volatility/liquidity/crash-state controls and strict leverage limits. [[https://www.nber.org/papers/w14473](https://www.nber.org/papers/w14473)](https://www.nber.org/papers/w14473](https://www.nber.org/papers/w14473))

- **S58: The Carry Trade and Fundamentals: Nothing to Fear But FEER Itself.** Conditioning carry on fundamentals can improve risk-adjusted behavior in historical tests. Project implication: Test FEER/value conditioning as a candidate state feature, not a rule. [[https://www.nber.org/papers/w15518](https://www.nber.org/papers/w15518)](https://www.nber.org/papers/w15518](https://www.nber.org/papers/w15518))

- **S59: The Cross-Section of Currency Risk Premia and US Consumption Growth Risk.** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum. Project implication: Use as transparent FX baselines and candidate features; never assume persistence after costs or publication. [[https://www.nber.org/papers/w11104](https://www.nber.org/papers/w11104)](https://www.nber.org/papers/w11104](https://www.nber.org/papers/w11104))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.8 Value

**[SOURCE-derived synthesis]** PPP/value-style currency signals tend to be slower-moving and difficult to time. They may be more useful as long-horizon explanatory/state variables than short-horizon execution triggers. Real-time data availability, publication lag and revision handling matter.

**Representative evidence-audit entries:**

- **S55: Carry Trade and Momentum in Currency Markets.** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum. Project implication: Use as transparent FX baselines and candidate features; never assume persistence after costs or publication. [[https://www.nber.org/papers/w16942](https://www.nber.org/papers/w16942)](https://www.nber.org/papers/w16942](https://www.nber.org/papers/w16942))

- **S56: Currency Carry Trades.** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum. Project implication: Use as transparent FX baselines and candidate features; never assume persistence after costs or publication. [[https://www.nber.org/papers/w16491](https://www.nber.org/papers/w16491)](https://www.nber.org/papers/w16491](https://www.nber.org/papers/w16491))

- **S57: Carry Trades and Currency Crashes.** Carry strategies can exhibit crash risk and negative skew. Project implication: Carry signal must include volatility/liquidity/crash-state controls and strict leverage limits. [[https://www.nber.org/papers/w14473](https://www.nber.org/papers/w14473)](https://www.nber.org/papers/w14473](https://www.nber.org/papers/w14473))

- **S58: The Carry Trade and Fundamentals: Nothing to Fear But FEER Itself.** Conditioning carry on fundamentals can improve risk-adjusted behavior in historical tests. Project implication: Test FEER/value conditioning as a candidate state feature, not a rule. [[https://www.nber.org/papers/w15518](https://www.nber.org/papers/w15518)](https://www.nber.org/papers/w15518](https://www.nber.org/papers/w15518))

- **S59: The Cross-Section of Currency Risk Premia and US Consumption Growth Risk.** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum. Project implication: Use as transparent FX baselines and candidate features; never assume persistence after costs or publication. [[https://www.nber.org/papers/w11104](https://www.nber.org/papers/w11104)](https://www.nber.org/papers/w11104](https://www.nber.org/papers/w11104))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.9 Macro FX

**[SOURCE-derived synthesis]** The Meese-Rogoff lineage remains a warning that macro exchange-rate models are difficult to beat out of sample. Macro variables are therefore evidence inputs, not unilateral trade instructions. The system should quantify incremental predictive value after prices and costs.

**Representative evidence-audit entries:**

- **S77: The Out-of-Sample Failure of Empirical Exchange Rate Models: Sampling Error or Misspecification?.** Classic out-of-sample exchange-rate forecasting failure warns against overconfident macro models. Project implication: Macro agent cannot have unilateral trade authority; compare to random-walk benchmarks. [[https://www.nber.org/books-and-chapters/exchange-rates-and-international-macroeconomics/out-sample-failure-empirical-exchange-rate-models-sampling-error-or-misspecification](https://www.nber.org/books-and-chapters/exchange-rates-and-international-macroeconomics/out-sample-failure-empirical-exchange-rate-models-sampling-error-or-misspecification)](https://www.nber.org/books-and-chapters/exchange-rates-and-international-macroeconomics/out-sample-failure-empirical-exchange-rate-models-sampling-error-or-misspecification](https://www.nber.org/books-and-chapters/exchange-rates-and-international-macroeconomics/out-sample-failure-empirical-exchange-rate-models-sampling-error-or-misspecification))

- **S78: The Six Major Puzzles in International Macroeconomics: Is There a Common Cause?.** Direct evidence on macroeconomic, monetary-policy, and exchange-rate mechanisms relevant to FX forecasting. Project implication: Macro agent should emit structured surprise/state variables; validate incremental value beyond price/carry baselines. [[https://www.nber.org/papers/w7777](https://www.nber.org/papers/w7777)](https://www.nber.org/papers/w7777](https://www.nber.org/papers/w7777))

- **S79: Does Incomplete Spanning in International Financial Markets Help to Explain Exchange Rates?.** Direct evidence on macroeconomic, monetary-policy, and exchange-rate mechanisms relevant to FX forecasting. Project implication: Macro agent should emit structured surprise/state variables; validate incremental value beyond price/carry baselines. [[https://www.nber.org/papers/w22023](https://www.nber.org/papers/w22023)](https://www.nber.org/papers/w22023](https://www.nber.org/papers/w22023))

- **S80: Can Oil Prices Forecast Exchange Rates?.** Commodity prices may forecast some currencies with economic links. Project implication: Test only for commodity-linked currencies; not a generic EUR/USD assumption. [[https://www.nber.org/papers/w17998](https://www.nber.org/papers/w17998)](https://www.nber.org/papers/w17998](https://www.nber.org/papers/w17998))

- **S81: Identifying the Effects of Monetary Policy Shocks on Exchange Rates Using High Frequency Data.** High-frequency policy-surprise identification shows event timing matters for FX response. Project implication: Create event windows and structured surprise variables rather than daily sentiment alone. [[https://www.nber.org/papers/w9660](https://www.nber.org/papers/w9660)](https://www.nber.org/papers/w9660](https://www.nber.org/papers/w9660))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.10 Central banks and monetary-policy surprises

**[SOURCE-derived synthesis]** High-frequency event-study evidence supports the importance of surprises in policy decisions, expected rate paths and communication. The system should model realized-minus-expected surprise, communication/rate-path components, event time and confidence rather than generic positive/negative sentiment.

**Representative evidence-audit entries:**

- **S77: The Out-of-Sample Failure of Empirical Exchange Rate Models: Sampling Error or Misspecification?.** Classic out-of-sample exchange-rate forecasting failure warns against overconfident macro models. Project implication: Macro agent cannot have unilateral trade authority; compare to random-walk benchmarks. [[https://www.nber.org/books-and-chapters/exchange-rates-and-international-macroeconomics/out-sample-failure-empirical-exchange-rate-models-sampling-error-or-misspecification](https://www.nber.org/books-and-chapters/exchange-rates-and-international-macroeconomics/out-sample-failure-empirical-exchange-rate-models-sampling-error-or-misspecification)](https://www.nber.org/books-and-chapters/exchange-rates-and-international-macroeconomics/out-sample-failure-empirical-exchange-rate-models-sampling-error-or-misspecification](https://www.nber.org/books-and-chapters/exchange-rates-and-international-macroeconomics/out-sample-failure-empirical-exchange-rate-models-sampling-error-or-misspecification))

- **S78: The Six Major Puzzles in International Macroeconomics: Is There a Common Cause?.** Direct evidence on macroeconomic, monetary-policy, and exchange-rate mechanisms relevant to FX forecasting. Project implication: Macro agent should emit structured surprise/state variables; validate incremental value beyond price/carry baselines. [[https://www.nber.org/papers/w7777](https://www.nber.org/papers/w7777)](https://www.nber.org/papers/w7777](https://www.nber.org/papers/w7777))

- **S79: Does Incomplete Spanning in International Financial Markets Help to Explain Exchange Rates?.** Direct evidence on macroeconomic, monetary-policy, and exchange-rate mechanisms relevant to FX forecasting. Project implication: Macro agent should emit structured surprise/state variables; validate incremental value beyond price/carry baselines. [[https://www.nber.org/papers/w22023](https://www.nber.org/papers/w22023)](https://www.nber.org/papers/w22023](https://www.nber.org/papers/w22023))

- **S80: Can Oil Prices Forecast Exchange Rates?.** Commodity prices may forecast some currencies with economic links. Project implication: Test only for commodity-linked currencies; not a generic EUR/USD assumption. [[https://www.nber.org/papers/w17998](https://www.nber.org/papers/w17998)](https://www.nber.org/papers/w17998](https://www.nber.org/papers/w17998))

- **S81: Identifying the Effects of Monetary Policy Shocks on Exchange Rates Using High Frequency Data.** High-frequency policy-surprise identification shows event timing matters for FX response. Project implication: Create event windows and structured surprise variables rather than daily sentiment alone. [[https://www.nber.org/papers/w9660](https://www.nber.org/papers/w9660)](https://www.nber.org/papers/w9660](https://www.nber.org/papers/w9660))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.11 FX microstructure

**[SOURCE-derived synthesis]** BIS and related literature describe a fragmented OTC market with electronic venues, dealer/internalization behavior, non-bank liquidity providers, execution algorithms and last-look practices. These details explain why midpoint backtests can mislead and why broker/venue semantics must be isolated behind adapters.

**Representative evidence-audit entries:**

- **S87: The foreign exchange market.** Modern overview of FX market structure and participants. Project implication: Ground execution/data architecture in OTC fragmentation and heterogeneous liquidity. [[https://www.bis.org/publications/working-paper-1094-foreign-exchange-market](https://www.bis.org/publications/working-paper-1094-foreign-exchange-market)](https://www.bis.org/publications/working-paper-1094-foreign-exchange-market](https://www.bis.org/publications/working-paper-1094-foreign-exchange-market))

- **S88: High-frequency trading in the foreign exchange market.** High-frequency FX trading changes liquidity/market dynamics. Project implication: Useful for future intraday design; not required for low-frequency V1. [[https://www.bis.org/publications/high-frequency-trading-foreign-exchange-market](https://www.bis.org/publications/high-frequency-trading-foreign-exchange-market)](https://www.bis.org/publications/high-frequency-trading-foreign-exchange-market](https://www.bis.org/publications/high-frequency-trading-foreign-exchange-market))

- **S89: FX trade execution: complex and highly fragmented.** FX execution is fragmented across venues, dealers and protocols. Project implication: Backtester must not assume a single centralized exchange or universal price. [[https://www.bis.org/publications/qr-201912/fx-trade-execution-complex-and-highly-fragmented](https://www.bis.org/publications/qr-201912/fx-trade-execution-complex-and-highly-fragmented)](https://www.bis.org/publications/qr-201912/fx-trade-execution-complex-and-highly-fragmented](https://www.bis.org/publications/qr-201912/fx-trade-execution-complex-and-highly-fragmented))

- **S90: FX execution algorithms and market functioning.** Execution algorithms change how risk and liquidity are transferred. Project implication: Separate signal alpha from execution quality; add TCA when broker connectivity exists. [[https://www.bis.org/publications/fx-execution-algorithms-and-market-functioning](https://www.bis.org/publications/fx-execution-algorithms-and-market-functioning)](https://www.bis.org/publications/fx-execution-algorithms-and-market-functioning](https://www.bis.org/publications/fx-execution-algorithms-and-market-functioning))

- **S92: Through stormy seas: how fragile is liquidity across asset classes and time?.** Liquidity fragility varies by asset and stress state. Project implication: Introduce spread/liquidity stress regimes and conservative fill assumptions. [[https://www.bis.org/publications/working-paper-1229-through-stormy-seas-how-fragile-liquidity-across-asset-classes-and-time](https://www.bis.org/publications/working-paper-1229-through-stormy-seas-how-fragile-liquidity-across-asset-classes-and-time)](https://www.bis.org/publications/working-paper-1229-through-stormy-seas-how-fragile-liquidity-across-asset-classes-and-time](https://www.bis.org/publications/working-paper-1229-through-stormy-seas-how-fragile-liquidity-across-asset-classes-and-time))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.12 Order flow

**[SOURCE-derived synthesis]** Evans-Lyons-style research supports order flow as an information-bearing variable, especially at shorter horizons, but the effect should not be extrapolated mechanically to long horizons. Retail-accessible data may only provide imperfect proxies; provenance and horizon alignment are essential.

**Representative evidence-audit entries:**

- **S87: The foreign exchange market.** Modern overview of FX market structure and participants. Project implication: Ground execution/data architecture in OTC fragmentation and heterogeneous liquidity. [[https://www.bis.org/publications/working-paper-1094-foreign-exchange-market](https://www.bis.org/publications/working-paper-1094-foreign-exchange-market)](https://www.bis.org/publications/working-paper-1094-foreign-exchange-market](https://www.bis.org/publications/working-paper-1094-foreign-exchange-market))

- **S88: High-frequency trading in the foreign exchange market.** High-frequency FX trading changes liquidity/market dynamics. Project implication: Useful for future intraday design; not required for low-frequency V1. [[https://www.bis.org/publications/high-frequency-trading-foreign-exchange-market](https://www.bis.org/publications/high-frequency-trading-foreign-exchange-market)](https://www.bis.org/publications/high-frequency-trading-foreign-exchange-market](https://www.bis.org/publications/high-frequency-trading-foreign-exchange-market))

- **S89: FX trade execution: complex and highly fragmented.** FX execution is fragmented across venues, dealers and protocols. Project implication: Backtester must not assume a single centralized exchange or universal price. [[https://www.bis.org/publications/qr-201912/fx-trade-execution-complex-and-highly-fragmented](https://www.bis.org/publications/qr-201912/fx-trade-execution-complex-and-highly-fragmented)](https://www.bis.org/publications/qr-201912/fx-trade-execution-complex-and-highly-fragmented](https://www.bis.org/publications/qr-201912/fx-trade-execution-complex-and-highly-fragmented))

- **S90: FX execution algorithms and market functioning.** Execution algorithms change how risk and liquidity are transferred. Project implication: Separate signal alpha from execution quality; add TCA when broker connectivity exists. [[https://www.bis.org/publications/fx-execution-algorithms-and-market-functioning](https://www.bis.org/publications/fx-execution-algorithms-and-market-functioning)](https://www.bis.org/publications/fx-execution-algorithms-and-market-functioning](https://www.bis.org/publications/fx-execution-algorithms-and-market-functioning))

- **S92: Through stormy seas: how fragile is liquidity across asset classes and time?.** Liquidity fragility varies by asset and stress state. Project implication: Introduce spread/liquidity stress regimes and conservative fill assumptions. [[https://www.bis.org/publications/working-paper-1229-through-stormy-seas-how-fragile-liquidity-across-asset-classes-and-time](https://www.bis.org/publications/working-paper-1229-through-stormy-seas-how-fragile-liquidity-across-asset-classes-and-time)](https://www.bis.org/publications/working-paper-1229-through-stormy-seas-how-fragile-liquidity-across-asset-classes-and-time](https://www.bis.org/publications/working-paper-1229-through-stormy-seas-how-fragile-liquidity-across-asset-classes-and-time))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.13 Liquidity

**[SOURCE-derived synthesis]** Liquidity is state-dependent and deteriorates around stress/events. Spread, quote availability, reject rates and slippage should become observable state variables and risk gates. For a small account, minimum size/financing/spread may matter more than market impact, but the architecture should support richer models later.

**Representative evidence-audit entries:**

- **S87: The foreign exchange market.** Modern overview of FX market structure and participants. Project implication: Ground execution/data architecture in OTC fragmentation and heterogeneous liquidity. [[https://www.bis.org/publications/working-paper-1094-foreign-exchange-market](https://www.bis.org/publications/working-paper-1094-foreign-exchange-market)](https://www.bis.org/publications/working-paper-1094-foreign-exchange-market](https://www.bis.org/publications/working-paper-1094-foreign-exchange-market))

- **S88: High-frequency trading in the foreign exchange market.** High-frequency FX trading changes liquidity/market dynamics. Project implication: Useful for future intraday design; not required for low-frequency V1. [[https://www.bis.org/publications/high-frequency-trading-foreign-exchange-market](https://www.bis.org/publications/high-frequency-trading-foreign-exchange-market)](https://www.bis.org/publications/high-frequency-trading-foreign-exchange-market](https://www.bis.org/publications/high-frequency-trading-foreign-exchange-market))

- **S89: FX trade execution: complex and highly fragmented.** FX execution is fragmented across venues, dealers and protocols. Project implication: Backtester must not assume a single centralized exchange or universal price. [[https://www.bis.org/publications/qr-201912/fx-trade-execution-complex-and-highly-fragmented](https://www.bis.org/publications/qr-201912/fx-trade-execution-complex-and-highly-fragmented)](https://www.bis.org/publications/qr-201912/fx-trade-execution-complex-and-highly-fragmented](https://www.bis.org/publications/qr-201912/fx-trade-execution-complex-and-highly-fragmented))

- **S90: FX execution algorithms and market functioning.** Execution algorithms change how risk and liquidity are transferred. Project implication: Separate signal alpha from execution quality; add TCA when broker connectivity exists. [[https://www.bis.org/publications/fx-execution-algorithms-and-market-functioning](https://www.bis.org/publications/fx-execution-algorithms-and-market-functioning)](https://www.bis.org/publications/fx-execution-algorithms-and-market-functioning](https://www.bis.org/publications/fx-execution-algorithms-and-market-functioning))

- **S92: Through stormy seas: how fragile is liquidity across asset classes and time?.** Liquidity fragility varies by asset and stress state. Project implication: Introduce spread/liquidity stress regimes and conservative fill assumptions. [[https://www.bis.org/publications/working-paper-1229-through-stormy-seas-how-fragile-liquidity-across-asset-classes-and-time](https://www.bis.org/publications/working-paper-1229-through-stormy-seas-how-fragile-liquidity-across-asset-classes-and-time)](https://www.bis.org/publications/working-paper-1229-through-stormy-seas-how-fragile-liquidity-across-asset-classes-and-time](https://www.bis.org/publications/working-paper-1229-through-stormy-seas-how-fragile-liquidity-across-asset-classes-and-time))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.14 Transaction costs

**[SOURCE-derived synthesis]** Transaction costs can erase thin statistical edges. Cost analysis must be integrated into expected edge, backtest accounting and promotion criteria. The cost model should be scenario-based until tied to a specific broker and data source; no invented “realistic” constant should be treated as universal.

**Representative evidence-audit entries:**

- **S108: Optimal Liquidation.** Foundational optimal execution tradeoff between risk and impact. Project implication: Architecture reference; small-account V1 likely spread/slippage dominated rather than market-impact dominated. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501))

- **S111: Strategic Risk Management: Out-of-Sample Evidence from the COVID-19 Equity Selloff.** Out-of-sample crisis evidence supports dynamic risk management. Project implication: Stress-test risk throttles on crisis windows rather than optimizing only average periods. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3655196](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3655196)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3655196](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3655196))

- **S113: Trend-Following, Risk-Parity and the Influence of Correlations.** Correlation-aware risk-parity can matter when asset correlations rise. Project implication: If multi-pair portfolio is added, account for changing correlations rather than only inverse volatility. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2673124](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2673124)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2673124](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2673124))

- **S115: Tail Protection for Long Investors: Trend Convexity at Work.** Trend convexity can provide tail protection in diversified settings. Project implication: Use as risk-factor understanding; do not assume a single-pair FX trend strategy has the same protection. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2777657](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2777657)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2777657](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2777657))

- **S117: Market risk terminology - Basel Framework.** Official market-risk terminology and framework. Project implication: Use consistent definitions of risk factors/positions and expected-shortfall concepts. [[https://www.bis.org/committees/bcbs/basel-framework/standard/mar/10/inforce/2023-01-01/published/2020-03-27](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/10/inforce/2023-01-01/published/2020-03-27)](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/10/inforce/2023-01-01/published/2020-03-27](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/10/inforce/2023-01-01/published/2020-03-27))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.15 Execution

**[SOURCE-derived synthesis]** Execution evidence supports explicit order states, TCA, rejection transparency, latency/fill uncertainty and broker-specific constraints. Backtest-live parity is an architectural goal, not a claim that simulated fills equal real fills. Shadow mode should quantify the gap.

**Representative evidence-audit entries:**

- **S108: Optimal Liquidation.** Foundational optimal execution tradeoff between risk and impact. Project implication: Architecture reference; small-account V1 likely spread/slippage dominated rather than market-impact dominated. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501))

- **S111: Strategic Risk Management: Out-of-Sample Evidence from the COVID-19 Equity Selloff.** Out-of-sample crisis evidence supports dynamic risk management. Project implication: Stress-test risk throttles on crisis windows rather than optimizing only average periods. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3655196](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3655196)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3655196](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3655196))

- **S113: Trend-Following, Risk-Parity and the Influence of Correlations.** Correlation-aware risk-parity can matter when asset correlations rise. Project implication: If multi-pair portfolio is added, account for changing correlations rather than only inverse volatility. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2673124](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2673124)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2673124](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2673124))

- **S115: Tail Protection for Long Investors: Trend Convexity at Work.** Trend convexity can provide tail protection in diversified settings. Project implication: Use as risk-factor understanding; do not assume a single-pair FX trend strategy has the same protection. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2777657](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2777657)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2777657](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2777657))

- **S117: Market risk terminology - Basel Framework.** Official market-risk terminology and framework. Project implication: Use consistent definitions of risk factors/positions and expected-shortfall concepts. [[https://www.bis.org/committees/bcbs/basel-framework/standard/mar/10/inforce/2023-01-01/published/2020-03-27](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/10/inforce/2023-01-01/published/2020-03-27)](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/10/inforce/2023-01-01/published/2020-03-27](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/10/inforce/2023-01-01/published/2020-03-27))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.16 Risk management

**[SOURCE-derived synthesis]** No single risk statistic is sufficient. Variance/volatility, drawdown, expected shortfall, leverage/margin, event exposure and system-health risk must be layered. Risk controls are hard permissions, not suggestions from an LLM.

**Representative evidence-audit entries:**

- **S108: Optimal Liquidation.** Foundational optimal execution tradeoff between risk and impact. Project implication: Architecture reference; small-account V1 likely spread/slippage dominated rather than market-impact dominated. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501))

- **S111: Strategic Risk Management: Out-of-Sample Evidence from the COVID-19 Equity Selloff.** Out-of-sample crisis evidence supports dynamic risk management. Project implication: Stress-test risk throttles on crisis windows rather than optimizing only average periods. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3655196](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3655196)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3655196](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3655196))

- **S113: Trend-Following, Risk-Parity and the Influence of Correlations.** Correlation-aware risk-parity can matter when asset correlations rise. Project implication: If multi-pair portfolio is added, account for changing correlations rather than only inverse volatility. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2673124](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2673124)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2673124](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2673124))

- **S115: Tail Protection for Long Investors: Trend Convexity at Work.** Trend convexity can provide tail protection in diversified settings. Project implication: Use as risk-factor understanding; do not assume a single-pair FX trend strategy has the same protection. [[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2777657](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2777657)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2777657](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2777657))

- **S117: Market risk terminology - Basel Framework.** Official market-risk terminology and framework. Project implication: Use consistent definitions of risk factors/positions and expected-shortfall concepts. [[https://www.bis.org/committees/bcbs/basel-framework/standard/mar/10/inforce/2023-01-01/published/2020-03-27](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/10/inforce/2023-01-01/published/2020-03-27)](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/10/inforce/2023-01-01/published/2020-03-27](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/10/inforce/2023-01-01/published/2020-03-27))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.17 Data integrity / point-in-time data

**[SOURCE-derived synthesis]** Availability timestamps and historical macro vintages are mandatory for credible historical decisions. Retrieval and memory must also be point-in-time eligible: a document or resolved trade outcome cannot appear in an earlier decision simply because it exists in the database today.

**Representative evidence-audit entries:**

- **S125: ALFRED Help - vintage economic data.** ALFRED provides vintage-aware macro data. Project implication: Use vintage dates for backtests to prevent revised-data leakage. [[https://alfred.stlouisfed.org/help](https://alfred.stlouisfed.org/help)](https://alfred.stlouisfed.org/help](https://alfred.stlouisfed.org/help))

- **S126: ALFRED Download Data Help.** Explains downloading vintage macro series. Project implication: Implement reproducible vintage-data ingestion. [[https://alfred.stlouisfed.org/help/downloaddata](https://alfred.stlouisfed.org/help/downloaddata)](https://alfred.stlouisfed.org/help/downloaddata](https://alfred.stlouisfed.org/help/downloaddata))

- **S127: ALFRED API documentation.** API documentation enables programmatic vintage queries. Project implication: Build macro data connector against vintage endpoints. [[https://fred.stlouisfed.org/docs/api/fred/alfred.html](https://fred.stlouisfed.org/docs/api/fred/alfred.html)](https://fred.stlouisfed.org/docs/api/fred/alfred.html](https://fred.stlouisfed.org/docs/api/fred/alfred.html))

- **S128: Data Revisions with FRED.** Explains why economic series revisions can materially change historical values. Project implication: Never use latest revised values as if they were known historically. [[https://www.stlouisfed.org/publications/page-one-economics/2022/08/01/data-revisions-with-fred](https://www.stlouisfed.org/publications/page-one-economics/2022/08/01/data-revisions-with-fred)](https://www.stlouisfed.org/publications/page-one-economics/2022/08/01/data-revisions-with-fred](https://www.stlouisfed.org/publications/page-one-economics/2022/08/01/data-revisions-with-fred))

- **S129: Real-Time Data Set for Macroeconomists.** Real-time macro dataset provides another vintage-data source. Project implication: Use for replication/cross-check of point-in-time macro experiments. [[https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/real-time-data-set-for-macroeconomists](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/real-time-data-set-for-macroeconomists)](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/real-time-data-set-for-macroeconomists](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/real-time-data-set-for-macroeconomists))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

## 5.18 Reinforcement learning

**[SOURCE-derived synthesis]** RL remains a later option. The evidence base contains many studies whose environments simplify fills, liquidity or reward design. Maysani Quant should first build a simulator able to falsify RL and require RL to beat deterministic controls on identical data/costs; early uses should be bounded tasks rather than unrestricted portfolio authority.

**Representative evidence-audit entries:**

- **S42: Empirical Asset Pricing via Machine Learning.** High-quality ML asset-pricing evidence that nonlinear models can capture predictive structure. Project implication: Use as methodological reference, not direct FX proof; compare nonlinear models to transparent baselines. [[https://www.nber.org/papers/w25398](https://www.nber.org/papers/w25398)](https://www.nber.org/papers/w25398](https://www.nber.org/papers/w25398))

- **S43: Artificial Intelligence Asset Pricing Models.** Modern AI asset-pricing models show flexible models can capture pricing relationships. Project implication: Treat as model-class evidence; require FX-specific replication and interpretability. [[https://www.nber.org/papers/w33351](https://www.nber.org/papers/w33351)](https://www.nber.org/papers/w33351](https://www.nber.org/papers/w33351))

- **S45: Combining Deep Learning and GARCH Models for Financial Volatility and Risk Forecasting.** Hybrid GARCH/deep models improve point volatility in some assets, but risk forecasts do not automatically improve. Project implication: Keep classical GARCH baselines and evaluate volatility forecasts separately from VaR/ES usefulness. [[https://arxiv.org/abs/2310.01063](https://arxiv.org/abs/2310.01063)](https://arxiv.org/abs/2310.01063](https://arxiv.org/abs/2310.01063))

- **S46: GARCH-Informed Neural Networks for Volatility Prediction in Financial Markets.** Hybrid GARCH-informed neural model reports OOS volatility improvements. Project implication: Candidate later model; benchmark against GARCH/EGARCH with FX data before use. [[https://arxiv.org/abs/2410.00288](https://arxiv.org/abs/2410.00288)](https://arxiv.org/abs/2410.00288](https://arxiv.org/abs/2410.00288))

- **S48: A Deep Reinforcement Learning Framework for the Financial Portfolio Management Problem.** Influential DRL portfolio framework but environment assumptions are simplified. Project implication: Study later after realistic deterministic simulator is established. [[https://arxiv.org/abs/1706.10059](https://arxiv.org/abs/1706.10059)](https://arxiv.org/abs/1706.10059](https://arxiv.org/abs/1706.10059))

**What Maysani Quant must test itself:** whether the effect adds incremental, cost-adjusted, out-of-sample value in the chosen FX universe/horizon, with the exact information budget and broker assumptions used by the production system.

# 6. Key Research Conclusions

### LLMs are better positioned as research organs than unrestricted traders

Live/sequential benchmarks and benchmark-oriented work make direct LLM authority difficult to justify. Use LLMs for retrieval, event interpretation, hypothesis generation, structured extraction and critique; keep numerical forecast/risk/execution deterministic.

### Multi-agent debate is not independent confirmation

Measure correlation, conditional incremental information and calibration. A critic exists to falsify a hypothesis, not to create a second vote.

### Backtest integrity is part of the model

Immutable experiment logging, PIT joins, historical vintages, walk-forward, multiple-testing controls and untouched holdouts are core infrastructure, not optional research hygiene.

### FX is structurally different from equities

OTC fragmentation, rate/funding sensitivity, order flow, carry, dealer/venue behavior, last look and rollover require FX-specific data and execution semantics.

### Execution and risk are part of expected edge

Spread/slippage/swap/reject/margin can turn gross alpha into negative net alpha. The decision engine evaluates edge only after modeled costs and uncertainty.

### Macro information needs release-time awareness

Store observation/reference period, release time, availability time, revision/vintage and source. Model surprise against expectation rather than interpreting a data point without context.

### Carry/momentum/value are baselines, not beliefs

They earn or lose weight through the same unseen validation process as every other signal.

### RL is postponed

First prove that the environment, deterministic baselines and cost accounting are credible; then test RL on bounded tasks.

### Memory is dual

Semantic memory helps context; statistical memory controls trust. Resolved outcomes must never leak backward in time.

### Small capital exposes reality

USD 50 is useful for survival experiments but can be dominated by minimum size/financing/broker rules. Evaluate the brain at multiple simulated capital levels.

### No repository proves the combined system will make money

Repositories demonstrate engineering patterns. Profitability remains an empirical claim that only our own unseen and forward evidence can support.

# 7. My Finance Course Knowledge

The course sources available for this project are FIN826_Foundation I(1).pdf (“The Investment Environment and the Language of Returns”), FIN826_Foundation II(1).pdf (“Risk, Risk Aversion, and Capital Allocation”), and two Python notebooks. This section uses only concepts visible in those supplied materials; it does not invent later course topics.

| **Course concept [SOURCE]** | **Course statement** | **Relevance to Maysani Quant [SYNTHESIS]** | **Architecture location** |
| --- | --- | --- | --- |
| Holding-period return | Net return r_(t+1) = (P_(t+1) + D_(t+1) - P_t) / P_t; gross return R = 1 + r. | Foundation for trade/portfolio P&L and return labels. | Portfolio ledger; feature/label calculation; evaluation. |
| Multi-period compounding | Returns compound multiplicatively; they do not add across time. | Survival and wealth paths matter; arithmetic average can hide wealth destruction. | Organism equity process; geometric growth metrics. |
| Log returns | ln(1+r) is additive over time and often useful statistically; simple returns remain additive across assets. | Useful for time-series features, volatility models and cumulative log wealth, while account P&L still uses correct cash accounting. | Feature engine; model inputs; performance reporting. |
| Arithmetic vs geometric mean | Arithmetic mean estimates one-period average; geometric mean describes realized compound growth; geometric <= arithmetic and gap rises with volatility. Approximation in slides: g ≈ a - 0.5 sigma^2. | Separates forecast expectation from realized wealth growth. | Model evaluation vs organism survival report. |
| Annualization | Under iid assumptions, mean scales with periods and volatility with square root of time; slides warn dependence, volatility clustering and fat tails break naive scaling. | Do not blindly annualize Sharpe/volatility at every horizon. | Metrics library with frequency and serial-correlation disclosure. |
| Excess return | r^e = r - r_f, with horizon-specific risk-free rate known at time t. | Useful for opportunity cost, carry and risk-adjusted evaluation. | Macro/carry layer and evaluation. |
| Stylized facts | Fat tails, non-normality and volatility clustering mean unconditional variance can understate crisis risk. | Risk engine needs more than normal-distribution volatility. | Stress tests, expected shortfall, regime/volatility state. |
| Variance / standard deviation | Course uses variance for tractability but explicitly notes it penalizes upside equally. | Volatility is useful but incomplete as risk. | Risk/state features; position scaling; evaluation. |
| VaR / Expected Shortfall / drawdown | Course compares variance, semivariance, VaR, ES and max drawdown and highlights weaknesses. | No single metric is authoritative. | Layered risk dashboard; stress/tail analysis. |
| Risk aversion and utility | Mean-variance utility in slides: U = E[r] - 0.5 A sigma^2; concavity captures preference for certainty. | Provides conceptual basis for risk penalties and survival-first utility. | Objective design and ensemble/risk penalty research. |
| Capital Allocation Line | For risky portfolio P plus risk-free asset, expected return and standard deviation scale with risky allocation y; CAL slope is Sharpe. | Leverage changes risk/return level, not underlying risk-adjusted “quality” under simplifying assumptions. | Keep signal quality separate from leverage; evaluate Sharpe and absolute drawdown. |
| Sharpe ratio | (E[r_P]-r_f)/sigma_P; slides warn comparability requires same frequency/assumptions and high Sharpe can hide short-volatility crash risk. | Use as one metric, never as sole promotion criterion. | Evaluation alongside drawdown, ES, cost drag and calibration. |
| Optimal risky allocation | Slides give y* = (E[r_P]-r_f)/(A sigma_P^2) = (1/A)(SR/sigma_P) under the model. | Motivates volatility-aware allocation but depends heavily on estimated expected return. | Conceptual input to position sizing; not a formula to copy blindly. |
| Estimation error | Course emphasizes that expected-return estimation errors can materially change allocation. | Forecast uncertainty must reduce risk and affect decision thresholds. | Uncertainty penalty, confidence intervals and shrinkage/calibration. |
| Borrowing vs lending rate | Higher borrowing cost kinks the CAL and changes leveraged allocation. | Leverage has financing frictions; risk-free borrowing is unrealistic. | FX margin/financing/carry model. |

## 7.1 Python notebook mapping

**[SOURCE] Notebook 1 - Python Basics for Finance** covers basic arithmetic/ROI, variables, lists as time series, simple returns, conditionals, stop-loss/take-profit logic exercises, AND/OR risk screens, loops, a BUY/SELL/HOLD signal list, while-loops, functions, and a simplified maximum-drawdown exercise. **Project implication:** these are conceptual building blocks; production code should replace ad-hoc lists and conditionals with typed models, pure functions, explicit time semantics and tests.

**[SOURCE] Notebook 2 - Python Libraries for Finance** introduces NumPy arrays/returns/cumulative products, annualization intuition, pandas DataFrames and cleaning/sorting, missing-value handling/groupby forward fill, percent-change feature engineering, per-stock mean/standard deviation/volume, and matplotlib line/bar/histogram/scatter plots. **Project implication:** NumPy/pandas remain useful research tools, but forward-fill and percent-change operations must be constrained by point-in-time rules so they do not create leakage.

# 8. FX-Specific Knowledge Layer

### Currency pair / base and quote

EUR/USD quotes USD per EUR. A long position is long EUR and short USD; a short is the opposite. P&L, financing and exposure must respect both legs.

### Pip / pipette / price precision

Pip value depends on pair, trade size and account currency. Never hard-code one universal pip value.

### Bid / ask / spread

Buys execute near ask and sells near bid; closing reverses side. Midpoint-only historical prices understate friction.

### Leverage

Leverage scales exposure relative to equity but does not create signal quality. It increases sensitivity to adverse moves and margin rules.

### Margin / liquidation

Broker-specific initial/maintenance margin and liquidation behavior must be modeled. V0.1 may use an explicit simplified rule, but it must be labeled as a simulator assumption.

### Rollover / swap

Holding currencies crosses financing conventions; broker swap may differ from theoretical rate differential and can have day-of-week conventions. It belongs in net P&L.

### Carry

Rate differential can be a predictive/risk-premium feature but has crash/funding/regime risk. Use contemporaneously available rates and broker financing for execution accounting.

### Interest-rate parity

Covered/uncovered parity concepts connect spot/forward rates and interest differentials. They are theoretical baselines, not automatic profitable rules.

### Purchasing-power parity / value

Relative prices can motivate long-horizon value measures, but timing, revisions and slow mean reversion make short-horizon use uncertain.

### Central banks / rate path

FX reacts to expected policy paths and surprises, not just the level of a policy rate. Event timestamp and expectation proxy matter.

### Yield differentials

Cross-country yield spreads are macro features whose maturity, source, release/market timestamp and currency hedge assumptions must be explicit.

### Macro surprise

Model actual minus consensus/expectation where a reliable point-in-time expectation exists; preserve source and availability time.

### Cross-asset state

Rates, equity risk, commodities, credit/volatility and other currencies can provide regime/context features, but incremental value must be tested.

### OTC fragmentation

There is no single centralized FX tape. Quotes, spreads and liquidity can differ by venue/provider; a canonical store must preserve provider identity.

### Dealer/internalization/NBLP behavior

Microstructure affects price discovery and execution. Retail data may only provide partial proxies; avoid pretending we have institutional order flow if we do not.

### Last look / rejects

Some venues/brokers can reject or reprice under defined conditions. Simulator and shadow mode should be able to record rejects and execution uncertainty.

### Liquidity

Spread and slippage are state-dependent, especially near events/stress. Liquidity health can become a hard risk gate.

### Order flow

Potentially informative at short horizons, but data access and horizon alignment matter. Treat proxy order-flow signals as separate hypotheses with provenance.

### Slippage / latency

Difference between decision/reference price and fill must be measured and scenario-tested. Live slippage should update execution diagnostics, not retroactively “fix” historical results.

# 9. Final Maysani Quant Architecture

**[SYNTHESIS] The architecture separates intelligence from authority.** An agent may observe or propose; only deterministic modules can calculate executable edge, approve risk, and mutate order/broker state.

External data sources
    |
    v
[Point-in-Time Data + Provenance Store]
    |
    +--> Deterministic Feature Engine -------------------+
    |                                                    |
    +--> Macro Agent ----> structured factors            |
    +--> News Agent -----> structured factors            |
    +--> Research Agent --> evidence/hypotheses          |
    +--> Regime Module ---> regime probabilities         |
    +--> Carry/Cross-Asset modules -----------------------+
                                                         v
                                              [Critic / Falsification]
                                                         |
                                                         v
                                              [Statistical Ensemble]
                                                         |
                                           expected return / uncertainty
                                                         |
                                      minus costs + risk/uncertainty penalty
                                                         |
                                                BUY / SELL / WAIT
                                                         |
                                                         v
                                               [HARD RISK ENGINE]
                                                         |
                                      APPROVE / MODIFY SIZE / REJECT
                                                         |
                                                         v
                                               [Execution Kernel]
                                                         |
                              Simulator -> Paper -> Shadow -> Live Broker
                                                         |
                                                         v
                                                    Portfolio
                                                         |
                 +---------------------------------------+-----------------+
                 v                                                         v
       Semantic Memory                                        Statistical Memory
                 \                                                         /
                  +---------------- [Evaluation + Audit] ------------------+

## 9.1 Data layer

- Canonical market observations with event_time, available_time, source_time, provider, instrument and quality flags.

- Macro releases with reference period, initial release, historical vintage/revision identity and consensus/expectation when available.

- News/events with publication time, ingestion time, source, entity/currency mapping, provenance and point-in-time eligibility.

- Research/RAG documents with version/date/source so retrieval can be restricted to information eligible at the decision timestamp.

- Immutable experiment and decision snapshots that store input hashes for reproducibility.

## 9.2 Intelligence layer

Quant, Macro, News, Research, Regime and Cross-Asset/Carry specialists produce typed observations, numeric factors, distributions/confidence or falsifiable hypotheses. They do not issue executable broker commands.

## 9.3 Decision layer

A statistical ensemble combines only validated signals. Weights depend on out-of-sample reliability, regime fit, correlation/independence, calibration and sample size. Expected return is compared with modeled costs and uncertainty before an action threshold is crossed.

## 9.4 Risk layer

A deterministic service receives the proposed direction, expected edge, stop/risk context, account state, margin state, exposures, system health and event constraints. It returns APPROVE, APPROVE_WITH_REDUCED_SIZE, or REJECT plus machine-readable reasons.

## 9.5 Execution layer

The same order-intent interface should feed historical simulation, paper broker, shadow broker and live broker adapters. Each adapter returns explicit order/fill/reject/cancel states. Production must never assume an API request equals a fill.

## 9.6 Memory and evaluation

Semantic memory stores contextual episodes and research. Statistical memory stores resolved forecast/trade performance by signal/regime/horizon. The audit layer records every input/output/version/veto/order/fill and supports full replay. Evaluation owns promotion, not the agent that proposed the idea.

# 10. Agent Specifications

## 10.1 Quant Agent / Quant Engine

**Inputs:** Point-in-time market features, returns, volatility, rates/cross-asset features, model config

**Outputs:** Numeric signal(s), expected return distribution or score, uncertainty, horizon, feature provenance

**Allowed:** Compute deterministic/statistical models; request tested calculations; compare against baselines

**Forbidden:** No broker actions; no risk override; no free-form position size

**Performance measurement:** Forecast error, calibration, IC/conditional performance, net contribution after costs, regime attribution

Example structured output:

{
  "as_of": "2026-01-15T16:00:00Z",
  "instrument": "EUR_USD",
  "horizon": "1D",
  "signal": -0.41,
  "expected_return": -0.0017,
  "uncertainty": 0.0025,
  "p_return_positive": 0.37,
  "model_version": "quant_momentum_v1",
  "feature_snapshot_id": "...",
  "quality_flags": []
}

## 10.2 Macro Agent

**Inputs:** Scheduled releases, vintages, expectations, yield/rate state, central-bank events, source documents

**Outputs:** Structured macro surprise features, rate-path/communication factors, horizon, confidence, evidence citations

**Allowed:** Interpret releases/events; normalize qualitative communication into structured evidence

**Forbidden:** No direct BUY/SELL; no use of revised future vintages; no invented consensus

**Performance measurement:** Incremental out-of-sample predictive value, calibration, event-window attribution

## 10.3 News Agent

**Inputs:** Timestamped news, source/provenance, entity/currency map, current market context

**Outputs:** Event type, direction/intensity, novelty, affected currencies, time horizon, uncertainty, source list

**Allowed:** Classify/extract facts and event features

**Forbidden:** No direct order; no unsupported causal story; no future articles in historical replay

**Performance measurement:** Extraction accuracy, calibration, incremental value vs no-news control, false-positive rate

## 10.4 Research Agent

**Inputs:** Curated papers, course material, repo docs, prior experiments, live research questions

**Outputs:** Hypotheses, evidence matrix, suggested deterministic tests, citations

**Allowed:** Retrieve, compare literature, generate falsifiable research proposals

**Forbidden:** Cannot promote own hypothesis; cannot modify production; cannot hide null evidence

**Performance measurement:** Research traceability, hypothesis novelty/quality, rate of hypotheses surviving controls (not rewarded for quantity)

## 10.5 Regime Module / Agent

**Inputs:** Volatility, trends, correlations, liquidity, macro/event state

**Outputs:** Regime probabilities/labels with uncertainty and transition state

**Allowed:** Classify observable environment and condition performance statistics

**Forbidden:** Cannot “explain” regime after outcome using future data; no direct order

**Performance measurement:** Stability, out-of-sample usefulness, transition calibration, incremental risk/forecast improvement

## 10.6 Carry / Cross-Asset Module

**Inputs:** Rates/yields, broker financing, forwards where available, cross-asset prices/features

**Outputs:** Carry score, financing estimate, cross-asset factor vector, uncertainty

**Allowed:** Compute transparent deterministic features and cost estimates

**Forbidden:** No theoretical carry treated as broker swap; no hidden stale data

**Performance measurement:** Net predictive value after financing/costs; robustness across regimes

## 10.7 Critic / Falsification Agent

**Inputs:** Proposed factor package, data provenance, regime, event calendar, model diagnostics, recent failures

**Outputs:** Structured objections: leakage risk, stale source, duplicated evidence, event/liquidity risk, regime mismatch, contradiction; severity/confidence

**Allowed:** Try to disprove or reduce confidence; trigger deterministic validation checks

**Forbidden:** Not an independent alpha vote; cannot enlarge size; cannot waive failed checks

**Performance measurement:** Detection of known test failures/leakage, useful rejection rate, false-alarm analysis

## 10.8 Chief / Decision Ensemble

**Inputs:** Validated structured factors from modules, correlation matrix, reliability stats, costs, uncertainty

**Outputs:** Net expected edge, action BUY/SELL/WAIT, confidence/calibration, factor contributions

**Allowed:** Combine inputs mathematically using versioned predefined rule/model

**Forbidden:** No unrestricted language-model decision; no risk bypass

**Performance measurement:** Net OOS contribution, calibration, stability, factor attribution

## 10.9 Risk Engine

**Inputs:** Decision proposal, account/position/exposure/margin, stop/risk info, vol/liquidity/event/system health

**Outputs:** APPROVE / REDUCE / REJECT, max permitted size, reason codes, kill-switch state

**Allowed:** Enforce hard deterministic constraints and safe degradation

**Forbidden:** No prompt-controlled override; no hidden changes to limits

**Performance measurement:** Constraint violation count (target zero), avoided tail losses, false blocking diagnostics, operational reliability

## 10.10 Execution Engine

**Inputs:** Approved order intent, venue/broker state, quote/spread, order policy

**Outputs:** Order lifecycle events, fills, rejects, cancels, slippage, fees, uncertain states

**Allowed:** Translate intent into simulator/broker commands and reconcile outcomes

**Forbidden:** Cannot infer approval; cannot fabricate fills; no withdrawals/deposits

**Performance measurement:** Fill quality, slippage, reject/reconcile rate, shadow-vs-live gap

## 10.11 Outcome Resolver / Statistical Memory

**Inputs:** Predictions, decisions, fills, future realized window once eligible

**Outputs:** Resolved label/outcome, P&L/cost attribution, calibration error, updated sufficient statistics

**Allowed:** Resolve only when outcome is observable; update predefined statistics

**Forbidden:** No backward leakage; no narrative rewriting of history

**Performance measurement:** Correctness/reproducibility of resolution and statistics

# 11. Mathematical Decision Framework

All formulas in this section are **[PROPOSED conceptual contracts]** until estimated and validated. They describe what the system should compute, not proven coefficients or profitable thresholds.

### 11.1 State

Let the point-in-time state be X_t, a vector of features available at time t: returns, trend/momentum, volatility, rates/yield spreads, carry/financing, macro surprises, news/event factors, cross-asset state, liquidity/spread, correlations, regime probabilities and quality flags. Every feature has provenance and an availability timestamp.

### 11.2 Forecast and risk

mu_hat_(t,h) = f_theta(X_t) estimates expected return over horizon h. sigma_hat_(t,h) = g_phi(X_t) estimates forecast dispersion/risk. The preferred output is a distribution or calibrated probability rather than a single point estimate where feasible.

### 11.3 Ensemble

A simple form is S_t = sum_i w_(i,t) * S_(i,t). Weights are versioned and may depend on validated reliability, regime, sample size, calibration and signal correlation. Weight adaptation cannot use unresolved future outcomes.

### 11.4 Cost-adjusted edge

A conceptual decision quantity is: Edge_t = E[R_(t,h) | X_t] - ExpectedTradingCosts_t - lambda * Risk_t - UncertaintyPenalty_t. Trading costs include executable spread, expected slippage, commission and expected financing/rollover over the intended holding period.

### 11.5 Action rule

For a symmetric conceptual threshold tau > 0: BUY if Edge_t > tau; SELL if Edge_t < -tau; otherwise WAIT. In production the buy/sell thresholds need not be symmetric if empirical costs or risk differ, but every threshold must be versioned and validated.

### 11.6 Probability and calibration

The system may estimate p_t = P(R_(t,h) > 0 | X_t) and/or probabilities of exceeding cost/risk hurdles. Brier score, log loss, reliability plots and conditional calibration should be tracked so “70% confidence” has empirical meaning.

### 11.7 Regime-conditioned evidence

Instead of asking whether a factor “works,” estimate quantities such as E[R | signal, regime], hit/payoff distributions, and confidence intervals. A regime-conditioned weight is justified only when there are enough observations and the benefit survives unseen data.

### 11.8 Survival objective

A research objective may include expected log growth, e.g. maximizing E[log(W_T)], subject to hard ruin/drawdown/leverage/margin constraints. This is a conceptual objective only. It does not permit unconstrained Kelly sizing, and the risk engine remains an independent hard boundary.

# 12. Risk Engine

**[SYNTHESIS] Risk is a deterministic permission service.** Its rules are configuration-controlled, versioned, tested and auditable. LLM outputs may reduce confidence or suggest a risk investigation but cannot disable a risk rule.

### Data-quality gate

Reject new risk if required data are stale, missing, out-of-order, inconsistent, or fail provenance checks.

### System-health gate

Reject/flatten according to policy if broker connectivity, clock sync, persistence, reconciliation or execution state is unsafe.

### Per-trade / position risk

Limit notional and loss-at-stop or scenario loss relative to current equity. Stop-distance logic must respect instrument precision and gap risk.

### Gross/net exposure

Cap total notional, currency-leg exposures and directional concentration.

### Leverage / margin

Check broker-style leverage and margin headroom before creating or increasing risk.

### Correlation / cluster exposure

Prevent several apparently different trades from creating the same underlying USD or risk-factor bet.

### Daily/session loss

Block new risk or throttle after configured realized/unrealized loss thresholds.

### Drawdown control

Reduce permitted exposure as drawdown deepens; terminal kill/death rules are separate and explicit.

### Volatility/liquidity scaling

Reduce size or reject when observed/predicted volatility, spread, or liquidity stress exceeds safe bounds.

### Event-risk gate

Optionally restrict entries/size near scheduled high-impact events until the event module is validated.

### Maximum open risk

Aggregate scenario/stop risk across all open positions rather than checking positions independently.

### Emergency kill switch

Idempotent mechanism to stop new orders and follow a documented cancel/flatten/reconcile sequence where configured.

### Position-sizing contract

A common conceptual sizing identity is position_size = account_risk_budget / loss_per_unit_at_stop. All elements must be instrument-aware and cost-aware. Any example percentage used during development is **provisional** and lives in configuration, not prose or hidden constants. The first goal is to prove constraint correctness, not optimize the risk percentage.

### Risk-engine invariants

- No approved size exceeds configured leverage, margin or exposure constraints.

- A REJECT cannot be converted into an order by a downstream component.

- Configuration changes create a new version and audit event.

- Restarting the service does not reset drawdown/daily-loss state incorrectly.

- Stale/missing account or market state fails safe for new risk.

- All vetoes and reductions emit reason codes that can be analyzed later.

- AI text, prompts and RAG documents are never evaluated as executable risk configuration.

# 13. Backtesting and Scientific Validation

This is the scientific core of the project. A sophisticated model evaluated badly is less trustworthy than a simple model evaluated honestly.

## 13.1 Event-driven simulation

V0.1 should represent market events, strategy decisions, order intents, risk decisions, fills, position updates and portfolio marks as explicit ordered events. Even if the first dataset is bar-based, the simulator should not silently pretend it knows the within-bar path.

## 13.2 Execution realism checklist

- Bid/ask or a documented spread model; buys and sells use the correct side.

- Configurable commission/fee model.

- Slippage model with stress scenarios rather than one optimistic constant.

- Rollover/swap/financing for positions held across relevant boundaries.

- Leverage and margin checks before fill/position acceptance.

- Rejected/partial/uncertain order states supported by the domain model even if V0.1 uses a simplified fill policy.

- Price precision, quantity precision and minimum-size rules as instrument/broker metadata.

- Portfolio/equity reconciliation after every event.

- Conservative handling of ambiguous bar events: if a stop and take-profit are both touched and path ordering is unknown, use a documented adverse assumption or disallow the ambiguous case rather than choose the favorable outcome.

## 13.3 Look-ahead and point-in-time controls

- Features at decision time t may use only observations with available_time <= t.

- If the strategy decides after bar close t, a simple V0.1 execution convention is next-bar-open t+1 plus bid/ask/slippage, not the already-known close used for the decision.

- Macro releases store original/vintage values and release timestamps; later revisions cannot replace history in replay.

- News/RAG retrieval filters out documents published after the historical decision timestamp.

- Trade memories become eligible only after the designated resolution time/date.

- Rolling normalization/feature statistics must be fit on past data only; global normalization is prohibited unless analytically proven not to leak future information.

## 13.4 Selection bias and multiple testing

Every trial receives an immutable experiment ID with hypothesis, feature set, parameters, data snapshot, train/validation/test windows, cost model, code commit, result and status. Failed and abandoned trials stay in the registry. Research agents receive an experiment budget so rapid parameter search cannot create an invisible factor zoo.

Use multiple-testing-aware tools such as Deflated Sharpe Ratio and Probability of Backtest Overfitting when the experiment volume makes them applicable. These metrics supplement rather than replace unseen forward evaluation.

## 13.5 Walk-forward and holdout design

A canonical workflow is **train -****>**** validate -****>**** unseen test -****>**** roll forward**. For overlapping labels/holding horizons, purging and embargo may be required to prevent training observations from leaking into validation through overlapping outcomes. One final holdout should remain untouched by repeated development. Once it is used to make decisions, it is no longer a clean final holdout.

## 13.6 Required metrics

- Total and log return; geometric growth

- Sharpe with frequency/serial-correlation disclosure

- Sortino

- Maximum drawdown and drawdown duration

- Calmar

- Hit rate and payoff ratio

- Expected Shortfall / tail scenarios

- Turnover and time in market

- Spread, slippage, financing and total cost drag

- Margin/leverage utilization

- Forecast calibration, Brier score and log loss where probabilistic

- Factor/signal contribution and correlation

- Performance by regime

- PBO/Deflated Sharpe when appropriate

- Paper/live vs backtest degradation

- Operational errors, rejects, reconciliation failures

## 13.7 Baselines

Every candidate should face at least: no-trade/WAIT, buy-and-hold-like exposure where meaningful for the instrument/horizon, simple trend/momentum, simple mean-reversion, and any incumbent champion. An LLM feature is promoted only if the identical pipeline with the LLM feature removed performs materially worse on unseen evidence after costs.

## 13.8 Promotion pipeline

IDEA
  -> code
  -> unit/property tests
  -> historical sanity test
  -> walk-forward validation
  -> untouched/unseen evaluation
  -> cost + stress scenarios
  -> autonomous paper
  -> real-broker shadow
  -> candidate release
  -> controlled production

At any stage a candidate can be rejected or returned to research. “More complex” is not a promotion criterion.

# 14. Memory and Learning Architecture

## 14.1 Semantic memory

Stores qualitative context: event summaries, research notes, central-bank narratives, retrieved evidence, post-trade explanations, known failure episodes and engineering incidents. Retrieval is filtered by source, date and historical eligibility. Semantic memory can help an agent ask better questions; it does not directly change capital allocation.

## 14.2 Statistical memory

Stores sufficient statistics and resolved performance by signal, model version, horizon and regime: observation count, mean/median realized return, cost-adjusted return, win probability, MAE/MSE, calibration error, confidence intervals, drawdown contribution, sample age, and significance/multiple-testing context. **Only this layer may automatically inform weights, and only through predefined code.**

## 14.3 Decision/trade memory

For every decision - including WAIT - store decision timestamp, eligible information snapshot IDs, feature/model versions, agent outputs, ensemble decomposition, expected costs, risk decision/reason, order/fill lifecycle, later outcome and resolution timestamp. This makes “why did it trade?” answerable without reconstructing from prose.

## 14.4 Resolution-date rule

A memory with a future outcome is unavailable until its resolution timestamp. This rule is directly inspired by the point-in-time memory protections observed in TradingAgents and is mandatory for Maysani Quant. The database may physically contain the future-resolved record today, but a historical query must filter it out.

## 14.5 Example statistical weight update

**[PROPOSED]** Suppose a momentum signal historically had weight 0.30. A predefined updater could shrink its effective weight using a reliability term derived from out-of-sample calibration, regime-conditioned sample size and confidence bounds. The updater is a deterministic function, versioned and tested. An LLM may explain why performance changed or suggest a new test, but cannot set the new number by narrative judgment.

## 14.6 Experiment memory

All hypotheses, including rejected ones, remain queryable. The research agent should be able to answer: “Have we already tested this idea? On which window? With which costs? What failed?” This reduces accidental repeated trials and makes research-budget accounting possible.

# 15. Evolution / Champion-Challenger System

Continuous improvement is permitted only in the **development domain**. Production remains a versioned champion. AI agents and coding agents may propose challenger features/models/risk policies, but they do not decide whether their own work is successful.

Production champion vN
       |
       +--------------------------+
                                  v
                         Challenger hypothesis
                                  |
                           code + unit tests
                                  |
                         experiment registry
                                  |
                  walk-forward / unseen / stress
                                  |
                            forward paper
                                  |
                             shadow broker
                                  |
                        promotion review/gate
                         /              \
                    reject             promote
                                         |
                                 Production vN+1
                                         |
                                      rollback

Promotion rules should be machine-checkable where possible: required tests green, no integrity flags, minimum evidence/sample requirements, cost-adjusted improvement or justified risk reduction, acceptable drawdown/tail behavior, no unexplained degradation, and successful restart/reconciliation drills. A candidate can be valuable even if it reduces return but improves survival/risk; the objective function must state that trade-off explicitly.

# 16. Multi-Organism Experiment

**[PROPOSED]** After one organism is scientifically stable, run a population of isolated organisms over the same point-in-time information stream. They may differ in validated strategy family, risk policy, ensemble weighting, model family, memory policy or update cadence. Each organism receives a unique ID, seed/config, initial capital and immutable experiment lineage.

Repeated survival across unseen regimes is more informative than one lucky path. Report the distribution of terminal wealth, ruin/death frequency, drawdown, tail outcomes, turnover, cost drag, calibration and live-vs-backtest gap. Avoid selecting the best organism after the fact without correcting for the number of organisms tested; population experiments themselves create multiple-testing risk.

A population is also useful for ablation: one organism can run without LLM news features, one without macro, one with static weights, one with adaptive weights, etc. This makes it possible to attribute whether added complexity actually earns its operational cost.

# 17. Technology Stack

| **Technology** | **Role / rationale** |
| --- | --- |
| Python | Primary research, feature, model, risk and orchestration language; strongest fit with finance/ML ecosystem and reviewed repos. |
| NumPy / pandas | Deterministic array/time-series research; pandas convenient for V0.1, with stricter schemas or Polars/Arrow considered later if scale requires. |
| SciPy / statsmodels | Statistical estimation, distributions, regressions, hypothesis/diagnostic tooling. |
| scikit-learn | Baseline ML models, preprocessing pipelines and calibrated evaluation. |
| PyTorch - later | Only for models that justify added complexity after baselines. |
| PostgreSQL | Long-term production store for portfolios, decisions, experiments, outcomes, operational state and provenance. |
| pgvector | Optional semantic retrieval in the same database; useful later for RAG/memory without adding a new database early. |
| SQLite / local columnar files in V0.1 | [PROPOSED] Simpler local persistence for initial experiment ledger/journal while interfaces remain migration-friendly to PostgreSQL. |
| FastAPI | Internal/API control plane for dashboard, monitoring, experiments and broker-control surfaces. |
| Docker | Reproducible runtime and later isolated organism deployments. |
| GitHub | Permanent source of truth, branches/PRs/version history. |
| GitHub Actions | CI tests, lint/static checks, reproducible backtest smoke tests, controlled deployments. |
| Claude initially | Coding agent working against the repository and master reference; not a runtime trading dependency. |
| Codex later/optionally | Alternative/additional coding agent or reviewer; project should remain agent-vendor independent. |
| Netlify | Frontend/dashboard deployment only; not the persistent Python trading engine. |
| Maysani domain | Mobile-friendly control-center subdomain such as quant.maysani.... |
| Linux VPS / cloud runtime | Always-on backend, workers, database and later paper/shadow/live engine; selected when V0.1 needs persistence/24x5 operation. |

### Deployment placement

**Local/development:** research notebooks, unit tests, small backtests. **GitHub:** code, documentation, CI configuration and version history. **Netlify:** mobile/web dashboard. **Cloud Linux runtime:** persistent Python services, worker/scheduler, database, paper/shadow/live engine, metrics. **Broker/data APIs:** accessed only through server-side adapters and secret management; never from browser JavaScript.

# 18. Development Architecture

The coding agent may work continuously, but “always building” must not mean “always changing production.”

YOU / PHONE
    |
    v
Project direction (ChatGPT / human decisions)
    |
    v
Claude or Codex development agent
    |
    v
Git branch / PR
    |
    v
CI: tests + lint + deterministic smoke backtests + security checks
    |
    v
Experiment environment
    |
    v
Candidate release
    |
    v
Promotion gate -------------------> REJECT / RETURN TO RESEARCH
    | PASS
    v
Protected production release
    |
    v
Always-on FX organism

Production must deploy immutable version/tag/container identities and record the exact git commit with every decision. Secrets are stored in cloud/CI secret facilities, never committed. The production service account should have only the broker permissions required for trading; withdrawals/deposits are outside the trading engine. Any future automatic promotion should require explicit, machine-auditable criteria and should remain disabled until the process is proven safe.

# 19. Mobile Control Center

The dashboard is an observability/control surface, not the source of trading truth. Netlify can host the frontend while authenticated API calls reach the always-on backend. Sensitive broker credentials never reach the browser.

### Minimum mobile view

MAYSANI QUANT
------------------------------------------------
ORGANISM #001                         ALIVE
Equity                               $54.82
Lifetime return                       +9.64%
Current drawdown                      -2.31%
Open risk                              0.41%

EUR/USD
Decision                                WAIT
Net expected edge                      +0.03%
Forecast uncertainty                    0.08%
Regime                              RISK-OFF

SYSTEM
Market data                                 OK
Macro                                       OK
News                                        OK
Risk engine                                 OK
Execution                                   OK
Last reconciliation                         OK

DEVELOPMENT
Production                              v0.8.2
Candidate                               v0.9.0
Tests                                  812 PASS
Experiments running                           4
Last promotion                          REJECTED
------------------------------------------------

### Dashboard requirements

- Organism alive/dead/paused state and reason.

- Equity, realized/unrealized P&L, drawdown and exposure.

- Open positions and order lifecycle states.

- Latest BUY/SELL/WAIT, expected net edge, uncertainty and factor contributions.

- Current regime and risk-engine state/reason codes.

- Market/macro/news/data-feed freshness and provenance warnings.

- Broker connectivity, rejects, reconciliation and shadow-vs-simulated fill diagnostics.

- Production/candidate version, git commit, CI/test state and experiment status.

- Strategy promotion/rejection history and rollback status.

- Mobile alerts only for material events: system failure, kill switch, risk threshold, organism death, candidate promotion/rejection and daily summary.

# 20. Full Build Roadmap

## 20.1 Phase 0 - Foundation

**Objective:** Create a reproducible repository and engineering contract before trading logic.

**Components:**

- Repo/package structure

- Python environment/lockfile

- pytest, lint/type checks, logging/config

- .env.example and secret policy

- basic Docker/CI

- architecture docs

**Dependencies:** None beyond repo access and Python tooling

**Deliverables:**

- Fresh clone installs

- tests/quality checks run in one command

- CI green

**Required tests:**

- Installation smoke test

- config validation

- deterministic seed/version test

**Exit criteria:** A clean fresh environment can run tests and a placeholder CLI.

**Do NOT build yet:** No broker, dashboard, LLM agents or production cloud.

## 20.2 Phase 1 - Organism

**Objective:** Create the account/portfolio state machine with USD 50 simulation.

**Components:**

- Account/equity/cash

- position model

- BUY/SELL/WAIT decision record

- P&L

- ALIVE/DEAD state

- trade/decision journal

**Dependencies:** Phase 0

**Deliverables:**

- Organism can be born, marked, trade in a toy environment, gain/lose and die deterministically.

**Required tests:**

- Accounting reconciliation

- death transition

- WAIT logged

- restart persistence

**Exit criteria:** All state transitions deterministic and fully journaled.

**Do NOT build yet:** No predictive AI; no real market data dependency.

## 20.3 Phase 2 - Point-in-Time Data

**Objective:** Build canonical EUR/USD historical data with strict time/provenance contracts.

**Components:**

- OHLC/quotes where available

- provider/source metadata

- event vs available timestamp

- quality checks

- normalized instrument metadata

- snapshot IDs

**Dependencies:** Phase 0

**Deliverables:**

- Validated EUR/USD dataset and loader

- data-quality report

- feature-ready PIT schema

**Required tests:**

- No duplicates/order inversions

- future-availability test

- timezone tests

- missing/stale handling

**Exit criteria:** A historical timestamp reconstructs only what the system could know then.

**Do NOT build yet:** No broad multi-pair universe; no macro/news yet.

## 20.4 Phase 3 - FX Backtesting Laboratory

**Objective:** Build the event-driven simulation/accounting world.

**Components:**

- Events/orders/fills/positions

- spread/commission/slippage

- swap hook

- margin/leverage

- stops/TP abstractions

- rejections/uncertain states

- drawdown/compounding

**Dependencies:** Phases 1-2

**Deliverables:**

- One-command reproducible backtest

- ledger reconciliation

- cost report

**Required tests:**

- Flat-price round trip loses modeled costs

- ambiguous bar handling

- margin/liquidation tests

- deterministic replay

**Exit criteria:** USD 50 can realistically survive/compound/die under documented assumptions.

**Do NOT build yet:** No complex alpha; no LLM.

## 20.5 Phase 4 - Hard Risk & Survival

**Objective:** Add deterministic veto/sizing.

**Components:**

- Risk policy interface

- leverage/margin/exposure caps

- per-trade/open-risk limits

- daily-loss/drawdown throttle

- data/system-health veto

- kill switch

**Dependencies:** Phases 1-3

**Deliverables:**

- Machine-readable risk decisions

- risk audit log

**Required tests:**

- Attempted violations rejected

- restart state preserved

- kill-switch idempotency

**Exit criteria:** No strategy can violate account-level constraints.

**Do NOT build yet:** No AI-controlled risk parameters.

## 20.6 Phase 5 - Quant Brain V1

**Objective:** Add simple transparent baseline signals.

**Components:**

- Momentum/trend

- mean reversion

- volatility state

- later carry/value/cross-asset interfaces

- structured forecast output

**Dependencies:** Phases 2-4

**Deliverables:**

- Baseline library

- factor reports

- signal schema

**Required tests:**

- Unit tests

- no-lookahead features

- parameter-sensitivity sanity

- baseline comparison

**Exit criteria:** Signals reproducible and economically interpretable.

**Do NOT build yet:** No black-box deep learning; carry may wait for rates data.

## 20.7 Phase 6 - Scientific Validation

**Objective:** Make experimentation falsifiable.

**Components:**

- Experiment registry

- train/validate/unseen/walk-forward

- metrics

- trial accounting

- stress/cost scenarios

- DSR/PBO hooks

**Dependencies:** Phases 2-5

**Deliverables:**

- Immutable experiment records

- comparison reports

**Required tests:**

- Holdout protection

- failed trial retention

- reproduce prior experiment by ID

**Exit criteria:** No strategy is promoted from one attractive backtest.

**Do NOT build yet:** No continuous self-promotion.

## 20.8 Phase 7 - Regime Brain

**Objective:** Condition evidence on observable market states.

**Components:**

- Trend/range

- high/low vol

- risk-on/off proxies

- rate-divergence/event stress

- regime probabilities

**Dependencies:** Phases 5-6

**Deliverables:**

- Regime classifier/state module

- conditional performance report

**Required tests:**

- PIT classification

- transition stability

- incremental OOS test

**Exit criteria:** Regime information improves decisions/risk on unseen data or is rejected.

**Do NOT build yet:** No hindsight regime labeling for live decisions.

## 20.9 Phase 8 - Macro Brain

**Objective:** Add point-in-time economic/rate information.

**Components:**

- Rates/yields

- CPI/employment/GDP/PMI where justified

- central-bank events

- expectations/surprises

- historical vintages

**Dependencies:** Phases 2,6

**Deliverables:**

- Macro event store

- structured macro features

**Required tests:**

- Release-time/vintage tests

- event-window tests

- no revision leakage

**Exit criteria:** Macro features demonstrate incremental OOS value or remain context-only.

**Do NOT build yet:** No generic “hawkish = buy” rules.

## 20.10 Phase 9 - AI / News / Research

**Objective:** Introduce LLMs only as structured research organs.

**Components:**

- News extractor

- macro language interpreter

- RAG research agent

- critic/falsifier

- typed schemas/provenance

**Dependencies:** Phases 2,6,8

**Deliverables:**

- Agent services with strict schemas

- retrieval audit

- no-LLM ablation

**Required tests:**

- Numeracy/extraction tests

- PIT retrieval

- hallucination/unknown handling

- ablation vs identical non-LLM control

**Exit criteria:** Agents produce reliable structured evidence without direct order authority.

**Do NOT build yet:** No LLM final trade or position sizing.

## 20.11 Phase 10 - Mathematical Decision Engine

**Objective:** Combine validated factors into net edge and BUY/SELL/WAIT.

**Components:**

- Ensemble

- correlation/reliability weights

- expected return distribution

- uncertainty

- cost model

- action thresholds

**Dependencies:** Phases 5-9

**Deliverables:**

- Versioned decision model

- factor attribution

**Required tests:**

- Calibration

- signal-correlation tests

- cost sensitivity

- WAIT behavior

**Exit criteria:** Decision rule adds OOS value without violating risk architecture.

**Do NOT build yet:** No majority-vote ensemble.

## 20.12 Phase 11 - Memory

**Objective:** Create semantic + statistical learning.

**Components:**

- Semantic episodes/RAG

- statistical sufficient stats

- resolution timestamps

- trade/agent prediction memory

- experiment memory

**Dependencies:** Phases 6,9,10

**Deliverables:**

- Dual-memory store

- eligibility filters

- update functions

**Required tests:**

- Future-outcome leakage test

- statistical update determinism

- sample-size shrinkage tests

**Exit criteria:** Historical replay cannot see unresolved future memory; automatic weights use statistical evidence only.

**Do NOT build yet:** No embedding-similarity sizing.

## 20.13 Phase 12 - Evolution

**Objective:** Automate safe challenger research.

**Components:**

- Champion/challenger registry

- hypothesis queue

- experiment budgets

- promotion/rejection/rollback

**Dependencies:** Phases 6,10,11

**Deliverables:**

- Candidate release workflow

- promotion report

**Required tests:**

- Cannot self-promote

- rollback test

- experiment-budget enforcement

**Exit criteria:** Challengers can be tested continuously while champion remains stable.

**Do NOT build yet:** No automatic production mutation.

## 20.14 Phase 13 - Autonomous Paper Trading

**Objective:** Run full system on live information with simulated broker.

**Components:**

- Live feeds

- scheduler/workers

- paper execution

- 24x5 monitoring

- daily reports

**Dependencies:** Phases 3-12

**Deliverables:**

- Always-on paper organism

- live audit trail

**Required tests:**

- Restart/recovery

- data outage

- kill switch

- backtest-vs-paper diagnostics

**Exit criteria:** Sustained forward operation with no integrity failures and explainable performance.

**Do NOT build yet:** No real money.

## 20.15 Phase 14 - Shadow Broker

**Objective:** Use real broker quotes/constraints but hypothetical orders.

**Components:**

- Broker adapter

- actual spreads/quotes

- min size/precision

- shadow order/fill model

- TCA

**Dependencies:** Phase 13

**Deliverables:**

- Shadow account

- sim-vs-broker gap report

**Required tests:**

- Auth/permission

- reconnect/reconcile

- reject/latency scenarios

**Exit criteria:** Operational assumptions are validated against real broker conditions.

**Do NOT build yet:** No live order submission.

## 20.16 Phase 15 - Controlled Live Experiment

**Objective:** Allow tiny real trading only after prior gates.

**Components:**

- Trading-only API permissions

- strict live risk profile

- live TCA

- automatic stop/kill/alerts

**Dependencies:** Phase 14 + explicit human go-live decision

**Deliverables:**

- Versioned live release

- live incident runbook

**Required tests:**

- Withdrawal impossible

- kill switch

- restart/reconciliation

- position limits

**Exit criteria:** Live behavior remains within controls; material degradation triggers stop/research.

**Do NOT build yet:** No autonomous deposits/withdrawals; no aggressive scaling.

## 20.17 Phase 16 - Multiple Organisms

**Objective:** Run population/ablation experiments.

**Components:**

- Isolated organism configs

- common PIT feed

- population analytics

- multiple-testing correction

**Dependencies:** Stable single-organism pipeline

**Deliverables:**

- Population experiment suite

**Required tests:**

- Independence/config isolation

- same information budget

- selection-bias reporting

**Exit criteria:** Conclusions come from distributions/repeated evidence, not one lucky account.

**Do NOT build yet:** No selecting the best survivor without correcting for trials.

## 20.18 Phase 17 - Dashboard

**Objective:** Build mobile control center on Netlify/Maysani domain.

**Components:**

- Frontend

- auth

- API

- status/equity/risk/trades

- development/CI/experiment status

- alerts

**Dependencies:** Paper/shadow APIs stable

**Deliverables:**

- quant.maysani... control center

**Required tests:**

- No secrets browser-side

- role/auth tests

- stale-data display

**Exit criteria:** User can safely understand system state from phone.

**Do NOT build yet:** Dashboard does not become trading source of truth.

## 20.19 Phase 18 - Always-Building Infrastructure

**Objective:** Enable continuous coding/research while protecting production.

**Components:**

- Cloud coding agents

- branch/PR automation

- CI runners

- experiment workers

- candidate releases

- protected deployment/rollback

**Dependencies:** Mature tests/promotion process

**Deliverables:**

- 24x7 development pipeline with immutable production releases

**Required tests:**

- Agent cannot deploy around gates

- supply-chain/secret checks

- rollback/recovery

**Exit criteria:** Development may continue constantly without unvalidated code touching live capital.

**Do NOT build yet:** No “agent improves itself and deploys anything better-looking” loop.

# 21. V0.1 Exact Specification

**[SYNTHESIS] V0.1 is deliberately boring.** Its purpose is to prove data timing, accounting, costs, risk, reproducibility and experiment discipline before adding LLMs, macro, deep learning or live brokers.

## 21.1 Scope

- EUR/USD only.

- Historical data only.

- Initial simulated equity: USD 50.00.

- Actions: BUY, SELL, WAIT.

- Deterministic price/volatility features.

- Two baseline strategies: transparent momentum/trend and transparent mean-reversion.

- Event-driven simulation with documented bar-level assumptions.

- Configurable spread, commission, slippage and financing hooks; no universal “realistic” constant fabricated.

- Deterministic hard risk engine.

- Portfolio/equity accounting and drawdown.

- Permanent decision/trade/experiment journal.

- Configurable ALIVE/DEAD threshold and deterministic state transition.

- Reproducible tests and one-command backtest.

- No LLM dependency.

## 21.2 Recommended repository structure

maysani-quant/
  pyproject.toml
  README.md
  CLAUDE.md
  .env.example
  configs/
    v0_1.yaml
  data/
    README.md
  docs/
    MAYSANI_QUANT_MASTER_REFERENCE.md
    MAYSANI_QUANT_MASTER_REFERENCE.docx
    adr/
  src/maysani_quant/
    domain/
      enums.py
      models.py
      events.py
    data/
      interfaces.py
      csv_source.py
      validation.py
    features/
      returns.py
      momentum.py
      mean_reversion.py
      volatility.py
    strategies/
      base.py
      momentum_v1.py
      mean_reversion_v1.py
    risk/
      interfaces.py
      hard_limits.py
    execution/
      models.py
      simulator.py
      costs.py
    portfolio/
      ledger.py
      accounting.py
    backtest/
      engine.py
      metrics.py
      report.py
    experiments/
      registry.py
      schema.py
    journal/
      store.py
      schema.py
    cli.py
  tests/
    unit/
    integration/
    regression/

## 21.3 Domain models

| **Model** | **Minimum fields / purpose** |
| --- | --- |
| MarketBar | instrument, start/end time, available_time, open/high/low/close, optional bid/ask/spread fields, source, quality flags |
| FeatureSnapshot | as_of, instrument, feature values, input snapshot IDs, code/model version |
| Signal | as_of, instrument, strategy_id/version, horizon, score, optional expected_return/uncertainty, reason codes |
| RiskDecision | proposal ID, APPROVE/REDUCE/REJECT, max size, reason codes, risk-config version |
| OrderIntent | side, quantity/notional, order type, decision ID, risk-decision ID, timestamp |
| Fill | order ID, timestamp, price, quantity, spread/slippage/fee components, status |
| Position | instrument, side/net quantity, average price, realized/unrealized P&L, financing |
| PortfolioSnapshot | timestamp, cash, equity, gross/net exposure, leverage, margin, drawdown, alive state |
| DecisionRecord | BUY/SELL/WAIT, factor/signal IDs, expected costs, risk result, portfolio state |
| TradeRecord | open/close events, fills, costs, realized result, duration, strategy/decision lineage |
| ExperimentRecord | hypothesis, config, data hash, code commit, time windows, cost model, metrics, status, parent experiment |

## 21.4 Interfaces

class MarketDataSource:
    def iter_events(self, start, end): ...

class FeaturePipeline:
    def compute(self, history, as_of): ...

class Strategy:
    def evaluate(self, features, portfolio) -> Signal: ...

class RiskPolicy:
    def assess(self, signal, portfolio, market_state) -> RiskDecision: ...

class ExecutionModel:
    def submit(self, order_intent, market_event) -> list[Fill]: ...

class PortfolioLedger:
    def apply(self, event_or_fill) -> PortfolioSnapshot: ...

class Journal:
    def append(self, record) -> str: ...

These signatures are conceptual; Claude may improve Python typing and event abstractions while preserving authority boundaries and traceability.

## 21.5 Decision timing contract

A default V0.1 convention should be explicit and conservative: features and strategy evaluate only after bar t is complete; the earliest ordinary market fill is the next eligible bar/event at t+1 using the executable side plus configured slippage/cost. A feature cannot read bar t+1. If the dataset only contains midpoint OHLC, spread must be added as a documented scenario rather than pretending midpoint is executable.

## 21.6 Baseline strategies

**Momentum/trend v1:** rolling log-return and/or moving-average relationship with a volatility filter. Parameters are few, predeclared and included in experiment records.

**Mean-reversion v1:** rolling standardized deviation (z-score) from a rolling center with entry/exit thresholds. It is a baseline/falsification control, not a claim that EUR/USD mean reverts profitably.

Carry is deferred until the point-in-time rate/financing layer exists.

## 21.7 Persistence

For V0.1, a small SQLite database or append-only local files (e.g. Parquet/JSONL behind an interface) are acceptable. The schema must make migration to PostgreSQL straightforward. Do not deploy PostgreSQL merely to make V0.1 look “production-grade” if it slows core correctness.

## 21.8 Configuration

All parameters belong in versioned config: initial equity, death threshold, timeframe, feature lookbacks, signal thresholds, spread/cost/slippage scenarios, leverage/margin assumptions, risk limits, random seed if any, dataset path/hash, and reporting options. There are no hidden tuning constants in prompts.

## 21.9 Required tests

- Determinism: same data/config/code produces identical event/decision/fill/equity output.

- No-future-data: strategy/feature query fails or excludes records with available_time > as_of.

- Accounting reconciliation: cash + marked positions - modeled liabilities/costs = equity under the defined accounting model.

- Flat-price round trip: a complete round trip loses exactly modeled costs (within precision), never creates free profit.

- Correct bid/ask side: long entry/exit and short entry/exit use documented executable sides.

- Risk veto: dangerous requested sizes are rejected/reduced and cannot reach execution unchanged.

- Leverage/margin: cannot create a position beyond configured constraints.

- Drawdown/death: state transition is deterministic and terminal according to configuration.

- WAIT: a no-trade decision is journaled with the same provenance discipline as a trade.

- Ambiguous OHLC stop/TP: conservative/documented rule is enforced.

- Restart/persistence: journal and account state recover without duplicating fills or resetting risk state.

- Experiment reproducibility: experiment ID points to data hash, config and code version.

- Baseline comparison: no-trade and both baseline strategies appear in the report.

- CI: unit/integration/regression suite runs from a fresh clone.

## 21.10 Acceptance criteria

- Fresh clone installs from documented instructions.

- pytest (or the documented one-command test suite) passes in CI.

- One documented CLI command runs a EUR/USD backtest from a fixed dataset/config.

- The report includes gross return, net return, costs, drawdown, turnover, time in market and organism ALIVE/DEAD state.

- Every decision can be traced to feature snapshot, strategy version, risk decision and portfolio state.

- No code path can read future bars or unresolved memory.

- Costs are included in portfolio accounting.

- Risk vetoes are enforced downstream.

- No LLM/API key is required for V0.1.

- No profitability claim is printed by default; output describes measured results and assumptions.

# 22. Things Claude Must Never Do

These are project-level engineering rules, not suggestions:

- Never fabricate market, macro, consensus, news, broker or performance data.

- Never introduce future information into a historical decision, including through preprocessing, revised macro values, retrieval, memory or labels.

- Never silently change risk limits, death rules, margin assumptions or transaction-cost assumptions.

- Never give an LLM unrestricted broker control or allow agent text to bypass risk.

- Never automatically deploy an experimental strategy to live trading merely because a backtest improved.

- Never optimize repeatedly against the designated final holdout and continue calling it a holdout.

- Never delete failed experiments or hide negative/null results.

- Never assume gross return equals executable return.

- Never ignore spread, slippage, financing/swap, leverage or margin in deployability claims.

- Never hide test failures, disable tests to make CI green, or weaken an invariant without an explicit architecture decision.

- Never change the authority boundaries (AI -> quant -> risk -> execution) without documenting the reason and updating this reference/ADR.

- Never expose API keys, broker credentials, private tokens or secrets in git, logs, browser bundles, prompts or reports.

- Never make withdrawal/deposit functionality part of the trading engine.

- Never treat an agent persona as independent evidence without measured independence.

- Never let semantic/embedding memory directly increase position size.

- Never present a generated or literature-derived strategy as “profitable” until it has met the project promotion standard.

- Never use a live account to debug code paths that can be tested in simulation/paper/shadow.

- Never assume backtest/live code parity removes broker/network/timing/reconciliation risk.

- Never copy repository code without checking its license/provenance and documenting the dependency.

- Never let continuous development mutate the currently running production container/image in place.

# 23. Open Questions / Research Backlog

- **Data provider and granularity:** Which EUR/USD historical source provides sufficient bid/ask or spread fidelity for V0.1/V0.2, and what are its licensing/redistribution limits?

- **Primary decision horizon:** Daily, hourly or mixed horizon? Start with the horizon that can be simulated honestly with available data, not the one that appears most profitable.

- **Broker choice:** Which broker/API is available in the relevant jurisdiction, with trading-only credentials, account minimums, margin rules, minimum size and reliable paper/shadow facilities?

- **USD 50 feasibility:** At the chosen broker, what minimum unit size, spread, commission and financing make a USD 50 live account feasible or infeasible?

- **Death threshold:** What protective terminal threshold should apply in simulation vs paper vs live, and how does it interact with margin liquidation?

- **Spread/slippage model:** Which historical or broker-derived model best represents time-of-day/event-state costs?

- **Swap model:** How should theoretical carry vs broker rollover be separated in features and execution P&L?

- **Macro vintage source:** Which provider(s) offer reliable release timestamps, consensus and historical vintages for the target economies?

- **News licensing:** Which news sources permit automated use, storage and historical replay?

- **Agent model choice:** Which LLMs are most reliable for structured extraction/numeracy at acceptable cost/latency? This is a research choice, not an architectural dependency.

- **Ensemble method:** Linear/shrinkage/Bayesian/stacking approach? Must be selected through controlled OOS tests, not aesthetic preference.

- **Uncertainty model:** Prediction intervals, conformal methods, Bayesian estimates or empirical forecast-error models?

- **Regime definition:** Hard labels vs probabilities; which states are observable without hindsight and improve decisions?

- **Multiple-testing budget:** How many feature/parameter trials trigger DSR/PBO/reporting requirements and how should related hypotheses be grouped?

- **Memory adaptation:** What sample-size/confidence requirements are needed before statistical memory may alter weights?

- **Execution kernel migration:** At what complexity point should custom V0.x simulator yield to NautilusTrader or another mature engine?

- **Cloud/VPS choice:** Select only after workload, data/broker location, uptime and security requirements are clear.

- **Dashboard auth:** Which authentication/authorization system protects the Netlify control center and high-risk actions?

- **Production promotion:** Which gates can eventually be automated, and which should remain explicit human approvals?

- **Live scaling:** How is capital increased, if ever, based on forward evidence, drawdown and capacity rather than backtest confidence?

- **Regulatory/tax/terms review:** Before live trading or commercialization, confirm applicable broker terms, data licenses, local regulatory/tax obligations and software licenses.

- **RL boundary:** Identify one bounded RL task and a deterministic control before any RL work is authorized.

- **Population statistics:** How many organism runs are needed to make survival comparisons meaningful without creating a new selection-bias problem?

# 24. Source Catalog

## 24.1 Primary repository and project sources

- **TradingAgents:** Repository: [https://github.com/TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents); Paper: [https://arxiv.org/abs/2412.20138](https://arxiv.org/abs/2412.20138)

- **AgenticTrading:** Repository: [https://github.com/Open-Finance-Lab/AgenticTrading](https://github.com/Open-Finance-Lab/AgenticTrading); Paper: [https://arxiv.org/abs/2512.02227](https://arxiv.org/abs/2512.02227)

- **FinRobot:** Repository: [https://github.com/AI4Finance-Foundation/FinRobot](https://github.com/AI4Finance-Foundation/FinRobot)

- **FinCon:** Repository: [https://github.com/The-FinAI/FinCon](https://github.com/The-FinAI/FinCon); Paper: [https://arxiv.org/abs/2407.06567](https://arxiv.org/abs/2407.06567)

- **FINMEM:** Repository: [https://github.com/wilfrid51/FINMEM](https://github.com/wilfrid51/FINMEM); Paper: [https://arxiv.org/abs/2311.13743](https://arxiv.org/abs/2311.13743)

- **FinAgent:** Paper: [https://arxiv.org/abs/2402.18485](https://arxiv.org/abs/2402.18485)

- **AI-Trader:** Repository: [https://github.com/HKUDS/AI-Trader](https://github.com/HKUDS/AI-Trader); Paper: [https://arxiv.org/abs/2512.10971](https://arxiv.org/abs/2512.10971)

- **StockBench:** Repository: [https://github.com/ChenYXxxx/stockbench](https://github.com/ChenYXxxx/stockbench); Paper: [https://arxiv.org/abs/2510.02209](https://arxiv.org/abs/2510.02209)

- **QuantConnect LEAN:** Repository: [https://github.com/QuantConnect/Lean](https://github.com/QuantConnect/Lean)

- **NautilusTrader:** Repository: [https://github.com/nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader)

- **Qlib:** Repository: [https://github.com/microsoft/qlib](https://github.com/microsoft/qlib)

- **vectorbt:** Repository: [https://github.com/polakowo/vectorbt](https://github.com/polakowo/vectorbt)

- **FinRL:** Repository: [https://github.com/AI4Finance-Foundation/FinRL](https://github.com/AI4Finance-Foundation/FinRL)

- **Vibe-Trading:** Repository: [https://github.com/HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading)

- **QuantDinger:** Repository: [https://github.com/OpenByteInc/QuantDinger](https://github.com/OpenByteInc/QuantDinger)

### Official online references specifically used for online-only architecture verification

- QuantConnect LEAN engine: [https://github.com/QuantConnect/Lean/blob/master/Engine/Engine.cs](https://github.com/QuantConnect/Lean/blob/master/Engine/Engine.cs)

- QuantConnect LEAN launcher/config: [https://github.com/QuantConnect/Lean/blob/master/Launcher/config.json](https://github.com/QuantConnect/Lean/blob/master/Launcher/config.json)

- NautilusTrader documentation: [https://nautilustrader.io/docs/](https://nautilustrader.io/docs/)

- NautilusTrader concepts: [https://nautilustrader.io/docs/latest/concepts/](https://nautilustrader.io/docs/latest/concepts/)

- NautilusTrader high-level backtesting: [https://nautilustrader.io/docs/latest/getting_started/backtest_high_level/](https://nautilustrader.io/docs/latest/getting_started/backtest_high_level/)

- NautilusTrader live configuration: [https://nautilustrader.io/docs/latest/how_to/configure_live_trading/](https://nautilustrader.io/docs/latest/how_to/configure_live_trading/)

- vectorbt documentation: [https://vectorbt.dev/](https://vectorbt.dev/)

- vectorbt usage/features: [https://vectorbt.dev/getting-started/usage/](https://vectorbt.dev/getting-started/usage/) and [https://vectorbt.dev/getting-started/features/](https://vectorbt.dev/getting-started/features/)

## 24.2 Finance course sources

- FIN826_Foundation I(1).pdf - Foundations I: The Investment Environment and the Language of Returns.

- FIN826_Foundation II(1).pdf - Foundations II: Risk, Risk Aversion, and Capital Allocation.

- Finance_Python_Notebook_1_BASICS(1).ipynb - Python Basics for Finance.

- Finance_Python_Notebook_2_LIBRARIES(1).ipynb - Python Libraries for Finance.

## 24.3 Prior project research artifacts

- AI_Trading_Agent_Research_Dossier.md - early repository/product/research map.

- AI_Trading_Repository_Deep_Analysis.docx/.pdf - source-level repository synthesis and target architecture.

- AI_Trading_100plus_Literature_Review.pdf - 129-source literature synthesis.

- AI_Trading_129_Source_Evidence_Audit.xlsx and summary PDF - source-by-source evidence classification, action and review depth.

- AI-Trading-100plus-Research-Synthesis.md and source catalog CSV - earlier synthesis artifacts; treated as supplementary because the 129-source audit is the more complete catalog.

# Appendix A. Primary File Traceability

## A.1 AgenticTrading-main.zip

- Size: 18,947,746 bytes

- SHA-256: 18b9e9a535623806cafd4b6cbc28170797dff36cb48f29f24258079c07268d52

- Role: repository snapshot

## A.2 AI-Trader-main.zip

- Size: 1,111,480 bytes

- SHA-256: f6b689ff86cd3aa2c35b582823f075322b056538fc66638bc2262bdb143d17ba

- Role: repository snapshot

## A.3 FinCon-main.zip

- Size: 1,885 bytes

- SHA-256: 7528db5244b3dbff85d3075c364fc10f8909d408570e9d45e2a27c7ad0b12d68

- Role: repository snapshot

## A.4 FINMEM-main.zip

- Size: 25,951,858 bytes

- SHA-256: 0f086e4566ee022fcc133793a7d48fe3ca983b3d46c5e5bc5f77a9d23a5e707d

- Role: repository snapshot

## A.5 FinRL-master.zip

- Size: 15,170,439 bytes

- SHA-256: 13860748ae00a40f1f62e837cb554c02fd081c472a98d9f11e19f4f840177292

- Role: repository snapshot

## A.6 FinRobot-master.zip

- Size: 11,509,640 bytes

- SHA-256: b428a07a95ade072e9df9b08b904f393622ee92e53be55fd5cef713da5922972

- Role: repository snapshot

## A.7 qlib-main.zip

- Size: 5,250,376 bytes

- SHA-256: 32f3da76915542ab24e379238b9d76e53006d073feba67f9361de9585611c37c

- Role: repository snapshot

## A.8 QuantDinger-main.zip

- Size: 14,147,739 bytes

- SHA-256: 68725dcf1c8cfb502d86f3d8e87d3240bc38b6d44fb41dd8935597811ca371dd

- Role: repository snapshot

## A.9 stockbench-main.zip

- Size: 14,029,238 bytes

- SHA-256: 5ba6393890584180ff31d679720c8985bf6d17240c8e7b0993ae3ab315923522

- Role: repository snapshot

## A.10 TradingAgents-main.zip

- Size: 3,571,877 bytes

- SHA-256: 675b7ab55a920864bb1e60bce1f01bd268b986dece93f17fdba563706e9d3a6c

- Role: repository snapshot

## A.11 Vibe-Trading-main.zip

- Size: 49,628,066 bytes

- SHA-256: a8ecc353700133ab3a2714e0825f9c71eb41f2cf083da5878f9e1510a4f34624

- Role: repository snapshot

## A.12 FIN826_Foundation I(1).pdf

- Size: 384,434 bytes

- SHA-256: 9e48ba386c545d8248bbc86e589e59b5e8aa0b07e02168bc86a9baf013b46392

- Role: course source

## A.13 FIN826_Foundation II(1).pdf

- Size: 370,931 bytes

- SHA-256: 0f6d6de0e8865f34d1270222bedaca5ea800db4fee325d200d0a0494a02ae4f1

- Role: course source

## A.14 Finance_Python_Notebook_1_BASICS(1).ipynb

- Size: 34,842 bytes

- SHA-256: d3563c50ca893eeb51c92c6c1cf64471ed3ea3d189417fcbb6f003f78c5a47cf

- Role: course source

## A.15 Finance_Python_Notebook_2_LIBRARIES(1).ipynb

- Size: 227,466 bytes

- SHA-256: abcaf15a4b69e568db1d002057b9cd71868fbac4990343886dde267fa925a006

- Role: course source

## A.16 AI_Trading_Agent_Research_Dossier.md

- Size: 10,606 bytes

- SHA-256: 6b96446e2a2dd9278ef5f4b8e8b749e8544fa6a6904d372bb5eec785e8b1d3b8

- Role: project research/audit artifact

## A.17 AI_Trading_100plus_Literature_Review.pdf

- Size: 35,507 bytes

- SHA-256: 7ac1b957a5ba5fe9a1820c7e6706ef230c9462d668d6735a8b418bec8d57c813

- Role: project research/audit artifact

## A.18 AI_Trading_129_Source_Evidence_Audit.xlsx

- Size: 26,100 bytes

- SHA-256: 1d0234dd333a4649c2863bd77da7760dac0b4ccc0de46f1d735b3bd3db6d4faf

- Role: project research/audit artifact

## A.19 AI_Trading_129_Source_Evidence_Audit_Summary.pdf

- Size: 36,939 bytes

- SHA-256: 3a501bd20c4ee1b72f36f33355bce1c344616e4e1749a6853dcaa8dcd34cf158

- Role: project research/audit artifact

## A.20 AI_Trading_Repository_Deep_Analysis.docx

- Size: 55,129 bytes

- SHA-256: 56ec554a362bf761f53be7c19e395e428e54f8b68dff39565c09404f033804fa

- Role: project research/audit artifact

## A.21 AI_Trading_Repository_Deep_Analysis.pdf

- Size: 327,116 bytes

- SHA-256: 27569bf042c2d7de62a2affe98aa772f5639313065f1098f62062703e8b332cf

- Role: project research/audit artifact

## A.22 AI-Trading-100plus-Research-Synthesis.md

- Size: 7,570 bytes

- SHA-256: 00ab87eaf2be1fbaef4d3ba70b47cfc529c1fd86c4d5821a50c71e84f81e7157

- Role: project research/audit artifact

## A.23 AI-Trading-100plus-Source-Catalog.csv

- Size: 2,684 bytes

- SHA-256: 744035bc9341788e86b087d9e2a63affd00bd2ef4b0a3303f844fe98fc8a7ff7

- Role: project research/audit artifact

# Appendix B. Full 129-Source Evidence Audit

This appendix preserves every entry from the project evidence workbook. **Review depth is shown for every source.** Assessments are the project audit notes, not claims that every full paper was read. A future agent should revisit primary texts when a source becomes implementation-critical.

## B - LLM/Agent

### S1. When Agents Trade: Live Multi-Market Trading Benchmark for LLM Agents

**Evidence:** High
**Classification:** CORE
**Action:** MODIFY
**Stance:** Challenging
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Live multi-market benchmark: architecture/risk style can drive behavior more than model backbone.
**Maysani Quant implication:** Benchmark agent architecture and risk policy separately from LLM model choice; use live paper evaluation.
**URL:** [https://arxiv.org/abs/2510.11695](https://arxiv.org/abs/2510.11695)

### S2. Large Language Model Agent in Financial Trading: A Survey

**Evidence:** Medium-High
**Classification:** SUPPORTING
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Relevant to LLM research, financial reasoning, RAG, memory, sentiment, or multi-agent architectures.
**Maysani Quant implication:** Use LLMs for research/feature extraction/critique; do not grant direct sizing or risk authority without deterministic validation.
**URL:** [https://arxiv.org/abs/2408.06361](https://arxiv.org/abs/2408.06361)

### S3. StockBench: Can LLM Agents Trade Stocks Profitably In Real-world Markets?

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Contamination-aware sequential trading benchmark; most models struggle versus simple baselines.
**Maysani Quant implication:** Every AI feature must beat no-LLM and simple trading baselines on unseen periods.
**URL:** [https://arxiv.org/abs/2510.02209](https://arxiv.org/abs/2510.02209)

### S4. The New Quant: A Survey of Large Language Models in Financial Prediction and Trading

**Evidence:** Medium-High
**Classification:** SUPPORTING
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Relevant to LLM research, financial reasoning, RAG, memory, sentiment, or multi-agent architectures.
**Maysani Quant implication:** Use LLMs for research/feature extraction/critique; do not grant direct sizing or risk authority without deterministic validation.
**URL:** [https://arxiv.org/abs/2510.05533](https://arxiv.org/abs/2510.05533)

### S5. From Knowing to Doing: A Memory-Controlled Benchmark for LLM Trading Agents on Stock Markets

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Memory-controlled benchmark designed to separate memorized knowledge from actual sequential trading skill.
**Maysani Quant implication:** Use date/ticker masking and provenance checks when evaluating agent memory or historical reasoning.
**URL:** [https://arxiv.org/abs/2605.28359](https://arxiv.org/abs/2605.28359)

### S6. AlphaForgeBench: Benchmarking End-to-End Trading Strategy Design with Large Language Models

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Reframes LLMs as strategy/factor designers whose outputs are executable and testable.
**Maysani Quant implication:** Use AI to generate hypotheses/features; deterministic code measures edge and decides whether a factor survives.
**URL:** [https://arxiv.org/abs/2602.18481](https://arxiv.org/abs/2602.18481)

### S7. Finance Agent Benchmark: Benchmarking LLMs on Real-world Financial Research Tasks

**Evidence:** High
**Classification:** CORE
**Action:** MODIFY
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Measures financial research capability rather than assuming trading P&L from general reasoning skill.
**Maysani Quant implication:** Evaluate research quality separately from trading quality; good analysis is not sufficient evidence of alpha.
**URL:** [https://arxiv.org/abs/2508.00828](https://arxiv.org/abs/2508.00828)

### S8. TradingAgents: Multi-Agents LLM Financial Trading Framework

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** MODIFY
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Useful multi-agent investment-firm workflow but final decisions remain LLM-heavy.
**Maysani Quant implication:** Reuse orchestration/audit patterns; replace trade/risk core with quantitative and deterministic modules.
**URL:** [https://arxiv.org/abs/2412.20138](https://arxiv.org/abs/2412.20138)

### S9. A Multimodal Foundation Agent for Financial Trading: Tool-Augmented, Diversified, and Generalist

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** MODIFY
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Relevant to LLM research, financial reasoning, RAG, memory, sentiment, or multi-agent architectures.
**Maysani Quant implication:** Use LLMs for research/feature extraction/critique; do not grant direct sizing or risk authority without deterministic validation.
**URL:** [https://arxiv.org/abs/2402.18485](https://arxiv.org/abs/2402.18485)

### S10. FinTradeBench: A Financial Reasoning Benchmark for LLMs

**Evidence:** High
**Classification:** CORE
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Financial reasoning benchmark useful for testing numerical/decision reliability.
**Maysani Quant implication:** Use benchmark-style tests for agent numeracy before trusting structured financial extraction.
**URL:** [https://arxiv.org/abs/2603.19225](https://arxiv.org/abs/2603.19225)

### S11. FinanceReasoning: Benchmarking Financial Numerical Reasoning More Credible, Comprehensive and Challenging

**Evidence:** High
**Classification:** CORE
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Targets credible financial numerical reasoning and exposes weaknesses in reasoning accuracy.
**Maysani Quant implication:** Add unit tests/evaluation sets for arithmetic, ratios, and financial logic in agent outputs.
**URL:** [https://arxiv.org/abs/2506.05828](https://arxiv.org/abs/2506.05828)

### S12. FinVerse: Financial Time-Series Benchmark

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Financial time-series benchmark relevant to model-selection claims.
**Maysani Quant implication:** Use benchmark tasks only as model screening; trading promotion still requires our own FX walk-forward tests.
**URL:** [https://arxiv.org/abs/2608.03259](https://arxiv.org/abs/2608.03259)

### S13. Retrieval Augmented Generation (RAG) for Fintech: Agentic Design and Evaluation

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Relevant to LLM research, financial reasoning, RAG, memory, sentiment, or multi-agent architectures.
**Maysani Quant implication:** Use LLMs for research/feature extraction/critique; do not grant direct sizing or risk authority without deterministic validation.
**URL:** [https://arxiv.org/abs/2510.25518](https://arxiv.org/abs/2510.25518)

### S14. Fine-Tuning Large Language Models for Stock Return Prediction Using Newsflow

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Relevant to LLM research, financial reasoning, RAG, memory, sentiment, or multi-agent architectures.
**Maysani Quant implication:** Use LLMs for research/feature extraction/critique; do not grant direct sizing or risk authority without deterministic validation.
**URL:** [https://arxiv.org/abs/2407.18103](https://arxiv.org/abs/2407.18103)

### S15. FinBERT: Financial Sentiment Analysis with Pre-trained Language Models

**Evidence:** High
**Classification:** SUPPORTING
**Action:** TEST
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Finance-domain sentiment model establishes strong text classification baseline.
**Maysani Quant implication:** Use as a baseline for event/sentiment extraction, not as a direct trading rule.
**URL:** [https://arxiv.org/abs/1908.10063](https://arxiv.org/abs/1908.10063)

### S16. Financial sentiment analysis using FinBERT with application in predicting stock movement

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Relevant to LLM research, financial reasoning, RAG, memory, sentiment, or multi-agent architectures.
**Maysani Quant implication:** Use LLMs for research/feature extraction/critique; do not grant direct sizing or risk authority without deterministic validation.
**URL:** [https://arxiv.org/abs/2306.02136](https://arxiv.org/abs/2306.02136)

### S17. BloombergGPT: A Large Language Model for Finance

**Evidence:** High
**Classification:** REFERENCE
**Action:** REFERENCE
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Finance-domain language model evidence for domain adaptation.
**Maysani Quant implication:** Useful for choosing research models; not evidence of profitable trading.
**URL:** [https://arxiv.org/abs/2303.17564](https://arxiv.org/abs/2303.17564)

### S18. Sentiment-driven prediction of financial returns: a Bayesian-enhanced FinBERT approach

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Relevant to LLM research, financial reasoning, RAG, memory, sentiment, or multi-agent architectures.
**Maysani Quant implication:** Use LLMs for research/feature extraction/critique; do not grant direct sizing or risk authority without deterministic validation.
**URL:** [https://arxiv.org/abs/2403.04427](https://arxiv.org/abs/2403.04427)

### S19. RAGCHECKER: A Fine-grained Framework for Diagnosing Retrieval-Augmented Generation

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** RAG evaluation framework focuses on retrieval and generation failure modes.
**Maysani Quant implication:** Instrument retrieval quality, faithfulness, source dating and answer provenance in our research agent.
**URL:** [https://arxiv.org/abs/2408.08067](https://arxiv.org/abs/2408.08067)

### S20. DEVIL'S ADVOCATE: Anticipatory Reflection for LLM Agents

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** MODIFY
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Adversarial reflection can improve agent reasoning but does not prove trading edge.
**Maysani Quant implication:** Use critic agents to falsify hypotheses, not to cast votes that count as independent signals.
**URL:** [https://arxiv.org/abs/2405.16334](https://arxiv.org/abs/2405.16334)

## B - Validation

### S21. The Probability of Backtest Overfitting

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253)

### S22. Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659)

### S23. Mathematical Appendices to: The Probability of Backtest Overfitting

**Evidence:** High
**Classification:** REFERENCE
**Action:** REFERENCE
**Stance:** Supportive
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Mathematical appendix to PBO rather than an independent trading result.
**Maysani Quant implication:** Keep as technical reference for implementing/validating PBO calculations.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2568435](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2568435)

### S24. Backtest Overfitting in Financial Markets

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2731886](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2731886)

### S25. The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551)

### S26. Stock Portfolio Design and Backtest Overfitting

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2739335](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2739335)

### S27. How Hard Is It to Pick the Right Model? MCS and Backtest Overfitting

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3044740](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3044740)

### S28. All that Glitters Is Not Gold: Comparing Backtest and Out-of-Sample Performance on a Large Cohort of Trading Algorithms

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Large cohort of 888 algorithms shows weak relationship between backtest Sharpe and live/OOS performance.
**Maysani Quant implication:** Track search intensity and downgrade strategies selected from many trials; do not rank solely by backtest Sharpe.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2745220](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2745220)

### S29. ... and the Cross-Section of Expected Returns

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Shows conventional significance thresholds are too weak after large-scale factor mining.
**Maysani Quant implication:** Raise significance hurdle and account for correlated multiple testing in alpha discovery.
**URL:** [https://www.nber.org/papers/w20592](https://www.nber.org/papers/w20592)

### S30. Backtesting

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2345489](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2345489)

### S31. Evaluating Trading Strategies

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2474755](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2474755)

### S32. What Threshold Should be Applied to Tests of Factor Models?

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Updates factor-model significance guidance; dependence and sample-selection matter.
**Maysani Quant implication:** Use stronger statistical thresholds/local FDR in automated factor discovery.
**URL:** [https://www.nber.org/papers/w34898](https://www.nber.org/papers/w34898)

### S33. Re-Examining the Profitability of Technical Analysis with White's Reality Check and Hansen's SPA Test

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=685361](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=685361)

### S34. A Stepwise SPA Test for Data Snooping and its Application on Fund Performance Evaluation

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=885364](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=885364)

### S35. Evaluation Integrity in Machine Learning for Finance

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** REFERENCE
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7007079](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7007079)

### S36. Epistemic Failure and Methodological Reform in Financial Machine Learning

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** REFERENCE
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6245658](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6245658)

### S37. Beyond Accuracy: A Validation Framework for Machine Learning in Cryptocurrency Trading

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** REFERENCE
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6508779](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6508779)

### S38. Quantifying Backtest Overfitting from Information Leakage

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** REFERENCE
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7029819](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7029819)

### S39. Susceptibility-graded Release Control: Preventing Incomplete-cross-section Leakage

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** REFERENCE
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7391122](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7391122)

### S40. When Not to Trade: Leakage-Aware Selective Machine Learning for Factor Rotation

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** REFERENCE
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly addresses backtest overfitting, selection bias, leakage, multiple testing, or performance-statistic reliability.
**Maysani Quant implication:** Build immutable experiment logging, walk-forward testing, multiple-testing controls, leakage checks, and corrected performance inference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7021298](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7021298)

### S41. The Statistics of Sharpe Ratios

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Sharpe estimation and annualization are distorted by serial correlation.
**Maysani Quant implication:** Use serial-correlation-aware Sharpe inference and confidence intervals.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=377260](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=377260)

## B - Quant/ML

### S42. Empirical Asset Pricing via Machine Learning

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Supportive
**Review depth:** Abstract/official summary assessed
**Assessment:** High-quality ML asset-pricing evidence that nonlinear models can capture predictive structure.
**Maysani Quant implication:** Use as methodological reference, not direct FX proof; compare nonlinear models to transparent baselines.
**URL:** [https://www.nber.org/papers/w25398](https://www.nber.org/papers/w25398)

### S43. Artificial Intelligence Asset Pricing Models

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Supportive
**Review depth:** Abstract/official summary assessed
**Assessment:** Modern AI asset-pricing models show flexible models can capture pricing relationships.
**Maysani Quant implication:** Treat as model-class evidence; require FX-specific replication and interpretability.
**URL:** [https://www.nber.org/papers/w33351](https://www.nber.org/papers/w33351)

### S44. On the Limits of Low-Frequency OHLCV Signals in Machine Learning-Driven Portfolio Optimization

**Evidence:** Medium
**Classification:** WEAK EVIDENCE
**Action:** REFERENCE
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Questions information content of low-frequency OHLCV-only ML systems.
**Maysani Quant implication:** Do not assume deep models can create edge from sparse OHLCV; test incremental information content.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6952859](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6952859)

### S45. Combining Deep Learning and GARCH Models for Financial Volatility and Risk Forecasting

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** TEST
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Hybrid GARCH/deep models improve point volatility in some assets, but risk forecasts do not automatically improve.
**Maysani Quant implication:** Keep classical GARCH baselines and evaluate volatility forecasts separately from VaR/ES usefulness.
**URL:** [https://arxiv.org/abs/2310.01063](https://arxiv.org/abs/2310.01063)

### S46. GARCH-Informed Neural Networks for Volatility Prediction in Financial Markets

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** TEST
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Hybrid GARCH-informed neural model reports OOS volatility improvements.
**Maysani Quant implication:** Candidate later model; benchmark against GARCH/EGARCH with FX data before use.
**URL:** [https://arxiv.org/abs/2410.00288](https://arxiv.org/abs/2410.00288)

### S47. Portfolio Management using Deep Reinforcement Learning

**Evidence:** Low-Medium
**Classification:** WEAK EVIDENCE
**Action:** POSTPONE
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** RL portfolio result is sensitive to simulator/reward design and is not FX-execution evidence.
**Maysani Quant implication:** Do not use RL in V1.
**URL:** [https://arxiv.org/abs/2405.01604](https://arxiv.org/abs/2405.01604)

### S48. A Deep Reinforcement Learning Framework for the Financial Portfolio Management Problem

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** POSTPONE
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Influential DRL portfolio framework but environment assumptions are simplified.
**Maysani Quant implication:** Study later after realistic deterministic simulator is established.
**URL:** [https://arxiv.org/abs/1706.10059](https://arxiv.org/abs/1706.10059)

### S49. Deep reinforcement learning for portfolio management

**Evidence:** Low-Medium
**Classification:** WEAK EVIDENCE
**Action:** POSTPONE
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Another DRL portfolio study with limited evidence of live robustness.
**Maysani Quant implication:** Postpone; use only as comparative research.
**URL:** [https://arxiv.org/abs/2012.13773](https://arxiv.org/abs/2012.13773)

### S50. Reinforcement Learning for Portfolio Management

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** POSTPONE
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** RL framework may help policy selection but requires careful environment design.
**Maysani Quant implication:** Potential later use for bounded tasks, not core signal/risk engine.
**URL:** [https://arxiv.org/abs/1909.09571](https://arxiv.org/abs/1909.09571)

### S51. Prediction of foreign currency exchange rates using an attention-based long short-term memory network

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** TEST
**Stance:** Supportive
**Review depth:** Abstract/official summary assessed
**Assessment:** Attention-LSTM FX forecasting is directly relevant but model results may be sample-specific.
**Maysani Quant implication:** Replicate on EUR/USD with purged walk-forward and realistic costs before considering.
**URL:** [https://www.sciencedirect.com/science/article/pii/S2666827025000313](https://www.sciencedirect.com/science/article/pii/S2666827025000313)

### S52. Comparing the forecasting performance of neural networks and forward exchange rates

**Evidence:** Medium
**Classification:** REFERENCE
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Abstract/official summary assessed
**Assessment:** Older neural-network versus forward-rate forecasting evidence; historically informative but dated technology/data.
**Maysani Quant implication:** Use as historical baseline context, not production design evidence.
**URL:** [https://www.sciencedirect.com/science/article/pii/S1042444X97000182](https://www.sciencedirect.com/science/article/pii/S1042444X97000182)

### S53. Time-Series Forecasting for Out-of-Distribution Generalization Using Invariant Learning

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** TEST
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Invariant learning targets out-of-distribution generalization, a key regime-change problem.
**Maysani Quant implication:** Candidate robustness technique after baseline models are established.
**URL:** [https://arxiv.org/abs/2406.09130](https://arxiv.org/abs/2406.09130)

### S54. SAMformer: Unlocking the Potential of Transformers in Time Series

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** TEST
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Modern transformer time-series architecture with general forecasting relevance.
**Maysani Quant implication:** Only test if it beats simple time-series models under our FX protocol.
**URL:** [https://arxiv.org/abs/2402.10198](https://arxiv.org/abs/2402.10198)

## B - FX Factors

### S55. Carry Trade and Momentum in Currency Markets

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum.
**Maysani Quant implication:** Use as transparent FX baselines and candidate features; never assume persistence after costs or publication.
**URL:** [https://www.nber.org/papers/w16942](https://www.nber.org/papers/w16942)

### S56. Currency Carry Trades

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum.
**Maysani Quant implication:** Use as transparent FX baselines and candidate features; never assume persistence after costs or publication.
**URL:** [https://www.nber.org/papers/w16491](https://www.nber.org/papers/w16491)

### S57. Carry Trades and Currency Crashes

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Carry strategies can exhibit crash risk and negative skew.
**Maysani Quant implication:** Carry signal must include volatility/liquidity/crash-state controls and strict leverage limits.
**URL:** [https://www.nber.org/papers/w14473](https://www.nber.org/papers/w14473)

### S58. The Carry Trade and Fundamentals: Nothing to Fear But FEER Itself

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Conditioning carry on fundamentals can improve risk-adjusted behavior in historical tests.
**Maysani Quant implication:** Test FEER/value conditioning as a candidate state feature, not a rule.
**URL:** [https://www.nber.org/papers/w15518](https://www.nber.org/papers/w15518)

### S59. The Cross-Section of Currency Risk Premia and US Consumption Growth Risk

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum.
**Maysani Quant implication:** Use as transparent FX baselines and candidate features; never assume persistence after costs or publication.
**URL:** [https://www.nber.org/papers/w11104](https://www.nber.org/papers/w11104)

### S60. The Cross-Section of Foreign Currency Risk Premia and Consumption Growth Risk: A Reply

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum.
**Maysani Quant implication:** Use as transparent FX baselines and candidate features; never assume persistence after costs or publication.
**URL:** [https://www.nber.org/papers/w13812](https://www.nber.org/papers/w13812)

### S61. Countercyclical Currency Risk Premia

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum.
**Maysani Quant implication:** Use as transparent FX baselines and candidate features; never assume persistence after costs or publication.
**URL:** [https://www.nber.org/papers/w16427](https://www.nber.org/papers/w16427)

### S62. Common Risk Factors in Currency Markets

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum.
**Maysani Quant implication:** Use as transparent FX baselines and candidate features; never assume persistence after costs or publication.
**URL:** [https://www.nber.org/papers/w14082](https://www.nber.org/papers/w14082)

### S63. The Term Structure of Currency Carry Trade Risk Premia

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum.
**Maysani Quant implication:** Use as transparent FX baselines and candidate features; never assume persistence after costs or publication.
**URL:** [https://www.nber.org/papers/w19623](https://www.nber.org/papers/w19623)

### S64. Economic Momentum and Currency Returns

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Economic momentum predicts currency returns in historical sample and adds beyond standard factors.
**Maysani Quant implication:** Test point-in-time macro trend features using unrevised/vintage data.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2579666](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2579666)

### S65. Dissecting Currency Momentum

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Currency momentum appears largely factor momentum rather than idiosyncratic pair momentum.
**Maysani Quant implication:** Model common factor momentum and avoid counting related momentum signals as independent.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3759017](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3759017)

### S66. Currency Carry, Momentum, and Global Interest Rate Volatility

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Links carry and momentum to global interest-rate volatility/intermediary constraints.
**Maysani Quant implication:** Add global rate-volatility regime feature and stress carry/momentum during volatility spikes.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3190657](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3190657)

### S67. Are Carry, Momentum and Value Still There in Currencies?

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Documents large post-publication deterioration in carry/momentum/value performance.
**Maysani Quant implication:** Treat classic currency factors as baselines and require recent OOS evidence; model alpha decay.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4024296](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4024296)

### S68. Out-of-Sample Evidence on the Returns to Currency Trading

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum.
**Maysani Quant implication:** Use as transparent FX baselines and candidate features; never assume persistence after costs or publication.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2444873](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2444873)

### S69. Currency Value

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum.
**Maysani Quant implication:** Use as transparent FX baselines and candidate features; never assume persistence after costs or publication.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2282480](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2282480)

### S70. Value and Momentum Everywhere

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Direct evidence on currency return predictors/risk premia such as carry, momentum, value, or economic momentum.
**Maysani Quant implication:** Use as transparent FX baselines and candidate features; never assume persistence after costs or publication.
**URL:** [https://conference.nber.org/confer/2008/si2008/AP/pedersen.pdf](https://conference.nber.org/confer/2008/si2008/AP/pedersen.pdf)

### S71. Volatility Managed Portfolios

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Supportive
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Volatility-managed exposure can improve risk-adjusted results in some settings.
**Maysani Quant implication:** Test volatility scaling, but attribute gains to trend/correlation effects and costs.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2773438](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2773438)

### S72. Volatility-Managed Portfolios

**Evidence:** High
**Classification:** DUPLICATE
**Action:** REFERENCE
**Stance:** Supportive
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Closely overlaps the volatility-managed portfolio literature already represented.
**Maysani Quant implication:** Keep for citation/replication context; avoid double-counting evidence.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2659431](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2659431)

### S73. Do Carry Trade Returns Follow A Random Walk?

**Evidence:** Low-Medium
**Classification:** WEAK EVIDENCE
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Narrow recent paper on carry return dynamics with limited validation weight.
**Maysani Quant implication:** Do not change architecture; retain as niche reference.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6844481](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6844481)

### S74. Portfolio Inertia and Expected Excess Returns in Currency Markets - Evidence from Advanced Economies

**Evidence:** High
**Classification:** SUPPORTING
**Action:** TEST
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Portfolio-inertia evidence may help explain currency excess returns in advanced economies.
**Maysani Quant implication:** Potential macro/flow feature later; not V1.
**URL:** [https://www.elibrary.imf.org/view/journals/001/2025/011/article-A001-en.xml](https://www.elibrary.imf.org/view/journals/001/2025/011/article-A001-en.xml)

### S75. Dominant Currency Pricing and Currency Risk Premia

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Dominant-currency pricing and dollar debt/invoicing link observable macro structure to currency premia.
**Maysani Quant implication:** Candidate slower-moving country-state features for cross-currency models.
**URL:** [https://www.imf.org/en/publications/wp/issues/2026/07/31/dominant-currency-pricing-and-currency-risk-premia-578314](https://www.imf.org/en/publications/wp/issues/2026/07/31/dominant-currency-pricing-and-currency-risk-premia-578314)

### S76. Carry Trade vs. Deposit-Driven Euroization

**Evidence:** Medium
**Classification:** REFERENCE
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Euroization/carry interaction is context-specific.
**Maysani Quant implication:** Retain only if expanding to relevant EM currencies.
**URL:** [https://www.imf.org/en/publications/wp/issues/2018/03/15/carry-trade-vs-45686](https://www.imf.org/en/publications/wp/issues/2018/03/15/carry-trade-vs-45686)

## B - FX Macro

### S77. The Out-of-Sample Failure of Empirical Exchange Rate Models: Sampling Error or Misspecification?

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Classic out-of-sample exchange-rate forecasting failure warns against overconfident macro models.
**Maysani Quant implication:** Macro agent cannot have unilateral trade authority; compare to random-walk benchmarks.
**URL:** [https://www.nber.org/books-and-chapters/exchange-rates-and-international-macroeconomics/out-sample-failure-empirical-exchange-rate-models-sampling-error-or-misspecification](https://www.nber.org/books-and-chapters/exchange-rates-and-international-macroeconomics/out-sample-failure-empirical-exchange-rate-models-sampling-error-or-misspecification)

### S78. The Six Major Puzzles in International Macroeconomics: Is There a Common Cause?

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Direct evidence on macroeconomic, monetary-policy, and exchange-rate mechanisms relevant to FX forecasting.
**Maysani Quant implication:** Macro agent should emit structured surprise/state variables; validate incremental value beyond price/carry baselines.
**URL:** [https://www.nber.org/papers/w7777](https://www.nber.org/papers/w7777)

### S79. Does Incomplete Spanning in International Financial Markets Help to Explain Exchange Rates?

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Direct evidence on macroeconomic, monetary-policy, and exchange-rate mechanisms relevant to FX forecasting.
**Maysani Quant implication:** Macro agent should emit structured surprise/state variables; validate incremental value beyond price/carry baselines.
**URL:** [https://www.nber.org/papers/w22023](https://www.nber.org/papers/w22023)

### S80. Can Oil Prices Forecast Exchange Rates?

**Evidence:** High
**Classification:** SUPPORTING
**Action:** TEST
**Stance:** Supportive
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Commodity prices may forecast some currencies with economic links.
**Maysani Quant implication:** Test only for commodity-linked currencies; not a generic EUR/USD assumption.
**URL:** [https://www.nber.org/papers/w17998](https://www.nber.org/papers/w17998)

### S81. Identifying the Effects of Monetary Policy Shocks on Exchange Rates Using High Frequency Data

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** High-frequency policy-surprise identification shows event timing matters for FX response.
**Maysani Quant implication:** Create event windows and structured surprise variables rather than daily sentiment alone.
**URL:** [https://www.nber.org/papers/w9660](https://www.nber.org/papers/w9660)

### S82. A Reassessment of Monetary Policy Surprises and High-Frequency Identification

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Reassesses high-frequency monetary surprises and identification assumptions.
**Maysani Quant implication:** Use multiple surprise dimensions and guard against mislabeled information shocks.
**URL:** [https://www.nber.org/papers/w29939](https://www.nber.org/papers/w29939)

### S83. Monetary Policy without Moving Interest Rates: The Fed Non-Yield Shock

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Supportive
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Shows monetary information can move assets without headline rate changes.
**Maysani Quant implication:** Extract non-yield/information shocks from policy communication as separate features.
**URL:** [https://www.nber.org/papers/w32636](https://www.nber.org/papers/w32636)

### S84. US Monetary Spillovers, Foreign Exchange, and Gold Reserves at Times of Geopolitical Fragmentation

**Evidence:** High
**Classification:** SUPPORTING
**Action:** TEST
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Reserve buffers can moderate FX responses to US policy shocks across countries.
**Maysani Quant implication:** Relevant to multi-currency expansion; not core EUR/USD V1.
**URL:** [https://www.nber.org/papers/w35337](https://www.nber.org/papers/w35337)

### S85. From press conferences to speeches: the impact of the ECB's monetary policy communication

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Supportive
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** ECB communications between meetings can materially shape expectations.
**Maysani Quant implication:** Continuously ingest speeches/communication with precise timestamps and event type.
**URL:** [https://www.ecb.europa.eu/press/economic-bulletin/focus/2025/html/ecb.ebbox202501_07~c37ab82e06.en.html](https://www.ecb.europa.eu/press/economic-bulletin/focus/2025/html/ecb.ebbox202501_07~c37ab82e06.en.html)

### S86. Monetary transmission with frequent policy events

**Evidence:** High
**Classification:** SUPPORTING
**Action:** TEST
**Stance:** Supportive
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Frequent policy-event framework is relevant to event-based macro modeling.
**Maysani Quant implication:** Use as support for a policy-event state machine if expanding macro layer.
**URL:** [https://www.ecb.europa.eu/pub/research/authors/profiles/thilo-kind.en.html](https://www.ecb.europa.eu/pub/research/authors/profiles/thilo-kind.en.html)

## B - FX Microstructure

### S87. The foreign exchange market

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Modern overview of FX market structure and participants.
**Maysani Quant implication:** Ground execution/data architecture in OTC fragmentation and heterogeneous liquidity.
**URL:** [https://www.bis.org/publications/working-paper-1094-foreign-exchange-market](https://www.bis.org/publications/working-paper-1094-foreign-exchange-market)

### S88. High-frequency trading in the foreign exchange market

**Evidence:** High
**Classification:** CORE
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** High-frequency FX trading changes liquidity/market dynamics.
**Maysani Quant implication:** Useful for future intraday design; not required for low-frequency V1.
**URL:** [https://www.bis.org/publications/high-frequency-trading-foreign-exchange-market](https://www.bis.org/publications/high-frequency-trading-foreign-exchange-market)

### S89. FX trade execution: complex and highly fragmented

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** FX execution is fragmented across venues, dealers and protocols.
**Maysani Quant implication:** Backtester must not assume a single centralized exchange or universal price.
**URL:** [https://www.bis.org/publications/qr-201912/fx-trade-execution-complex-and-highly-fragmented](https://www.bis.org/publications/qr-201912/fx-trade-execution-complex-and-highly-fragmented)

### S90. FX execution algorithms and market functioning

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Execution algorithms change how risk and liquidity are transferred.
**Maysani Quant implication:** Separate signal alpha from execution quality; add TCA when broker connectivity exists.
**URL:** [https://www.bis.org/publications/fx-execution-algorithms-and-market-functioning](https://www.bis.org/publications/fx-execution-algorithms-and-market-functioning)

### S91. Recent trends in the foreign exchange and money markets

**Evidence:** Medium-High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Directly explains FX market structure, order flow, liquidity, carry positioning, hedging, and execution mechanics.
**Maysani Quant implication:** Model bid/ask, venue/broker behavior, liquidity, order-flow context, rollover/forward basis, and execution constraints.
**URL:** [https://www.bis.org/speeches/20140329-recent-trends-foreign-exchange-and-money-markets](https://www.bis.org/speeches/20140329-recent-trends-foreign-exchange-and-money-markets)

### S92. Through stormy seas: how fragile is liquidity across asset classes and time?

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Liquidity fragility varies by asset and stress state.
**Maysani Quant implication:** Introduce spread/liquidity stress regimes and conservative fill assumptions.
**URL:** [https://www.bis.org/publications/working-paper-1229-through-stormy-seas-how-fragile-liquidity-across-asset-classes-and-time](https://www.bis.org/publications/working-paper-1229-through-stormy-seas-how-fragile-liquidity-across-asset-classes-and-time)

### S93. Order Flow and Exchange Rate Dynamics

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Order flow contains substantial short-horizon information in classic FX microstructure research.
**Maysani Quant implication:** Potential future high-frequency feature, contingent on reliable order-flow data access.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=295071](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=295071)

### S94. Exchange Rate Fundamentals and Order Flow

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Supportive
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Connects macro fundamentals with order flow as an information aggregation mechanism.
**Maysani Quant implication:** Use order flow as a bridge between news/macro and price when suitable data becomes available.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=992154](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=992154)

### S95. Understanding Order Flow

**Evidence:** High
**Classification:** CORE
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Explains informational content and interpretation of order flow.
**Maysani Quant implication:** Reference for future microstructure feature engineering.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=842482](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=842482)

### S96. Order Flow and Exchange Rate Dynamics in Electronic Brokerage System Data

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Electronic brokerage data shows order-flow effects, especially at high frequency.
**Maysani Quant implication:** Do not extrapolate short-horizon flow effects to long-horizon trades without testing.
**URL:** [https://www.federalreserve.gov/econres/ifdp/order-flow-and-exchange-rate-dynamics-in-electronic-brokerage-system-data.htm](https://www.federalreserve.gov/econres/ifdp/order-flow-and-exchange-rate-dynamics-in-electronic-brokerage-system-data.htm)

### S97. An empirical study of liquidity and information effects of order flow on exchange rates

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Separates liquidity and information effects of FX order flow.
**Maysani Quant implication:** If order flow is added, distinguish informed flow from liquidity-driven flow.
**URL:** [https://www.ecb.europa.eu/pub/research/authors/profiles/paolo-vitale.en.html](https://www.ecb.europa.eu/pub/research/authors/profiles/paolo-vitale.en.html)

### S98. A market microstructure analysis of foreign exchange intervention

**Evidence:** High
**Classification:** REFERENCE
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** FX intervention microstructure model is relevant mainly around official intervention.
**Maysani Quant implication:** Add intervention-event flag later; not V1.
**URL:** [https://www.ecb.europa.eu/pub/research/authors/profiles/paolo-vitale.en.html](https://www.ecb.europa.eu/pub/research/authors/profiles/paolo-vitale.en.html)

### S99. Covered interest parity lost: understanding the cross-currency basis

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** CIP deviations show funding/hedging constraints matter even for seemingly arbitrage-like relationships.
**Maysani Quant implication:** Do not derive carry/forward economics from naive interest differentials alone; include basis/hedging costs where relevant.
**URL:** [https://www.bis.org/publications/qr-201609/covered-interest-parity-lost-understanding-cross-currency-basis](https://www.bis.org/publications/qr-201609/covered-interest-parity-lost-understanding-cross-currency-basis)

### S100. CIP, FX swaps, cross-currency swaps and the factors that move the basis

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Supportive
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** Mechanics of FX swaps/cross-currency basis clarify real funding costs.
**Maysani Quant implication:** Use correct forward points/swap mechanics when modeling rollover/carry.
**URL:** [https://www.bis.org/publications/cip-fx-swaps-cross-currency-swaps-and-factors-move-basis](https://www.bis.org/publications/cip-fx-swaps-cross-currency-swaps-and-factors-move-basis)

### S101. Sizing up carry trades in BIS statistics

**Evidence:** High
**Classification:** SUPPORTING
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** Shows how difficult it is to infer actual carry positions from aggregate statistics.
**Maysani Quant implication:** Treat positioning estimates as noisy features with explicit uncertainty.
**URL:** [https://www.bis.org/publications/sizing-carry-trades-bis-statistics](https://www.bis.org/publications/sizing-carry-trades-bis-statistics)

### S102. Carry off, carry on

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Recent carry unwinds highlight leverage and crowding risk.
**Maysani Quant implication:** Stress carry exposures under sudden funding-currency reversals.
**URL:** [https://www.bis.org/publications/qr-202409/carry-off-carry-on](https://www.bis.org/publications/qr-202409/carry-off-carry-on)

### S103. Monetary policy transmission to exchange rates: the role of currency carry trades

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Supportive
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** Carry positions can amplify exchange-rate response to policy tightening.
**Maysani Quant implication:** Add carry-positioning/state interaction around policy events if data is available.
**URL:** [https://www.bis.org/publications/bulletin-124-monetary-policy-transmission-exchange-rates-role-currency-carry-trades](https://www.bis.org/publications/bulletin-124-monetary-policy-transmission-exchange-rates-role-currency-carry-trades)

### S104. Evidence of carry trade activity

**Evidence:** High
**Classification:** REFERENCE
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Historical evidence on detecting carry activity from imperfect data.
**Maysani Quant implication:** Use for positioning-data caveats.
**URL:** [https://www.bis.org/publications/evidence-carry-trade-activity](https://www.bis.org/publications/evidence-carry-trade-activity)

### S105. The anatomy of the global FX market through the lens of the 2013 Triennial Survey

**Evidence:** High
**Classification:** REFERENCE
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** Describes global FX participant/venue structure from 2013 survey.
**Maysani Quant implication:** Historical market-structure baseline; prefer newer 2025 survey for current architecture.
**URL:** [https://www.bis.org/publications/qr-201312/anatomy-global-fx-market-through-lens-2013-triennial-survey](https://www.bis.org/publications/qr-201312/anatomy-global-fx-market-through-lens-2013-triennial-survey)

### S106. Global FX markets when hedging takes centre stage

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Mixed
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** 2025 survey shows hedging, internalization, forwards/options and dealer behavior are central to modern FX.
**Maysani Quant implication:** Use latest market structure for execution assumptions and liquidity context.
**URL:** [https://www.bis.org/publications/qr-202512/global-fx-markets-when-hedging-takes-centre-stage](https://www.bis.org/publications/qr-202512/global-fx-markets-when-hedging-takes-centre-stage)

### S107. Renminbi propels the growth of EME currency trading

**Evidence:** High
**Classification:** REFERENCE
**Action:** REFERENCE
**Stance:** Mixed
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** Current EME turnover trends are useful for future universe expansion.
**Maysani Quant implication:** No effect on EUR/USD V1.
**URL:** [https://www.bis.org/publications/qr-202512/renminbi-propels-growth-eme-currency-trading](https://www.bis.org/publications/qr-202512/renminbi-propels-growth-eme-currency-trading)

## B - Risk/Execution

### S108. Optimal Liquidation

**Evidence:** High
**Classification:** CORE
**Action:** REFERENCE
**Stance:** Supportive
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Foundational optimal execution tradeoff between risk and impact.
**Maysani Quant implication:** Architecture reference; small-account V1 likely spread/slippage dominated rather than market-impact dominated.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=53501)

### S109. Revisiting Optimal Execution of Portfolio Transactions: A Dynamic Programming and Reinforcement Learning Approach

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** POSTPONE
**Stance:** Supportive
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** RL execution approach is relevant only after execution simulator is credible.
**Maysani Quant implication:** Potential future bounded RL task.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4508553](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4508553)

### S110. Market Impact Models for Small Funds: Practical Execution Alpha, Intraday Liquidity Dynamics, and the Microstructure of Trading

**Evidence:** Low-Medium
**Classification:** WEAK EVIDENCE
**Action:** REFERENCE
**Stance:** Supportive
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Recent small-fund execution paper is practical but not yet strongly validated.
**Maysani Quant implication:** Use as idea source only; verify formulas against established microstructure literature.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6301920](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6301920)

### S111. Strategic Risk Management: Out-of-Sample Evidence from the COVID-19 Equity Selloff

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Supportive
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Out-of-sample crisis evidence supports dynamic risk management.
**Maysani Quant implication:** Stress-test risk throttles on crisis windows rather than optimizing only average periods.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3655196](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3655196)

### S112. Volatility Targeting Is Trendy: How Trend Following Explains Alpha in Volatility-Managed Strategies

**Evidence:** Medium-High
**Classification:** SUPPORTING
**Action:** TEST
**Stance:** Challenging
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Shows volatility targeting alpha can be explained by trend in equities, but not universally across currencies.
**Maysani Quant implication:** Do not count volatility targeting as independent FX alpha; test attribution.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4773781](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4773781)

### S113. Trend-Following, Risk-Parity and the Influence of Correlations

**Evidence:** High
**Classification:** CORE
**Action:** TEST
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Correlation-aware risk-parity can matter when asset correlations rise.
**Maysani Quant implication:** If multi-pair portfolio is added, account for changing correlations rather than only inverse volatility.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2673124](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2673124)

### S114. The Trend is Our Friend: Risk Parity, Momentum and Trend Following in Global Asset Allocation

**Evidence:** Medium-High
**Classification:** SUPPORTING
**Action:** REFERENCE
**Stance:** Supportive
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Cross-asset trend/momentum evidence is informative but not FX-specific.
**Maysani Quant implication:** Reference for trend design; require FX replication.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2265693](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2265693)

### S115. Tail Protection for Long Investors: Trend Convexity at Work

**Evidence:** High
**Classification:** CORE
**Action:** REFERENCE
**Stance:** Supportive
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Trend convexity can provide tail protection in diversified settings.
**Maysani Quant implication:** Use as risk-factor understanding; do not assume a single-pair FX trend strategy has the same protection.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2777657](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2777657)

### S116. Do Downside Floors Hold Out of Sample? CVaR-Constrained Optimisation of Derivative-Bearing Portfolios

**Evidence:** Medium
**Classification:** SUPPORTING
**Action:** TEST
**Stance:** Mixed
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** CVaR downside floors are attractive but need true OOS validation.
**Maysani Quant implication:** Compare CVaR constraints to simpler drawdown/position limits before adding complexity.
**URL:** [https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6915241](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6915241)

### S117. Market risk terminology - Basel Framework

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Neutral
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Official market-risk terminology and framework.
**Maysani Quant implication:** Use consistent definitions of risk factors/positions and expected-shortfall concepts.
**URL:** [https://www.bis.org/committees/bcbs/basel-framework/standard/mar/10/inforce/2023-01-01/published/2020-03-27](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/10/inforce/2023-01-01/published/2020-03-27)

### S118. Market risk - Basel Framework

**Evidence:** High
**Classification:** REFERENCE
**Action:** REFERENCE
**Stance:** Neutral
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Bank regulatory market-risk disclosure framework is broader than our system needs.
**Maysani Quant implication:** Use terminology/reference only; not a trading model.
**URL:** [https://www.bis.org/committees/bcbs/basel-framework/standard/dis/50/inforce/2023-01-01/published/2020-03-27](https://www.bis.org/committees/bcbs/basel-framework/standard/dis/50/inforce/2023-01-01/published/2020-03-27)

### S119. Foreign exchange risks - Basel Consolidated Guidelines

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Neutral
**Review depth:** Primary abstract/official page reviewed directly
**Assessment:** Official guidance on FX settlement, liquidity and replacement-cost risks.
**Maysani Quant implication:** Operational risk checklist for eventual live broker/counterparty integration.
**URL:** [https://www.bis.org/committees/bcbs/basel-consolidated-guidelines/module/rma/20](https://www.bis.org/committees/bcbs/basel-consolidated-guidelines/module/rma/20)

### S120. FX Global Code

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Neutral
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** Global principles for fair, robust FX market practice.
**Maysani Quant implication:** Use as execution-governance reference for broker/venue selection and audit.
**URL:** [https://www.globalfxc.org/fx-global-code/](https://www.globalfxc.org/fx-global-code/)

### S121. GFXC Execution Principles Working Group Report on Last Look

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** Last-look practice can cause request rejection and adverse execution outcomes.
**Maysani Quant implication:** Simulator/live TCA should track rejection rates, latency and price after rejection when relevant.
**URL:** [https://www.globalfxc.org/uploads/gfxc_report_last_look-1.pdf](https://www.globalfxc.org/uploads/gfxc_report_last_look-1.pdf)

### S122. The FX Global Code - BIS remarks on algo due diligence and TCA

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Neutral
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Official emphasis on algo due diligence and transaction-cost analysis.
**Maysani Quant implication:** Add broker/algo due-diligence checklist and TCA before live deployment.
**URL:** [https://www.bis.org/speeches/20210729-fx-global-code](https://www.bis.org/speeches/20210729-fx-global-code)

### S123. Updates to the FX Global Code

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Neutral
**Review depth:** Abstract/search/official summary assessed; full text not always directly accessible
**Assessment:** Updates reinforce current FX Code execution expectations.
**Maysani Quant implication:** Keep operational policy current as broker integration evolves.
**URL:** [https://www.bis.org/speeches/20210820-updates-fx-global-code](https://www.bis.org/speeches/20210820-updates-fx-global-code)

### S124. Uncovering FX settlement risk: new measures from the 2025 BIS Triennial Survey

**Evidence:** High
**Classification:** REFERENCE
**Action:** REFERENCE
**Stance:** Neutral
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** Settlement risk is important institutionally but only indirectly relevant to retail broker execution.
**Maysani Quant implication:** Keep for operational/counterparty awareness; not a signal feature.
**URL:** [https://www.bis.org/publications/qr-202606/uncovering-fx-settlement-risk-new-measures-2025-bis-triennial-survey](https://www.bis.org/publications/qr-202606/uncovering-fx-settlement-risk-new-measures-2025-bis-triennial-survey)

## B - Data Integrity

### S125. ALFRED Help - vintage economic data

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Neutral
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** ALFRED provides vintage-aware macro data.
**Maysani Quant implication:** Use vintage dates for backtests to prevent revised-data leakage.
**URL:** [https://alfred.stlouisfed.org/help](https://alfred.stlouisfed.org/help)

### S126. ALFRED Download Data Help

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Neutral
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** Explains downloading vintage macro series.
**Maysani Quant implication:** Implement reproducible vintage-data ingestion.
**URL:** [https://alfred.stlouisfed.org/help/downloaddata](https://alfred.stlouisfed.org/help/downloaddata)

### S127. ALFRED API documentation

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Neutral
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** API documentation enables programmatic vintage queries.
**Maysani Quant implication:** Build macro data connector against vintage endpoints.
**URL:** [https://fred.stlouisfed.org/docs/api/fred/alfred.html](https://fred.stlouisfed.org/docs/api/fred/alfred.html)

### S128. Data Revisions with FRED

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Challenging
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** Explains why economic series revisions can materially change historical values.
**Maysani Quant implication:** Never use latest revised values as if they were known historically.
**URL:** [https://www.stlouisfed.org/publications/page-one-economics/2022/08/01/data-revisions-with-fred](https://www.stlouisfed.org/publications/page-one-economics/2022/08/01/data-revisions-with-fred)

### S129. Real-Time Data Set for Macroeconomists

**Evidence:** High
**Classification:** CORE
**Action:** ADOPT
**Stance:** Neutral
**Review depth:** Official publication/guidance reviewed directly
**Assessment:** Real-time macro dataset provides another vintage-data source.
**Maysani Quant implication:** Use for replication/cross-check of point-in-time macro experiments.
**URL:** [https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/real-time-data-set-for-macroeconomists](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/real-time-data-set-for-macroeconomists)

# Appendix C. Claude Start-of-Work Checklist

- Read Sections 1-3 to understand objective and non-negotiables.

- Read Section 21 before writing V0.1 code; V0.1 scope overrides temptation to build later phases.

- Create/confirm CLAUDE.md that points to this master reference and repeats only the highest-risk invariants.

- Inspect current repository state and create an architecture decision record before changing authority boundaries.

- Implement domain models and tests before strategies.

- Build point-in-time data and accounting/risk invariants before optimizing signals.

- Keep every assumption configurable and record it in experiment output.

- Do not add an LLM dependency to V0.1.

- When uncertain whether a source supports a claim, mark it unverified and ask/research rather than inventing.

- At the end of each implementation batch, report files changed, tests run, failures, assumptions and next promotion gate.

Maysani Quant  •  Internal Technical Reference  •