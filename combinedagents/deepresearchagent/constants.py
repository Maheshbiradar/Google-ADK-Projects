# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

# Centralized model strings — change here, updates everywhere
FAST_MODEL  = "gemini-flash-latest"   # news_agent, academic_agent, industry_agent — parallel search
SMART_MODEL = "gemini-pro-latest"     # evaluator_agent, report_agent — heavy reasoning / synthesis

# Temperature per agent role
PIPELINE_TEMP = 0.1   # factual research needs maximum consistency

# ─────────────────────────────────────────────
# STATE KEYS
# ─────────────────────────────────────────────

TOPIC              = "topic"               # seed
NEWS_RESULTS       = "news_results"        # news accumulator
ACADEMIC_RESULTS   = "academic_results"    # academic accumulator
INDUSTRY_RESULTS   = "industry_results"    # industry accumulator
COVERAGE_SCORE     = "coverage_score"      # written by evaluator_agent
FINAL_REPORT       = "final_report"        # written by report_agent

# ─────────────────────────────────────────────
# COVERAGE SCORE
# ─────────────────────────────────────────────

# Shape: {"news": 8, "academic": 9, "industry": 8, "overall": 8.3}
COVERAGE_SCORE_KEYS = ["news", "academic", "industry", "overall"]
COVERAGE_PASSING_THRESHOLD = 8.0   # minimum overall score to exit the loop

# ─────────────────────────────────────────────
# COORDINATOR CONFIG
# ─────────────────────────────────────────────

# research_parallel  → ParallelAgent  (news_agent, academic_agent, industry_agent)
# research_loop      → LoopAgent      (research_parallel + evaluator_agent)
# deep_research_pipeline → SequentialAgent (research_loop → report_agent)

LOOP_MAX_ITERATIONS = 3
