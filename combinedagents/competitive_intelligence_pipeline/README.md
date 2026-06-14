# Competitive Intelligence Pipeline

A multi-agent pipeline built on Google ADK that takes a company name and produces a structured competitive intelligence report researched across three dimensions.

---

## What it does

1. Extracts the company name from the user's message
2. Researches the company in parallel across three angles — news, financials, and competitors
3. Evaluates research coverage iteratively and loops until quality passes the threshold
4. Compiles all findings into a structured markdown intelligence report

---

## Architecture

```
competitive_intelligence_pipeline  ← SequentialAgent
│
├── company_extractor_agent        ← extracts company name from user input
│
├── research_loop                  ← LoopAgent (max 3 iterations)
│   ├── research_parallel          ← ParallelAgent
│   │   ├── news_agent             ← news and recent developments
│   │   ├── financial_agent        ← financial and market position
│   │   └── competitor_agent       ← competitor landscape
│   └── evaluator_agent            ← scores coverage, escalates when ready
│
└── report_agent                   ← synthesizes final markdown report
```

---

## Agents

| Agent                     | Model | Role                                                                  |
| ------------------------- | ----- | --------------------------------------------------------------------- |
| `company_extractor_agent` | FAST  | Extracts company name from user message                               |
| `news_agent`              | FAST  | Researches news and recent developments                               |
| `financial_agent`         | FAST  | Researches financial and market position                              |
| `competitor_agent`        | FAST  | Researches competitor landscape                                       |
| `evaluator_agent`         | SMART | Scores coverage across three dimensions, escalates on pass or failure |
| `report_agent`            | SMART | Synthesizes all research into a structured intelligence report        |

---

## State flow

```
Input:   state["company_name"]
         state["news_and_recent_developments_results"]
         state["financial_market_analysis_results"]
         state["competitor_landscape_results"]
         state["coverage_score"]
Output:  state["final_report"]
```

Each research agent appends findings to its accumulator on every iteration. The evaluator scores each dimension (0–10) and escalates when all scores reach **8.0** or above.

---

## Project structure

```
competitive_intelligence_pipeline/
├── agent.py                    # Pipeline assembly — coordinators and root_agent
├── company_extractor_agent.py
├── news_agent.py
├── financial_agent.py
├── competitor_agent.py
├── evaluator_agent.py
├── report_agent.py
├── constants.py                # Models, state keys, thresholds
└── .env                        # API keys (not committed)
```

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install google-adk
```

Add your API key to `.env`:

```
GOOGLE_API_KEY=your_key_here
```

---

## Run

```bash
adk web
```

Then send a message such as:

> Analyze NTT Data
