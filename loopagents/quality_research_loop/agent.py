from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools import google_search
from google.genai.types import GenerateContentConfig
from .constants import (
    FAST_MODEL,
    SMART_MODEL,
    PIPELINE_TEMP,
    TOPIC,
    ACCUMULATED_RESEARCH,
    COVERAGE_SCORE,
    FINAL_REPORT,
)

# ─────────────────────────────────────────────
# AGENT DEFINITIONS
# ─────────────────────────────────────────────

# Agent 1: searches the web and accumulates research on the topic
research_agent = None

# Agent 2: evaluates how thoroughly the topic has been covered (0–100 score)
evaluator_agent = None

# Agent 3: compiles the accumulated research into a polished final report
report_agent = None

# ─────────────────────────────────────────────
# LOOP AGENT
# ─────────────────────────────────────────────

# LoopAgent — runs research_agent → evaluator_agent repeatedly
research_loop = None

# SequentialAgent — runs research_loop then report_agent once
quality_research_loop = None
