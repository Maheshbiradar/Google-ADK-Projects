# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

# Centralized model strings — change here, updates everywhere
FAST_MODEL  = "gemini-flash-latest"
SMART_MODEL = "gemini-pro-latest"

# Temperature per agent role
PIPELINE_TEMP = 0.1   # factual research needs maximum consistency

# ─────────────────────────────────────────────
# STATE KEYS
# ─────────────────────────────────────────────

# temp: — lives one turn only, discarded after routing
ROUTING_DECISION    = "temp:routing_decision"    # "research" or "recall" — written and read by intent_router_agent
RECALL_QUERY        = "temp:recall_query"        # user's recall question — written by intent_router_agent, read by recall_agent

# session: — lives for the current conversation only
COMPANY_NAME        = "session:company_name"     # extracted company — written by company_extractor_agent, read by research_agent
RESEARCH_RESULTS    = "session:research_results" # JSON result — written by research_agent, read by intent_router_agent
RECALL_RESULTS      = "session:recall_results"   # summarized memory — written by recall_agent, read by intent_router_agent

# user: — survives across sessions
RESEARCHED_COMPANIES = "user:researched_companies"  # comma-separated list — appended by research_agent, read by recall_agent

# ─────────────────────────────────────────────
# COORDINATOR STRUCTURE
# ─────────────────────────────────────────────
# personal_research_assistant → SequentialAgent
#     sub_agents: [company_extractor_agent, intent_router_agent]
#
# intent_router_agent → LlmAgent
#     tools: [AgentTool(research_agent), AgentTool(recall_agent)]
#
# Services:
#     DatabaseSessionService  → SQLite — persists session transcripts
#     InMemoryMemoryService   → keyword search across past sessions