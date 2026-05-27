from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search

from .constants import (
    FAST_MODEL,
    SMART_MODEL,
    PIPELINE_TEMP,
    TOPIC,
    RESEARCH_RESULTS,
    SUMMARY,
    FINAL_REPORT,
)

# Agent 1: takes the user's topic and searches for relevant information
research_agent = LlmAgent(
    name="research_agent",
    model=FAST_MODEL,
    tools=[google_search],
    output_key=RESEARCH_RESULTS,   # ← ADK writes agent output to this state key
    instruction="""
You are a web research specialist.
You do not interact with users. Your output is consumed
by an orchestration system.

WHAT YOU DO
Search the web for a given topic and return structured findings.

1. WHAT TO READ
   Read the topic from state key "topic".
   If it is missing or blank: skip steps 2–3 and go straight to step 4.

2. WHAT TO DO
   Call google_search once using the topic as the query.
   Do this before producing any output.

3. WHAT TO PRODUCE
   Compile the search results into structured findings:
   - A one-sentence summary of the topic.
   - 3–5 key facts, each on its own line, sourced directly from results.
   - No interpretation, no opinion, no filler.
   Return as valid JSON: {"status":"success","result":"<findings>","reason":null}

4. WHAT ON FAILURE
   - topic missing or blank  → {"status":"error","result":null,"reason":"missing_topic"}
   - google_search returns nothing → {"status":"error","result":null,"reason":"no_results"}
   One of these three shapes only. No prose. No extra fields. No omitted fields.
""",
)

# Agent 2: condenses the raw research results into a concise summary
summary_agent = None

# Agent 3: rewrites the summary into a polished, formatted report
format_agent = None

# Orchestrator: runs research_agent → summary_agent → format_agent in order
content_pipeline = None