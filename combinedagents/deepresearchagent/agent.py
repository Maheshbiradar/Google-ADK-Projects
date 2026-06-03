from google.adk.agents import LlmAgent, ParallelAgent, LoopAgent, SequentialAgent
from google.adk.tools import google_search
from google.genai.types import GenerateContentConfig
from .constants import (
    FAST_MODEL,
    SMART_MODEL,
    PIPELINE_TEMP,
    TOPIC,
    NEWS_RESULTS,
    ACADEMIC_RESULTS,
    INDUSTRY_RESULTS,
    FINAL_REPORT,
    COVERAGE_PASSING_THRESHOLD,
    LOOP_MAX_ITERATIONS,
)

# ─────────────────────────────────────────────
# LEAF AGENTS  (run inside research_parallel)
# ─────────────────────────────────────────────

# Fetches recent news on the topic using google_search
news_agent = None

# Fetches academic / scholarly content on the topic using google_search
academic_agent = None

# Fetches industry reports and trends on the topic using google_search
industry_agent = None

# ─────────────────────────────────────────────
# EVALUATION & REPORTING AGENTS
# ─────────────────────────────────────────────

# Scores coverage across news / academic / industry results; no tools
# Outputs a coverage score: {"news": N, "academic": N, "industry": N, "overall": N}
evaluator_agent = None

# Synthesises all three result streams into a final written report; no tools
report_agent = None

# ─────────────────────────────────────────────
# COORDINATORS
# ─────────────────────────────────────────────

# ParallelAgent — runs news_agent, academic_agent, industry_agent concurrently
research_parallel = None

# LoopAgent — repeats research_parallel + evaluator_agent until coverage passes
#             or max_iterations (LOOP_MAX_ITERATIONS) is reached
research_loop = None

# SequentialAgent — top-level pipeline: research_loop → report_agent
deep_research_pipeline = None
