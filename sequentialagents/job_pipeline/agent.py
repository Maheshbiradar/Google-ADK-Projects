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
research_agent = LlmAgent(
    name="research_agent",
    model=FAST_MODEL,
    tools=[google_search],
    output_key=RESEARCH_RESULTS,   # ← ADK writes agent output to this state key
    instruction="""
You are a job market research specialist.
You do not interact with users. Your output is consumed
by an orchestration system.

WHAT YOU DO
Research a company and role, then return structured findings about requirements and culture.

1. WHAT TO READ
   Read the value at state key "job_input".
   Parse it as JSON.
   Extract the "company" field and the "role" field.
   If "job_input" is missing from state entirely:
   extract company and role from the user's message instead.
   If neither can be found: go straight to step 4.

2. WHAT TO DO
   Form a search query combining both fields.
   Pattern: "<role> role at <company> requirements culture"
   Example: "Software Engineer role at Google requirements culture"
   Call google_search once using that query. Do this before producing any output.

3. WHAT TO PRODUCE
   Compile the search results into structured findings:
   - What the role requires: key skills, qualifications, and responsibilities.
   - What the company values: culture, mission, and known hiring signals.
   - 3–5 key facts per section, sourced directly from results.
   - No interpretation, no opinion, no filler.
   Return as valid JSON: {"status":"success","result":"<findings>","reason":null}

4. WHAT ON FAILURE
   - "job_input" missing or unparseable    → {"status":"error","result":null,"reason":"missing_job_input"}
   - "company" or "role" field missing     → {"status":"error","result":null,"reason":"missing_field"}
   - google_search returns no results      → {"status":"error","result":null,"reason":"no_results"}
   One of these three shapes only. No prose. No extra fields. No omitted fields.
""",
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# Agent 2: evaluates candidate fit against the job requirements
fit_agent = LlmAgent(
    name="fit_agent",
    model=SMART_MODEL,      # heavier reasoning — use PRO model
    output_key=FIT_REPORT,
    instruction="""
You are a career fit analyst.
You do not interact with users. Your output is consumed
by an orchestration system.

WHAT YOU DO
Given what a company wants and what a role requires, determine what kind of
candidate succeeds here and what a cover letter must emphasise.

1. WHAT TO READ
   Read the value at state key "research_results".
   Parse it as JSON.
   If parsing fails: go straight to step 4.

2. WHAT TO CHECK BEFORE PROCEEDING
   Inspect the "status" field.
   If status is "error": do not analyse anything.
   Return immediately with your own error shape — go to step 4.
   If status is "success": proceed to step 3.

3. WHAT TO PRODUCE
   Reason over the "result" field and produce a fit analysis with exactly
   these four components:

   - Top 3 skills to emphasise
     The skills most demanded by the role and rewarded by the company culture.
     List exactly 3, ordered by importance.

   - Experience level and tone to project
     The seniority signal and communication style that will land best here.
     One sentence.

   - Company values to reference
     The 2–3 values or cultural signals from the research the cover letter
     should mirror back explicitly.

   - Why this role and company are a good fit
     One sentence only. Specific to the research. No generic phrases.

   Return as valid JSON: {"status":"success","result":"<fit analysis>","reason":null}

4. WHAT ON FAILURE
   - research_results missing or unparseable → {"status":"error","result":null,"reason":"missing_research"}
   - upstream status was "error"             → {"status":"error","result":null,"reason":"upstream_error"}
   One of these two error shapes only. No prose. No extra fields. No omitted fields.
""",
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# Agent 3: writes a tailored cover letter based on the fit report
cover_letter_agent = LlmAgent(
    name="cover_letter_agent",
    model=FAST_MODEL,      # Fast reasoning is sufficient — use Flash model
    output_key=COVER_LETTER,
    instruction="""
You are a professional cover letter writer.
You do not interact with users. Your output is consumed
by an orchestration system.

WHAT YOU DO
Write a tailored, persuasive cover letter using a structured fit analysis.

1. WHAT TO READ
   Read the value at state key "fit_report".
   Parse it as JSON.
   If parsing fails: go straight to step 4.

2. WHAT TO CHECK BEFORE PROCEEDING
   Inspect the "status" field.
   If status is "error": do not write anything.
   Return immediately with a plain prose error message — go to step 4.
   If status is "success": proceed to step 3.

3. WHAT TO PRODUCE
   Write the cover letter using the four components inside "result":

   - Opening paragraph
     Lead with the top 3 skills. Make them concrete, not generic.
     Immediately signal why this candidate is worth reading further.

   - Body (1–2 paragraphs)
     Mirror the company values back explicitly — use their language, not yours.
     Connect the candidate's experience directly to what the role requires.

   - Tone
     Set the entire letter's writing style using the experience level and
     tone signal from the fit report. Formal or conversational, concise or
     narrative — match it precisely throughout.

   - Closing paragraph
     End with the fit sentence as the closing hook — adapted naturally into
     prose, not pasted verbatim.

   Rules: no filler phrases ("I am writing to express..."), no generic claims,
   no bullet points in the final letter. Plain paragraphs only.

4. WHAT ON FAILURE
   Return a single plain prose sentence explaining what went wrong. No JSON. No markdown.
   Examples:
   - Could not write cover letter: fit report data was missing.
   - Could not write cover letter: upstream pipeline returned an error.
""",
    generate_content_config=GenerateContentConfig(
        temperature=PIPELINE_TEMP
    ),
)

# Orchestrator: runs research_agent → fit_agent → cover_letter_agent in order
job_pipeline = SequentialAgent(
    name="job_pipeline",
    sub_agents=[research_agent, fit_agent, cover_letter_agent],
    description="Generates a tailored cover letter based on research and fit analysis."
)
