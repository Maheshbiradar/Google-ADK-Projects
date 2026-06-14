# Personal Research Assistant — Design Document

## 1. Folder Name

personal_research_assistant

## 2. State Keys

temp:routing_decision  
 type: string — "research" or "recall"
writer: intent_router_agent
reader: intent_router_agent (via AgentTool delegation)
why: lives one turn only — decision is irrelevant after routing

session:company_name  
 type: string — "Microsoft"
writer: company_extractor_agent
reader: research_agent
why: only needed for current conversation

session:research_results  
 type: JSON — {"status":"success","result":"...","reason":null}
writer: research_agent
reader: intent_router_agent (via AgentTool return)
why: only needed for current conversation

user:researched_companies
type: string — "Microsoft, Apple, NTT Data"
writer: research_agent
reader: intent_router_agent, recall_agent
why: must survive across sessions

temp:recall_query  
 type: string — "what did you find about Apple?"
writer: intent_router_agent
reader: recall_agent
why: lives one turn only

session:recall_results  
 type: string — summarized memory content
writer: recall_agent
reader: intent_router_agent (via AgentTool return)
why: only needed for current conversation

## 3. Models

company_extractor_agent — FAST_MODEL
Mechanical extraction — reads user message, returns company name.
No reasoning required. FAST_MODEL is sufficient.

intent_router_agent — FAST_MODEL
Binary classification — research or recall.
Pattern matching, not reasoning. FAST_MODEL is sufficient.

research_agent — FAST_MODEL
Web search and summarize — single pass, one angle.
Not deep reasoning. FAST_MODEL is sufficient.

recall_agent — FAST_MODEL
Searches memory transcripts and summarizes findings.
Retrieval not reasoning. FAST_MODEL is sufficient.

response_agent — SMART_MODEL
Synthesizes research or recall output into clean response.
Requires judgment and coherent prose. SMART_MODEL is required.

## 4. Coordinator Roster

intent_router_agent — LlmAgent
tools: [AgentTool(research_agent), AgentTool(recall_agent)]

personal_research_assistant — SequentialAgent
sub_agents: [company_extractor_agent, intent_router_agent]

## 5. Intent Routing Rules

Research intent:
"Research about company Microsoft"
"Can you tell me about Microsoft"
"Give me details about Microsoft"
"Provide me details in terms of news, competitor, market trends"
"Microsoft" — company name only

Recall intent:
"Give me details of the last company I searched"
"What was the report for Microsoft?"
"What do you know about Apple from before?"
"What companies have I researched?"
"Summarize what you found about NTT Data last time"
"What did you find previously?"

Signal words:
Research — research, tell me about, details, analyze
Recall — last, before, previously, found, remember, history

## 6. Memory Contract

During session:
research_agent writes session:research_results
research_agent appends company to user:researched_companies

When session ends:
session:research_results — deleted, session scope
user:researched_companies — survives, user scope
Full transcript — saved by DatabaseSessionService
Key facts — indexed by InMemoryMemoryService

Future session recall:
recall_agent calls load_memory with user query
InMemoryMemoryService searches transcripts by keyword
Returns matching transcript content
recall_agent summarizes and presents to user
