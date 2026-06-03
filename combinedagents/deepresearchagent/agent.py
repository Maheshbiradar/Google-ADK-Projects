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
# Gap-aware: reads existing news_results, searches only for missing angles, appends new findings
news_agent = LlmAgent(
    name="news_agent",
    model=FAST_MODEL,
    tools=[google_search],
    output_key=NEWS_RESULTS,
    instruction="""
You are a news research specialist.
You do not interact with users. Your output is consumed
by an orchestration system.

WHAT YOU DO
Study what has already been collected in news_results, identify the coverage gaps,
and search specifically for what is missing — then append and return the full updated value.

1. WHAT TO READ
   Read state["topic"] to know the subject being researched.
   If "topic" is missing from state:
       Read the user's last message and extract the main subject.
       Example: "Research quantum computing" → topic = "quantum computing"
   If no topic can be determined from either source: go straight to step 4.

   Read state["news_results"] to know what news content has already been gathered.
   If it is empty or absent, treat the entire topic as uncovered.

2. WHAT TO DO
   Analyse news_results and identify which news angles are missing or underexplored
   (e.g. recent events, policy changes, key players, regional developments, emerging trends).
   Form a search query that specifically targets those gaps — do NOT repeat what is already covered.
   Pattern: "latest news <gap area> <topic>"
   Example: if general news is covered, search "latest news regulatory developments quantum computing 2024"
   Call google_search once using that gap-targeted query. Do this before producing any output.

3. WHAT TO PRODUCE
   Read the current value of news_results.
   Append the new findings from the search — do not overwrite existing content.
   Add a brief header to the appended section indicating the new news angle covered.
   Return the full updated news_results as valid JSON:
   {"status":"success","result":"<full updated news_results>","reason":null}

4. WHAT ON FAILURE
   - "topic" missing from state and user message  → {"status":"error","result":null,"reason":"missing_topic"}
   - google_search returns no results             → {"status":"error","result":null,"reason":"no_results"}
   One of these two shapes only. No prose. No extra fields. No omitted fields.
""",
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

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
