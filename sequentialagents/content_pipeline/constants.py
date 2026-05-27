
# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

# Centralized model strings — change here, updates everywhere
FAST_MODEL  = "gemini-flash-latest"   # research_agent and format_agent
SMART_MODEL = "gemini-pro-latest"     # summary_agent — heavy reasoning

# Temperature per agent role
PIPELINE_TEMP = 0.1   # factual search needs maximum consistency

# ─────────────────────────────────────────────
# STATE KEYS
# ─────────────────────────────────────────────

TOPIC            = "topic"
RESEARCH_RESULTS = "research_results"
SUMMARY          = "summary"
FINAL_REPORT     = "final_report"