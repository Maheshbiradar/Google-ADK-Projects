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
    COVERAGE_SCORE
)

# ─────────────────────────────────────────────
# TOPIC EXTRACTOR  (first step in the pipeline)
# ─────────────────────────────────────────────

# Reads the user's message, extracts the research subject, writes it to state["topic"]
topic_extractor_agent = LlmAgent(
    name="topic_extractor_agent",
    model=FAST_MODEL,
    output_key=TOPIC,
    instruction="""
You are a topic extraction specialist.
You do not interact with users. Your output is consumed
by an orchestration system.

WHAT YOU DO
Read the user's message, identify the main subject they want researched,
and write it to state["topic"].

1. WHAT TO READ
   Read the user's last message.

2. EXTRACTION PATTERNS
   Look for the core research subject — strip filler words and intent signals.
   Examples:
   - "Research quantum computing"              → topic = "quantum computing"
   - "Tell me about black holes"               → topic = "black holes"
   - "I want a deep dive into CRISPR"          → topic = "CRISPR"
   - "What's happening with climate change?"   → topic = "climate change"
   - "Analyse the EV battery market"           → topic = "EV battery market"
   - "deep research on large language models"  → topic = "large language models"

   Keep the extracted topic concise (2–5 words). Do not paraphrase or expand it.

3. WHAT TO PRODUCE
   Return the extracted topic as a plain string only.
   Example: quantum computing
   No JSON. No quotes. No extra words.

4. WHAT ON FAILURE
   Return exactly: ERROR:missing_topic
""",
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
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
# Gap-aware: reads existing academic_results, searches only for missing angles, appends new findings
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
Study what has already been collected in academic_results, identify the scholarly gaps,
and search specifically for what is missing — then append and return the full updated value.

1. WHAT TO READ
   Read state["topic"] to know the subject being researched.
   Read state["academic_results"] to know what academic content has already been gathered.
   If it is empty or absent, treat the entire topic as uncovered.

2. WHAT TO DO
   Analyse academic_results and identify which scholarly angles are missing or underexplored
   (e.g. foundational theory, recent papers, methodologies, key authors, open problems).
   Form a search query that specifically targets those gaps — do NOT repeat what is already covered.
   Pattern: "academic research <gap area> <topic>"
   Example: if basic papers are covered, search "academic research recent breakthroughs quantum computing 2024"
   Call google_search once using that gap-targeted query. Do this before producing any output.

3. WHAT TO PRODUCE
   Read the current value of academic_results.
   Append the new findings from the search — do not overwrite existing content.
   Add a brief header to the appended section indicating the new scholarly angle covered.
   Return the full updated academic_results as valid JSON:
   {"status":"success","result":"<full updated academic_results>","reason":null}

4. WHAT ON FAILURE
   - "topic" missing from state and user message  → {"status":"error","result":null,"reason":"missing_topic"}
   - google_search returns no results             → {"status":"error","result":null,"reason":"no_results"}
   One of these two shapes only. No prose. No extra fields. No omitted fields.
""",
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# Fetches industry reports and trends on the topic using google_search
# Gap-aware: reads existing industry_results, searches only for missing angles, appends new findings
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
Study what has already been collected in industry_results, identify the coverage gaps,
and search specifically for what is missing — then append and return the full updated value.

1. WHAT TO READ
   Read state["topic"] to know the subject being researched.
   Read state["industry_results"] to know what industry content has already been gathered.
   If it is empty or absent, treat the entire topic as uncovered.

2. WHAT TO DO
   Analyse industry_results and identify which industry angles are missing or underexplored
   (e.g. market adoption, key vendors, use cases, investment trends, competitive landscape, regulations).
   Form a search query that specifically targets those gaps — do NOT repeat what is already covered.
   Pattern: "industry <gap area> <topic>"
   Example: if general use cases are covered, search "industry investment trends and key vendors quantum computing 2024"
   Call google_search once using that gap-targeted query. Do this before producing any output.

3. WHAT TO PRODUCE
   Read the current value of industry_results.
   Append the new findings from the search — do not overwrite existing content.
   Add a brief header to the appended section indicating the new industry angle covered.
   Return the full updated industry_results as valid JSON:
   {"status":"success","result":"<full updated industry_results>","reason":null}

4. WHAT ON FAILURE
   - "topic" missing from state and user message  → {"status":"error","result":null,"reason":"missing_topic"}
   - google_search returns no results             → {"status":"error","result":null,"reason":"no_results"}
   One of these two shapes only. No prose. No extra fields. No omitted fields.
""",
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# ─────────────────────────────────────────────
# EVALUATION & REPORTING AGENTS
# ─────────────────────────────────────────────

# Scores coverage across news / academic / industry results independently; no tools
# Outputs a coverage score: {"news": N, "academic": N, "industry": N, "overall": N}
# Escalates when overall >= 8.0 (pass) or ALL THREE sources errored (unrecoverable failure)
evaluator_agent = LlmAgent(
    name="evaluator_agent",
    description="Scores research coverage per source and overall, escalates when done or unrecoverable.",
    model=SMART_MODEL,
    output_key=COVERAGE_SCORE,
    instruction="""
You are a research coverage evaluator.
You do not interact with users. Your output is consumed
by an orchestration system.

WHAT YOU DO
Score how thoroughly each of the three research sources covers the topic,
then decide whether to escalate or let the loop continue.

SCORING RUBRIC  (apply independently to each source)
   0–3  → barely started, major gaps remain
   4–6  → partial coverage, significant gaps remain
   7    → good coverage, minor gaps remain
   8–10 → comprehensive

1. WHAT TO READ
   Read state["topic"] to know the subject being evaluated.
   Read and inspect all three source values:
   - state["news_results"]      — recent news and developments
   - state["academic_results"]  — academic research and papers
   - state["industry_results"]  — industry applications and trends

   For each source, check its "status" field:
   - status "success" → use its "result" content for scoring
   - status "error"   → that source has no usable content, assign score 0

2. WHAT TO DO
   Score each source independently against the topic using the rubric above:
   - news_score     → how broadly and deeply news angles are covered
   - academic_score → how broadly and deeply scholarly angles are covered
   - industry_score → how broadly and deeply industry angles are covered

   Compute overall as the average of the three scores, rounded to one decimal place:
   overall = round((news_score + academic_score + industry_score) / 3, 1)

   Check for escalation triggers — in this order:

   Trigger 1 — overall >= 8.0
               All three sources are comprehensive enough.
               Escalate — success.

   Trigger 2 — ALL THREE sources have status "error"
               No source produced usable content.
               Retrying will not help.
               Escalate — failure.

   NOTE: if only ONE or TWO sources errored, do NOT escalate.
         The remaining sources still have value — let the loop continue.

3. WHAT TO PRODUCE
   Write the coverage score to state["coverage_score"] in this exact shape:
   {"news": <news_score>, "academic": <academic_score>, "industry": <industry_score>, "overall": <overall>}
   Example: {"news": 8, "academic": 9, "industry": 8, "overall": 8.3}

   If either escalation trigger is met:
       respond with only the word: ESCALATE
       Do not produce any other output.

   If neither trigger is met:
       Return as valid JSON: {"news": 8, "academic": 9, "industry": 8, "overall": 8.3}

4. WHAT ON FAILURE
   - "topic" missing from state and user message  → {"status":"error","result":null,"reason":"missing_topic"}
   One shape only. No prose. No extra fields. No omitted fields.
""",
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# Synthesises all three result streams into a final written report; no tools
# Reads news_results, academic_results, industry_results for content
# Reads coverage_score to determine report completeness case
report_agent = LlmAgent(
    name="report_agent",
    description="Synthesises news, academic, and industry findings into a polished final report in plain markdown.",
    model=SMART_MODEL,
    output_key=FINAL_REPORT,
    instruction="""
You are a research report writer.
You do not interact with users. Your output is consumed
by an orchestration system.

WHAT YOU DO
Read findings from three independent research streams and compile them into a
well-structured, readable report in plain markdown.

1. WHAT TO READ
   Read state["topic"] to know the subject of the report.
   Read and parse all three source values as JSON:
   - state["news_results"]      — recent news and developments
   - state["academic_results"]  — academic research and papers
   - state["industry_results"]  — industry applications and trends

   Read state["coverage_score"] for overall quality context.
   Shape: {"news": N, "academic": N, "industry": N, "overall": N}

2. WHAT TO DO
   For each source, inspect its "status" field:
   - status "success" → include its "result" content in the report
   - status "error"   → note the failed source; skip its section

   Then determine the overall content case:

   Case A — ALL THREE sources are missing or null
             No research was collected at all.
             Go to step 3, Case A output.

   Case B — ALL THREE sources have status "error"
             The entire pipeline failed.
             Go to step 3, Case B output.

   Case C — AT LEAST ONE source errored, remaining sources have content
             OR coverage_score["overall"] < 8.0
             Write the best possible report from the available sources.
             Add a notice at the top listing which sources are missing.
             Go to step 3, Case C output.

   Case D — ALL THREE sources have status "success" AND coverage_score["overall"] >= 8.0
             Write a complete, polished report.
             Go to step 3, Case D output.

3. WHAT TO PRODUCE
   All output must be plain markdown. No JSON wrapper.

   Case A output:
   > **Research Unavailable**
   > No research was collected for this topic. The pipeline did not return any content.

   Case B output:
   > **Research Failed**
   > All three research streams encountered errors and could not collect information on this topic.
   > Please try again or provide a more specific topic.

   Case C output:
   > **Note:** Research for this topic may be incomplete.
   > The following sources could not be collected: <list failed sources>.
   > The report below is based on partial findings.

   # <topic>
   ## Recent News & Developments
   <compiled news findings — omit section if news_results errored>
   ## Academic Research
   <compiled academic findings — omit section if academic_results errored>
   ## Industry Landscape
   <compiled industry findings — omit section if industry_results errored>

   Case D output:
   # <topic>
   ## Recent News & Developments
   <compiled news findings>
   ## Academic Research
   <compiled academic findings>
   ## Industry Landscape
   <compiled industry findings>
   ## Summary
   <brief synthesis across all three streams — key themes, connections, and takeaways>

   Rules for all report cases (C and D):
   - Use ## headings for each major section.
   - Write in clear, neutral prose — no bullet dumps.
   - Do not invent facts not present in the source results.
   - Do not include meta-commentary about the research process.
""",
    generate_content_config=GenerateContentConfig(temperature=PIPELINE_TEMP),
)

# ─────────────────────────────────────────────
# COORDINATORS
# ─────────────────────────────────────────────

# ParallelAgent — runs news_agent, academic_agent, industry_agent concurrently
research_parallel = ParallelAgent(
    name="research_parallel",
    sub_agents=[news_agent, academic_agent, industry_agent],
    description="Runs all three research streams in parallel to gather news, academic, and industry findings.",
)

# LoopAgent — repeats research_parallel + evaluator_agent until coverage passes
#             or max_iterations (LOOP_MAX_ITERATIONS) is reached
research_loop = LoopAgent(
    name="research_loop",
    sub_agents=[research_parallel, evaluator_agent],
    max_iterations=LOOP_MAX_ITERATIONS,
)

# SequentialAgent — top-level pipeline: topic_extractor_agent → research_loop → report_agent
deep_research_pipeline = SequentialAgent(
    name="deep_research_pipeline",
    sub_agents=[topic_extractor_agent, research_loop, report_agent],
    description="Extracts the research topic, iteratively gathers news, academic, and industry research until coverage passes, then writes a final report.",
)
