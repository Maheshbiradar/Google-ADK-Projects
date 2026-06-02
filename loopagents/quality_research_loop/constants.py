# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

# Centralized model strings — change here, updates everywhere
FAST_MODEL  = "gemini-flash-latest"   # research_agent
SMART_MODEL = "gemini-pro-latest"     # evaluator_agent and report_agent — heavy reasoning

# Temperature per agent role
PIPELINE_TEMP = 0.1   # factual research needs maximum consistency

# ─────────────────────────────────────────────
# STATE KEYS
# ─────────────────────────────────────────────

TOPIC               = "topic"
ACCUMULATED_RESEARCH = "accumulated_research"
COVERAGE_SCORE      = "coverage_score"
FINAL_REPORT        = "final_report"
