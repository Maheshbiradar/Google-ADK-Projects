# Google ADK — 30-Day Learning Guide

> A structured, project-based journey from zero to production-ready AI agent developer using **Google Agent Development Kit (ADK)**.

---

## What is Google ADK?

Google Agent Development Kit (ADK) is an open-source, code-first Python framework for building, evaluating, and deploying sophisticated AI agents. It is the same framework powering agents inside Google products like Agentspace and Google Customer Engagement Suite. ADK supports multi-agent architectures, rich tool ecosystems, session management, streaming, and one-command deployment to Google Cloud.

---

## Repository Structure

```
adk-learning/
├── week_1/                  # Foundations & Core Concepts
│   ├── hello_agent/         # Day 1
│   ├── weather_bot/         # Day 3
│   ├── calculator_agent/    # Day 4
│   ├── research_agent/      # Day 5
│   ├── shopping_agent/      # Day 6
│   └── personal_assistant/  # Day 7 — Week 1 Milestone
│
├── week_2/                  # Multi-Agent Systems & Workflow Agents
│   ├── content_pipeline/    # Day 8
│   ├── market_research/     # Day 9
│   ├── code_reviewer/       # Day 10
│   ├── travel_planner/      # Day 11
│   ├── callback_agent/      # Day 12
│   ├── crm_agent/           # Day 13
│   └── ecommerce_support/   # Day 14 — Week 2 Milestone
│
├── week_3/                  # Advanced Integrations & Production Patterns
│   ├── github_agent/        # Day 15
│   ├── filesystem_agent/    # Day 16
│   ├── document_agent/      # Day 17
│   ├── eval_framework/      # Day 18
│   ├── live_chat_agent/     # Day 19
│   ├── sql_agent/           # Day 20
│   └── code_review_platform/# Day 21 — Week 3 Milestone
│
├── week_4/                  # Deployment, Scale & Capstone
│   ├── cloud_run_deploy/    # Day 22
│   ├── vertex_ai_deploy/    # Day 23
│   ├── observability/       # Day 24
│   ├── security_patterns/   # Day 25
│   ├── a2a_agents/          # Day 26
│   ├── performance/         # Day 27
│   └── hr_platform/         # Day 28-30 — Capstone
│
└── config.py                # Centralized model config (gemini-flash-latest etc.)
```

---

## Prerequisites

