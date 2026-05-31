from google.adk.agents import LlmAgent, ParallelAgent
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
)

# Agent 1: fetches recent news on the topic
news_agent = LlmAgent(
    name="news_agent",
    model=FAST_MODEL,
    tools=[google_search],
    output_key=NEWS_RESULTS,
    instruction=None,
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# Agent 2: fetches academic / research papers on the topic
academic_agent = LlmAgent(
    name="academic_agent",
    model=FAST_MODEL,
    tools=[google_search],
    output_key=ACADEMIC_RESULTS,
    instruction=None,
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# Agent 3: fetches industry reports and market data on the topic
industry_agent = LlmAgent(
    name="industry_agent",
    model=FAST_MODEL,
    tools=[google_search],
    output_key=INDUSTRY_RESULTS,
    instruction=None,
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# Agent 4: synthesises all three sources into a structured final report
format_agent = LlmAgent(
    name="format_agent",
    model=SMART_MODEL,
    output_key=FINAL_REPORT,
    instruction=None,
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# Orchestrator: runs news_agent, academic_agent, industry_agent in parallel,
# then format_agent synthesises the combined results
multi_source_pipeline = None
