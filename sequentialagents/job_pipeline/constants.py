
# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

# Centralized model strings — change here, updates everywhere
FAST_MODEL  = "gemini-flash-latest"   # research_agent and cover_letter_agent
SMART_MODEL = "gemini-pro-latest"     # fit_agent — heavy reasoning

# Temperature per agent role
PIPELINE_TEMP = 0.1   # factual search needs maximum consistency

# ─────────────────────────────────────────────
# STATE KEYS
# ─────────────────────────────────────────────

JOB_INPUT        = "job_input"
RESEARCH_RESULTS = "research_results"
FIT_REPORT       = "fit_report"
COVER_LETTER     = "cover_letter"