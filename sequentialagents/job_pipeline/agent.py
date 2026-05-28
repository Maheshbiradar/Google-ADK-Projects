from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search
from google.genai.types import GenerateContentConfig
from .constants import (
    FAST_MODEL,
    SMART_MODEL,
    PIPELINE_TEMP,
    JOB_INPUT,
    RESEARCH_RESULTS,
    FIT_REPORT,
    COVER_LETTER,
)

# Agent 1: researches the company and role from the job input
research_agent = None

# Agent 2: evaluates candidate fit against the job requirements
fit_agent = None

# Agent 3: writes a tailored cover letter based on the fit report
cover_letter_agent = None

# Orchestrator: runs research_agent → fit_agent → cover_letter_agent in order
job_pipeline = None

