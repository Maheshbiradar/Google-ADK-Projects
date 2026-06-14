from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig

from competitive_intelligence_pipeline.constants import (
    COMPANY_NAME,
    FAST_MODEL,
    PIPELINE_TEMP,
)

COMPANY_EXTRACTOR_INSTRUCTION = """
WHAT YOU DO
You are a company name extraction specialist.
You do not interact with users. Your output is consumed
by an orchestration system.

WHAT YOU DO
Extract the company name from the user's latest message so the research pipeline can run on the correct target company.

1. WHAT TO READ
Read only the user's latest message text from the conversation context.

2. EXTRACTION PATTERNS
- Exact company name only (for example: Tesla, Apple, Reliance Industries).
- Remove polite wrappers and request text (for example: "analyze", "build report for", "please research").
- Keep official suffixes when part of the legal name (Inc., Ltd., PLC, LLC, AG).
- If ticker and company are both present, prefer the full company name.
- If multiple companies are mentioned, select the primary company explicitly asked for analysis.

3. WHAT TO DO
- Identify one best company name from the user's message.
- Return only that company name as plain text.

4. WHAT TO PRODUCE
Produce a single clean company name string with no JSON, bullets, explanation, or extra words.

5. WHAT ON FAILURE
- If no company can be reliably identified, return EXACTLY: UNKNOWN_COMPANY
- Do not guess or hallucinate company names.
"""

company_extractor_agent = LlmAgent(
    name="company_extractor_agent",
    model=FAST_MODEL,
    instruction=COMPANY_EXTRACTOR_INSTRUCTION,
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
    output_key=COMPANY_NAME,
)
