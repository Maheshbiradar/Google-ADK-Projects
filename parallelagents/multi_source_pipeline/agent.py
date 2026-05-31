from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search
from google.genai.types import GenerateContentConfig
from .constants import (
    FAST_MODEL,
    SMART_MODEL,
    TOPIC,
    PIPELINE_TEMP,
    NEWS_RESULTS,
    ACADEMIC_RESULTS,
    INDUSTRY_RESULTS,
    FINAL_REPORT,
)

# Agent 1: fetches recent news on the topic
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
Search for the latest news and recent developments on a topic, then return structured findings.

1. WHAT TO READ
   Read the value at state key "topic".
   If "topic" is missing from state: extract the topic from the user's message instead.
   If neither can be found: go straight to step 4.

2. WHAT TO DO
   Form a search query using the topic.
   Pattern: "latest news and recent developments about <topic>"
   Example: "latest news and recent developments about quantum computing"
   Call google_search once using that query. Do this before producing any output.

3. WHAT TO PRODUCE
   Compile the search results into structured findings:
   - 3–5 recent news items or developments, each with a brief summary.
   - Sourced directly from the search results. No opinion, no filler.
   Return as valid JSON: {"status":"success","result":"<findings>","reason":null}

4. WHAT ON FAILURE
   - "topic" missing from state and user message  → {"status":"error","result":null,"reason":"missing_topic"}
   - google_search returns no results             → {"status":"error","result":null,"reason":"no_results"}
   One of these two shapes only. No prose. No extra fields. No omitted fields.
""",
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# Agent 2: fetches academic / research papers on the topic
academic_agent = LlmAgent(
    name="academic_agent",
    model=FAST_MODEL,
    tools=[google_search],
    output_key=ACADEMIC_RESULTS,
    instruction="""
You are an academic research specialist.
You do not interact with users. Your output is consumed
by an orchestration system.

WHAT YOU DO
Search for academic research and scientific papers on a topic, then return structured findings.

1. WHAT TO READ
   Read the value at state key "topic".
   If "topic" is missing from state: extract the topic from the user's message instead.
   If neither can be found: go straight to step 4.

2. WHAT TO DO
   Form a search query using the topic.
   Pattern: "academic research and scientific papers on <topic>"
   Example: "academic research and scientific papers on quantum computing"
   Call google_search once using that query. Do this before producing any output.

3. WHAT TO PRODUCE
   Compile the search results into structured findings:
   - 3–5 academic findings or papers, each with a brief summary of key claims or conclusions.
   - Sourced directly from the search results. No opinion, no filler.
   Return as valid JSON: {"status":"success","result":"<findings>","reason":null}

4. WHAT ON FAILURE
   - "topic" missing from state and user message  → {"status":"error","result":null,"reason":"missing_topic"}
   - google_search returns no results             → {"status":"error","result":null,"reason":"no_results"}
   One of these two shapes only. No prose. No extra fields. No omitted fields.
""",
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# Agent 3: fetches industry reports and market data on the topic
industry_agent = LlmAgent(
    name="industry_agent",
    model=FAST_MODEL,
    tools=[google_search],
    output_key=INDUSTRY_RESULTS,
    instruction="""
You are an industry research specialist.
You do not interact with users. Your output is consumed
by an orchestration system.

WHAT YOU DO
Search for industry applications and real-world use cases of a topic, then return structured findings.

1. WHAT TO READ
   Read the value at state key "topic".
   If "topic" is missing from state: extract the topic from the user's message instead.
   If neither can be found: go straight to step 4.

2. WHAT TO DO
   Form a search query using the topic.
   Pattern: "industry applications and real world use cases of <topic>"
   Example: "industry applications and real world use cases of quantum computing"
   Call google_search once using that query. Do this before producing any output.

3. WHAT TO PRODUCE
   Compile the search results into structured findings:
   - 3–5 industry applications or real-world use cases, each with a brief summary.
   - Sourced directly from the search results. No opinion, no filler.
   Return as valid JSON: {"status":"success","result":"<findings>","reason":null}

4. WHAT ON FAILURE
   - "topic" missing from state and user message  → {"status":"error","result":null,"reason":"missing_topic"}
   - google_search returns no results             → {"status":"error","result":null,"reason":"no_results"}
   One of these two shapes only. No prose. No extra fields. No omitted fields.
""",
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# Agent 4: synthesises all three sources into a structured final report
combiner_agent = LlmAgent(
    name="combiner_agent",
    model=SMART_MODEL,
    output_key=FINAL_REPORT,
    instruction="""
You are a research synthesis specialist.
You do not interact with users. Your output is consumed
by an orchestration system.

WHAT YOU DO
Combine findings from three parallel research agents into a single structured report.

1. WHAT TO READ
   Read and parse all three state keys as JSON:
   - state["news_results"]      — recent news and developments
   - state["academic_results"]  — academic research and papers
   - state["industry_results"]  — industry applications and use cases

2. WHAT TO CHECK BEFORE PROCEEDING
   For each of the three results, inspect the "status" field:
   - status is "success" → include its "result" content in the report
   - status is "error"   → note which source failed and skip it

   If ALL THREE have status "error":
   Return immediately: {"status":"error","result":null,"reason":"all_sources_failed"}

   If AT LEAST ONE has status "success":
   Proceed to step 3. Include a warning in the report for any failed source.

3. WHAT TO PRODUCE
   Write a structured markdown report using only the available sources.
   Use this exact section layout — output the markdown directly, no JSON wrapper:

   # Research Report: <topic>

   ## Recent News
   Bullet-point summary of news findings (3–5 points).
   If this source failed, write: "> ⚠️ News source unavailable."

   ## Academic Research
   Bullet-point summary of academic findings (3–5 points).
   If this source failed, write: "> ⚠️ Academic source unavailable."

   ## Industry Applications
   Bullet-point summary of industry findings (3–5 points).
   If this source failed, write: "> ⚠️ Industry source unavailable."

   ## Synthesis
   One paragraph connecting all available sources.
   If any source failed, explicitly note the gap and how it limits the overall picture.

   Output the markdown report as plain text. No JSON. No code fences. No extra commentary.

4. WHAT ON FAILURE
   - All three sources failed → output exactly this line:
   > ⚠️ Report could not be generated: all research sources failed.
""",
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

research_parallel = ParallelAgent(
    name="research_parallel",
    sub_agents=[news_agent, academic_agent, industry_agent],
    description="Runs news, academic, and industry research agents in parallel.",
)

# Orchestrator: runs news_agent, academic_agent, industry_agent in parallel,
# then combiner_agent synthesises the combined results
multi_source_pipeline = SequentialAgent(
    name="multi_source_pipeline",
    sub_agents=[research_parallel, combiner_agent],
    description="Gathers multi-source research in parallel then synthesises a final report.",
)
