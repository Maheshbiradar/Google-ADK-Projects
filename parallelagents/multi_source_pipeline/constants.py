
# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

# Centralized model strings — change here, updates everywhere
FAST_MODEL  = "gemini-flash-latest"   # news_agent, academic_agent, and industry_agent
SMART_MODEL = "gemini-pro-latest"     # format_agent — heavy reasoning / synthesis

# Temperature per agent role
PIPELINE_TEMP = 0.1   # factual search needs maximum consistency

# ─────────────────────────────────────────────
# STATE KEYS
# ─────────────────────────────────────────────

TOPIC              = "topic"
NEWS_RESULTS       = "news_results"
ACADEMIC_RESULTS   = "academic_results"
INDUSTRY_RESULTS   = "industry_results"
FINAL_REPORT       = "final_report"
