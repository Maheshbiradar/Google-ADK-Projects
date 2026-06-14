# State keys
COMPANY_NAME = "company_name"
NEWS_AND_RECENT_DEVELOPMENTS_RESULTS = "news_and_recent_developments_results"
FINANCIAL_MARKET_ANALYSIS_RESULTS = "financial_market_analysis_results"
COMPETITOR_LANDSCAPE_RESULTS = "competitor_landscape_results"
COVERAGE_SCORE = "coverage_score"
FINAL_REPORT = "final_report"

# Shape: {"news_and_recent_developments": 8, "financial_market_analysis": 9, "competitor_landscape": 8, "overall": 8.3}
COVERAGE_SCORE_KEYS = ["news_and_recent_developments", "financial_market_analysis", "competitor_landscape", "overall"]

COVERAGE_PASSING_THRESHOLD = 8.0

LOOP_MAX_ITERATIONS = 3

# Centralized model strings — change here, updates everywhere
FAST_MODEL  = "gemini-flash-latest"   # news_agent, financial_agent, competitor_agent — parallel search
SMART_MODEL = "gemini-pro-latest"     # evaluator_agent, report_agent — heavy reasoning / synthesis

# Temperature per agent role
PIPELINE_TEMP = 0.1   # factual research needs maximum consistency
# research_parallel             → ParallelAgent  (news_agent, financial_agent, competitor_agent)
# research_loop                 → LoopAgent       (research_parallel + evaluator_agent)
# competitive_intelligence_pipeline → SequentialAgent  (company_extractor_agent → research_loop → report_agent)

