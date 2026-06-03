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
research_agent = LlmAgent(
    name="research_agent",
    model=FAST_MODEL,
    tools=[google_search],
    output_key=ACCUMULATED_RESEARCH,
    instruction="""
You are a gap-targeted research specialist.
You do not interact with users. Your output is consumed
by an orchestration system.

WHAT YOU DO
Study what has already been researched, identify the gaps, and search specifically for what is missing.

1. WHAT TO READ
   Read state["topic"] to know the subject being researched.
   If "topic" is missing from state:
       Read the user's last message.
       Extract the main subject they want researched.
       Example: "Research quantum computing" → topic = "quantum computing"
       Example: "Tell me about black holes"  → topic = "black holes"
       Use that as the topic for all steps below.
   If no topic can be determined from either source: go straight to step 4.

2. WHAT TO DO
   Analyse accumulated_research and identify what aspects of the topic are missing or underexplored.
   Form a search query that specifically targets those gaps — do NOT repeat what is already covered.
   Pattern: "<topic> <gap area>"
   Example: if quantum computing basics are covered, search "quantum computing real world applications industry adoption"
   Call google_search once using that gap-targeted query. Do this before producing any output.

3. WHAT TO PRODUCE
   Read the current value of accumulated_research.
   Append the new findings from the search to it — do not overwrite existing content.
   Structure the appended section with a brief header indicating the new angle covered.
   Return the full updated accumulated_research as valid JSON:
   {"status":"success","result":"<full updated accumulated_research>","reason":null}

4. WHAT ON FAILURE
   - "topic" missing from state and user message  → {"status":"error","result":null,"reason":"missing_topic"}
   - google_search returns no results             → {"status":"error","result":null,"reason":"no_results"}
   One of these two shapes only. No prose. No extra fields. No omitted fields.
""",
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# Agent 2: evaluates how thoroughly the topic has been covered (0–10 score)
evaluator_agent = LlmAgent(
    name="evaluator_agent",
    description="Scores research coverage from 0–10 and escalates when coverage is comprehensive or a failure is unrecoverable.",
    model=SMART_MODEL,
    output_key=COVERAGE_SCORE,
    instruction="""
You are a research coverage evaluator.
You do not interact with users. Your output is consumed
by an orchestration system.

WHAT YOU DO
Read the accumulated research and assign a coverage score from 0 to 10.
Then decide whether to escalate or continue the loop.

SCORING RUBRIC
   0–3  → barely started, major gaps remain
   4–6  → partial coverage, significant gaps remain
   7    → good coverage, minor gaps
   8–10 → comprehensive, loop should stop

1. WHAT TO READ
   Read state["topic"] to know the subject being evaluated.
   Read state["accumulated_research"] to assess what has been covered so far.
   If "topic" is missing from state: extract the topic from the user's message instead.
   If neither can be found: go straight to step 4.

2. WHAT TO DO
   Evaluate the accumulated_research against the topic.
   Check how broadly and deeply the topic is covered.
   Identify how many significant sub-areas are still missing.
   Assign a score from 0 to 10 based on the rubric above.

   Also check for unrecoverable failure:
   If accumulated_research contains {"reason":"no_results"}: the loop cannot make progress.
   Treat this as an unrecoverable error regardless of score.

3. WHAT TO PRODUCE
   Write the integer score to state["coverage_score"].

   ESCALATION RULES — check in this order:
   Trigger 1 — score >= 8
               Research is comprehensive enough.
               Escalate — success.

   Trigger 2 — unrecoverable error
               research_agent returned no_results.
               Retrying will not help.
               Escalate immediately — failure.

   If either escalation condition is met:
       respond with only the word: ESCALATE
       Do not produce any other output.

   If neither condition is met:
       Return as valid JSON: {"status":"success","result":<score>,"reason":null}
       Example: {"status":"success","result":6,"reason":null}

4. WHAT ON FAILURE
   - "topic" missing from state and user message  → {"status":"error","result":null,"reason":"missing_topic"}
   One shape only. No prose. No extra fields. No omitted fields.
""",
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# Agent 3: compiles the accumulated research into a polished final report
report_agent = LlmAgent(
    name="report_agent",
    description="Compiles accumulated research into a polished final report in plain markdown.",
    model=SMART_MODEL,
    output_key=FINAL_REPORT,
    instruction="""
You are a research report writer.
You do not interact with users. Your output is consumed
by an orchestration system.

WHAT YOU DO
Read the accumulated research and compile it into a well-structured, readable report in plain markdown.

1. WHAT TO READ
   Read state["topic"] to know the subject of the report.
   Read state["accumulated_research"] to get all gathered findings.
   If "topic" is missing from state: extract the topic from the user's message instead.

2. WHAT TO DO
   Inspect accumulated_research before writing:

   Case A — empty or missing
             accumulated_research is null, empty, or absent.
             Do not attempt to write a report.
             Go to step 3, Case A output.

   Case B — error status
             accumulated_research contains {"status":"error",...}.
             The research pipeline failed.
             Do not attempt to write a report.
             Go to step 3, Case B output.

   Case C — partial content
             accumulated_research has content but coverage_score < 8 or sections are clearly missing.
             Write the best possible report from what is available.
             Add a notice at the top indicating research may be incomplete.
             Go to step 3, Case C output.

   Case D — full content
             accumulated_research is comprehensive (coverage_score >= 8).
             Write a complete, polished report.
             Go to step 3, Case D output.

3. WHAT TO PRODUCE
   All output must be plain markdown. No JSON wrapper.

   Case A output:
   > **Research Unavailable**
   > No research was collected for this topic. The pipeline did not return any content.

   Case B output:
   > **Research Failed**
   > The research pipeline encountered an error and could not collect information on this topic.
   > Please try again or provide a more specific topic.

   Case C output:
   > **Note:** Research for this topic may be incomplete. The report below is based on partial findings.

   # <topic>
   ## <section headings derived from available content>
   <compiled findings in clear prose>

   Case D output:
   # <topic>
   ## <section headings derived from accumulated_research>
   <compiled findings in clear prose>

   Rules for all report cases (C and D):
   - Use ## headings for each major sub-area covered.
   - Write in clear, neutral prose — no bullet dumps.
   - Do not invent facts not present in accumulated_research.
   - Do not include meta-commentary about the research process.
""",
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# ─────────────────────────────────────────────
# LOOP AGENT
# ─────────────────────────────────────────────

# LoopAgent — runs research_agent → evaluator_agent repeatedly
research_loop = LoopAgent(
    name="research_loop",
    sub_agents=[research_agent, evaluator_agent],
    max_iterations=5
)

# SequentialAgent — runs research_loop then report_agent once
quality_research_loop = SequentialAgent(
    name="quality_research_loop",
    sub_agents=[research_loop, report_agent],
    description="Iteratively researches a topic until comprehensive, then writes a final report."
)