- Python 3.9+
- Google AI Studio API key → [aistudio.google.com](https://aistudio.google.com)
- `pip install google-adk`

```bash
# Quick start
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install google-adk requests
```

---

## Model Configuration

All agents in this repo use the centralized `config.py` at the root:

```python
# config.py
FAST_MODEL   = "gemini-flash-latest"   # Most agents — speed + cost balanced
SMART_MODEL  = "gemini-pro-latest"     # Complex reasoning agents
CHEAP_MODEL  = "gemini-3.1-flash-lite" # High-volume, cost-sensitive agents
```

> **Note:** `gemini-2.0-flash` is deprecated as of June 2026. Always use `gemini-flash-latest` or a pinned stable string like `gemini-2.5-flash` for production.

---

## Key ADK Rules Learned in This Guide

| Rule                                                               | Why It Matters                                                     |
| ------------------------------------------------------------------ | ------------------------------------------------------------------ |
| `BuiltInCodeExecutor` cannot share an agent with custom `tools=[]` | Gemini API hard constraint — split into specialist agents          |
| `google_search` cannot share an agent with custom function tools   | Same constraint — use `AgentTool` pattern to compose               |
| Never use `{placeholders}` in instructions                         | ADK interprets curly braces as template variables                  |
| Always return `dict` from tools                                    | Enables structured error handling and LLM reasoning                |
| Docstring = tool API contract                                      | LLM reads docstring to decide when/how to call the tool            |
| Use `gemini-flash-latest` not `gemini-2.0-flash`                   | Old model string format is deprecated                              |
| State prefixes matter from day one                                 | `app:`, `user:`, `temp:` route to different backends in production |

---

---

# WEEK 1 — Foundations & Core Concepts

**Goal:** Understand ADK's building blocks. Build real agents with tools, sessions, and state from scratch.

**Skills gained:** Agent creation, custom tools, built-in tools, session state, ToolContext, model selection, instruction engineering.

---

### Day 1 — Environment Setup & Hello Agent

**Project:** `hello_agent`

**What it solves:**
Gets the complete ADK development environment running from zero. Installs ADK, wires up a Gemini API key, and produces a running agent that responds to messages and calls a custom Python tool. Establishes the `adk web` development workflow and the Events panel debugging approach used throughout all 30 days.

**Key concepts:** `root_agent`, virtual environments, `.env` setup, `adk run`, `adk web`, Events panel, basic tool anatomy.

---

### Day 2 — ADK Architecture Deep Dive

**Project:** Architecture diagrams and mental models (no standalone project)

**What it solves:**
Builds the mental model needed to understand every other day. Explains how `Agent`, `Tool`, `Session`, `State`, `Event`, and `Runner` connect together. Covers the agent loop (LLM decides → ADK executes → LLM reads result → decides again) and why understanding this loop is the key to debugging any ADK agent fast.

**Key concepts:** Runner, SessionService, Event pipeline, agent loop, ReAct pattern, tool execution flow.

---

### Day 3 — LLM Agents: Instructions, Models & Weather Bot

**Project:** `weather_bot`

**What it solves:**
Solves the challenge of connecting an ADK agent to a real external API (OpenWeatherMap) and returning live data to users. Demonstrates how instruction quality directly controls agent reliability — showing that vague instructions produce unpredictable behavior while specific, rule-based instructions produce production-quality responses.

**Tools:** `get_weather`, `compare_weather`, `get_weather_advice`

**Key concepts:** `instruction` engineering, `description` field, model selection (`gemini-flash-latest`), output format in instructions, boundary setting, error handling pattern `{"status": "error", "message": "..."}`.

---

### Day 4 — Custom Tools: Python Functions as Agent Superpowers

**Project:** `calculator_agent`

**What it solves:**
Solves the problem of giving agents precise, deterministic computation capabilities that LLMs cannot reliably do alone. Demonstrates how ADK converts Python functions into LLM-readable schemas, why docstrings are the tool's API contract, and how `ToolContext` enables tools to share state — building a calculator that tracks full calculation history across a conversation.

**Tools:** `calculate`, `calculate_percentage`, `solve_statistics`, `convert_units`, `get_calculation_history`

**Key concepts:** How ADK builds JSON schema from function signatures, type hints, docstring conventions, `ToolContext`, session state in tools, error handling taxonomy (validation / business logic / external / unexpected).

---

### Day 5 — Built-in Tools, Tool Composition & Research Agent

**Project:** `research_agent`

**What it solves:**
Solves the problem of agents being limited to training-time knowledge. Connects agents to live web search via `google_search` and sandboxed Python execution via `BuiltInCodeExecutor`. Critically demonstrates the **specialist agent pattern** — the correct ADK architecture when combining built-in tools with custom tools (required because Gemini API prohibits mixing them in one agent).

**Tools:** `google_search` (built-in), `BuiltInCodeExecutor` (built-in), `save_research_note`, `get_research_notes`, `create_research_outline`

**Architecture pattern:** `AgentTool` — wrapping specialist agents (`search_agent`, `code_agent`) as tools for the root orchestrator.

**Key concepts:** Built-in tools vs custom tools, tool execution pipeline, `AgentTool` pattern, `generate_content_config`, temperature tuning, the Gemini API constraint (built-ins + function calling cannot mix).

---

### Day 6 — Session Management, State & Shopping Cart Agent

**Project:** `shopping_agent`

**What it solves:**
Solves the fundamental challenge of conversational memory — how an agent remembers what a user said and did across multiple messages. Builds a full e-commerce shopping cart that persists items, quantities, discounts, and order totals across an entire conversation using ADK's session state system. Demonstrates why `InMemorySessionService` is for development only and how to design state for production from day one.

**Tools:** `browse_products`, `add_to_cart`, `remove_from_cart`, `view_cart`, `apply_discount`, `generate_checkout_summary`

**Key concepts:** Session lifecycle, state scopes (`app:`, `user:`, `session:`, `temp:`), `SessionService` implementations, Runner internals, conversation history vs state (two separate things), state design principles (lean, serializable, single source of truth).

---

### Day 7 — Week 1 Milestone: Personal Assistant Agent ⭐

**Project:** `personal_assistant`

**What it solves:**
Consolidates all Week 1 concepts into one cohesive, production-quality agent. A personal assistant that combines live web search, calculations, session memory, stateful note-taking, and multi-tool orchestration. Tests the ability to compose all learned patterns into a single well-architected agent — including the specialist agent pattern for built-in tools, proper state scoping, and production-grade instruction writing.

**Key concepts:** Full Week 1 synthesis — multi-tool orchestration, `AgentTool` composition, state persistence, instruction architecture, model configuration.

---

---

# WEEK 2 — Multi-Agent Systems & Workflow Agents

**Goal:** Master ADK's three workflow agent types and multi-agent hierarchies. Build systems where specialized agents collaborate, delegate, and coordinate automatically.

**Skills gained:** SequentialAgent, ParallelAgent, LoopAgent, multi-agent delegation, Callbacks, MemoryService, AgentTool pattern at scale.

---

### Day 8 — SequentialAgent: Deterministic Pipelines

**Project:** `content_pipeline`

**What it solves:**
Solves tasks that must happen in a fixed order where each step depends on the previous step's output. A content processing pipeline that fetches raw content → summarizes it → formats it → saves it. Demonstrates when deterministic sequential flow is the right choice over LLM-based routing, and how to pass data between pipeline stages via shared state.

**Key concepts:** `SequentialAgent`, pipeline design, step dependencies, data passing via state, when deterministic beats dynamic.

---

### Day 9 — ParallelAgent: Concurrent Execution

**Project:** `market_research`

**What it solves:**
Solves research tasks that require gathering information from multiple independent sources simultaneously. Instead of searching topics one by one (slow), searches multiple angles in parallel and aggregates results. A market research agent that fans out to multiple specialist search agents simultaneously and synthesizes a comprehensive report.

**Key concepts:** `ParallelAgent`, fan-out/fan-in patterns, concurrent tool execution, result aggregation, when parallel beats sequential (independent tasks with no dependencies).

---

### Day 10 — LoopAgent: Iterative Refinement

**Project:** `code_reviewer`

**What it solves:**
Solves tasks that require repeated attempts until a quality threshold is met — the "do it until it's good enough" problem. A code review agent that iteratively analyzes code, suggests improvements, applies them, re-evaluates, and loops until the code meets quality standards or a maximum iteration count is reached.

**Key concepts:** `LoopAgent`, exit conditions, iteration counters in state, quality thresholds, preventing infinite loops, when to loop vs when to stop.

---

### Day 11 — Multi-Agent Hierarchies & Delegation

**Project:** `travel_planner`

**What it solves:**
Solves complex multi-domain tasks that require specialized expertise in each domain. A travel planning system where a root coordinator agent delegates to a `FlightAgent`, `HotelAgent`, and `SightseeingAgent` — each expert in their domain — and synthesizes a complete itinerary. Demonstrates how `AgentTool` enables clean agent-to-agent delegation.

**Key concepts:** Agent hierarchies, `AgentTool` at scale, delegation patterns, coordinator design, sub-agent description writing, how sub-agents share context.

---

### Day 12 — Callbacks: Hooks, Guardrails & Observability

**Project:** `callback_agent`

**What it solves:**
Solves the problem of controlling, monitoring, and modifying agent behavior without changing core agent logic. Demonstrates how callbacks intercept the agent loop at key points — before/after agent runs, before/after tool calls — to add logging, safety guardrails, cost tracking, input validation, and output modification. Essential for production agents.

**Key concepts:** `before_agent_callback`, `after_agent_callback`, `before_tool_callback`, `after_tool_callback`, guardrail patterns, logging strategy, modifying tool responses, cost tracking via callbacks.

---

### Day 13 — Memory Service: Cross-Session Recall

**Project:** `crm_agent`

**What it solves:**
Solves the limitation of session state — it disappears when the conversation ends. A personal CRM agent that remembers clients, preferences, interaction history, and action items **across completely separate sessions**. When a user returns days later, the agent recalls previous context. Demonstrates the difference between short-term state (this conversation) and long-term memory (across all conversations).

**Key concepts:** `MemoryService` vs `SessionState`, `InMemoryMemoryService`, semantic search over memories, memory ingestion, recall patterns, `user:` prefixed state for cross-session persistence.

---

### Day 14 — Week 2 Milestone: E-commerce Support System ⭐

**Project:** `ecommerce_support`

**What it solves:**
Consolidates all Week 2 concepts into an enterprise-grade customer support system. Parallel agents handle order lookup and FAQ simultaneously. A loop agent iteratively escalates unresolved issues. Memory keeps customer history across sessions. Callbacks enforce response quality guardrails and log every interaction for audit. Demonstrates a realistic production multi-agent architecture.

**Key concepts:** Full Week 2 synthesis — parallel processing, loop escalation, cross-session memory, callback-based quality control, multi-agent orchestration at scale.

---

---

# WEEK 3 — Advanced Integrations & Production Patterns

**Goal:** Connect agents to the real world through OpenAPI specs, MCP servers, artifact management, streaming, and custom agent classes.

**Skills gained:** OpenAPI tools, MCP integration, artifact management, evaluation framework, streaming, BaseAgent extension, custom control flow.

---

### Day 15 — OpenAPI Tools: Auto-generate from REST APIs

**Project:** `github_agent`

**What it solves:**
Solves the massive time cost of manually writing tool functions for every REST API endpoint. Instead, ADK can read an OpenAPI spec and automatically generate all tools. A GitHub agent built entirely from the GitHub REST API OpenAPI spec — able to list repos, create issues, check PRs, and more — with zero manually written tool functions.

**Key concepts:** `OpenAPIToolset`, OpenAPI spec parsing, auto-generated tool schemas, authentication headers, when OpenAPI beats manual tools, spec sourcing strategies.

---

### Day 16 — MCP Tools: Model Context Protocol

**Project:** `filesystem_agent`

**What it solves:**
Solves the problem of connecting agents to the growing ecosystem of MCP-compatible servers — a standardized protocol for exposing tools to AI models. A filesystem agent that connects to an MCP filesystem server, enabling the agent to read, write, list, and manage files using the MCP standard. Demonstrates ADK's interoperability beyond the Google ecosystem.

**Key concepts:** `MCPToolset`, MCP server connection, tool discovery from MCP, stdio vs SSE transports, MCP vs custom tools tradeoffs, the growing MCP ecosystem.

---

### Day 17 — Artifact Management: Files & Binary Data

**Project:** `document_agent`

**What it solves:**
Solves the challenge of agents working with files and binary data across a session — PDFs, images, generated reports. An agent that accepts uploaded documents, processes them (extracts text, generates summaries), produces output files, and makes them available for download — all tracked with versioning through ADK's artifact system.

**Key concepts:** `ArtifactService`, `InMemoryArtifactService`, save/load artifacts, artifact versioning, handling binary data in agents, `tool_context.load_artifact()`, `tool_context.save_artifact()`.

---

### Day 18 — Evaluation Framework: Testing Agent Quality

**Project:** `eval_framework`

**What it solves:**
Solves the "how do I know my agent is actually working correctly?" problem. ADK's built-in evaluation framework lets you define test cases with expected behaviors, run them against your agent, and score the results automatically. Demonstrates how to build regression test suites that catch quality regressions before they reach production.

**Key concepts:** ADK eval framework, `EvalSet`, `EvalCase`, trajectory evaluation, response quality scoring, automated regression testing, CI integration patterns.

---

### Day 19 — Streaming: Real-time Agent Responses

**Project:** `live_chat_agent`

**What it solves:**
Solves the poor user experience of waiting for a complete agent response before seeing anything. Streaming delivers tokens to the user as they are generated — making agents feel instant and responsive. A live customer chat agent that streams responses token-by-token, with a FastAPI backend demonstrating how to wire ADK streaming into a real web application.

**Key concepts:** `runner.run_async()` event streaming, Server-Sent Events (SSE), bidirectional streaming, `is_final_response()`, streaming architecture in FastAPI, when streaming matters most.

---

### Day 20 — Custom Agents: Extending BaseAgent

**Project:** `sql_agent`

**What it solves:**
Solves cases where LLM-based routing and standard workflow agents are too flexible or too rigid. A SQL query agent built by extending `BaseAgent` directly — implementing `_run_async_impl` with custom control flow that validates queries, checks permissions, executes against a database, and returns typed results with a guaranteed structure the LLM never deviates from.

**Key concepts:** `BaseAgent`, `_run_async_impl`, custom control flow, when to extend BaseAgent vs use LlmAgent, deterministic vs dynamic behavior tradeoffs, yielding Events manually.

---

### Day 21 — Week 3 Milestone: AI Code Review Platform ⭐

**Project:** `code_review_platform`

**What it solves:**
Consolidates all Week 3 concepts into a real engineering tool. A code review platform that fetches PRs from GitHub via OpenAPI tools, reads files via MCP filesystem tools, runs analysis code via code execution, stores review reports as artifacts with versioning, streams review feedback in real time, and maintains a review history via memory service. A genuine tool an engineering team could use.

**Key concepts:** Full Week 3 synthesis — OpenAPI + MCP + artifacts + streaming + evaluation + custom agents working together.

---

---

# WEEK 4 — Deployment, Scale & Capstone

**Goal:** Take agents from local development to production. Deploy, monitor, secure, and optimize real agents on Google Cloud infrastructure.

**Skills gained:** Cloud Run deployment, Vertex AI Agent Engine, Cloud Trace observability, IAM security, A2A protocol, performance optimization.

---

### Day 22 — Deployment: Cloud Run

**Project:** `cloud_run_deploy`

**What it solves:**
Solves the gap between a working local agent and a publicly accessible, scalable service. Packages an ADK agent into a Docker container, exposes it via ADK's built-in FastAPI server, and deploys it to Google Cloud Run with proper environment variable management, health checks, and auto-scaling. After this day, your agent has a real HTTPS endpoint.

**Key concepts:** `adk deploy cloud_run`, Dockerfile for ADK, FastAPI server mode, environment variables via Secret Manager, Cloud Run scaling config, HTTPS endpoint, CORS configuration.

---

### Day 23 — Vertex AI Agent Engine: Managed Scale

**Project:** `vertex_ai_deploy`

**What it solves:**
Solves the operational burden of managing your own infrastructure. Vertex AI Agent Engine is Google's fully managed runtime for ADK agents — handles sessions, scaling, monitoring, and IAM automatically. A single `adk deploy agent_engine` command replaces your entire server management concern. Demonstrates the `VertexAiSessionService` that provides production-grade persistent sessions.

**Key concepts:** `adk deploy agent_engine`, `VertexAiSessionService`, managed session storage, Agent Engine scaling, regional deployment, switching from `InMemorySessionService` to Vertex AI in one line.

---

### Day 24 — Observability: Tracing, Logging & Metrics

**Project:** `observability`

**What it solves:**
Solves the "what is my agent actually doing in production?" problem. Integrates ADK with Google Cloud Trace for distributed tracing of agent calls, Cloud Logging for structured log analysis, and Cloud Monitoring for dashboards and alerts. After this day you can answer: which tool calls are slow, which users get errors, and how much each conversation costs.

**Key concepts:** Cloud Trace integration, OpenTelemetry in ADK, structured logging patterns, custom metrics (latency, tool call counts, token usage), alerting on agent errors, debugging production issues with traces.

---

### Day 25 — Security: Auth, IAM & Human-in-the-Loop

**Project:** `security_patterns`

**What it solves:**
Solves the problem of agents taking irreversible actions without human oversight. Demonstrates three security layers: IAM-based agent identity (what the agent is allowed to do in GCP), tool confirmation patterns (HITL — pausing for human approval before high-stakes actions), and OAuth for tool calls that need user-level permissions. Essential for any production agent handling real data or money.

**Key concepts:** Agent service accounts, IAM least-privilege, Human-in-the-Loop (HITL) callbacks, tool confirmation flow, OAuth 2.0 for tool auth, Secret Manager for credentials, audit logging.

---

### Day 26 — A2A Protocol: Agent-to-Agent Communication

**Project:** `a2a_agents`

**What it solves:**
Solves the problem of agents in different services or organizations needing to communicate. The A2A (Agent-to-Agent) protocol is Google's open standard for inter-agent communication over HTTP. Builds a microservice agent mesh where agents deployed independently can discover and call each other — the foundation of enterprise agent ecosystems.

**Key concepts:** A2A protocol, `RemoteA2aAgent`, agent discovery, agent cards, cross-service agent calls, A2A vs AgentTool (local vs remote), building agent microservices.

---

### Day 27 — Performance Optimization

**Project:** `performance`

**What it solves:**
Solves the real production pain points of cost, latency, and reliability at scale. Covers context window management (preventing conversation history from growing unboundedly), token budget strategies (controlling cost per conversation), response caching for repeated queries, lazy tool loading, and latency profiling to find bottlenecks. The difference between an agent that works and one that's economically viable at scale.

**Key concepts:** Context window limits and truncation strategies, token counting, response caching, `generate_content_config` tuning for cost, parallel tool calls for latency, profiling with Cloud Trace.

---

### Day 28–30 — Capstone: Enterprise HR Automation Platform ⭐⭐

**Project:** `hr_platform`

**What it solves:**
The ultimate synthesis project. An enterprise HR automation platform that demonstrates every concept from all 30 days working together in a real-world system. Employees interact with an HR assistant that handles onboarding workflows, policy Q&A, leave management, payroll inquiries, and performance review scheduling — all through a deployed, monitored, secured, multi-agent system.

**Architecture:**

- **Root orchestrator** — routes employee requests to specialist agents
- **Policy agent** — searches HR policy documents via RAG
- **Onboarding agent** — SequentialAgent running multi-step onboarding pipeline
- **Leave agent** — manages leave requests with HITL approval for edge cases
- **Analytics agent** — ParallelAgent gathering HR metrics, generates reports via code execution
- **Memory layer** — remembers employee context across all conversations
- **Deployment** — Vertex AI Agent Engine with Cloud Run frontend
- **Observability** — full Cloud Trace + Cloud Logging + Monitoring dashboards
- **Security** — IAM service accounts, HITL for sensitive actions, audit trail

**Key concepts:** Full 30-day synthesis — every pattern applied in a cohesive enterprise architecture.

---

---

## Running Any Agent

```bash
# From the adk-learning root folder
cd adk-learning

# Activate virtual environment
source .venv/bin/activate

# Run any agent in the browser UI
adk web

# Or run a specific agent in the terminal
adk run week_1/hello_agent
adk run week_1/weather_bot
adk run week_2/travel_planner
# etc.
```

---

## Environment Variables

Each agent folder contains a `.env` file. Never commit these to GitHub.

```bash
# Standard .env for all agents
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE

# For Week 3+ agents (optional extras)
OPENWEATHER_API_KEY=your_openweather_key
GITHUB_TOKEN=your_github_token

# For Week 4 deployment
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
GOOGLE_CLOUD_LOCATION=us-central1
```

Add a `.gitignore` at the root:

```
**/.env
**/__pycache__/
**/.venv/
*.pyc
.DS_Store
```

---

## Learning Milestones

| Milestone        | Day    | What You Can Build                                                    |
| ---------------- | ------ | --------------------------------------------------------------------- |
| ⭐ Milestone 1   | Day 7  | Single agents with tools, state, and session memory                   |
| ⭐ Milestone 2   | Day 14 | Multi-agent systems with parallel, sequential, and loop orchestration |
| ⭐ Milestone 3   | Day 21 | Production-pattern agents with OpenAPI, MCP, artifacts, and streaming |
| ⭐⭐ Milestone 4 | Day 30 | Full enterprise platforms deployed on Google Cloud                    |

---

## Key Resources

- [ADK Official Docs](https://google.github.io/adk-docs/)
- [ADK Python GitHub](https://github.com/google/adk-python)
- [Google AI Studio (API Keys)](https://aistudio.google.com/app/apikey)
- [Gemini Models Reference](https://ai.google.dev/gemini-api/docs/models)
- [ADK Tool Limitations](https://google.github.io/adk-docs/tools/limitations/)
- [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/docs/agent-engine)

---

## License

This learning guide and all code is for educational purposes.
ADK is licensed under Apache 2.0 — see [google/adk-python](https://github.com/google/adk-python).
