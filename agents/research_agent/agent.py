from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools import ToolContext
from google.genai import types
import datetime


# ─────────────────────────────────────────────────────────────
# CUSTOM TOOLS — go on the root agent only (no built-ins here)
# ─────────────────────────────────────────────────────────────

def save_research_note(
    topic: str,
    note: str,
    tool_context: ToolContext
) -> dict:
    """Saves an important research finding or note to session memory.

    Use this to preserve key facts or insights discovered
    during research so they can be referenced later.

    Args:
        topic: Short label for what this note is about.
        note: The actual finding or fact to save.

    Returns:
        Dictionary confirming the note was saved.
    """
    notes = tool_context.state.get("research_notes", {})
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    notes[topic] = {"content": note, "saved_at": timestamp}
    tool_context.state["research_notes"] = notes

    return {
        "status": "success",
        "message": f"Note saved under: '{topic}'",
        "total_notes": len(notes)
    }


def get_research_notes(tool_context: ToolContext) -> dict:
    """Retrieves all research notes saved in this session.

    Returns all previously saved findings organized by topic.

    Returns:
        Dictionary containing all saved research notes.
    """
    notes = tool_context.state.get("research_notes", {})
    if not notes:
        return {
            "status": "success",
            "message": "No research notes saved yet.",
            "notes": {}
        }
    return {
        "status": "success",
        "topic_count": len(notes),
        "notes": notes
    }


def create_research_outline(
    title: str,
    sections: str,
    tool_context: ToolContext
) -> dict:
    """Creates a structured research outline saved to the session.

    Use this after gathering enough information to organize
    findings into a clear report structure.

    Args:
        title: The main title of the research report.
        sections: Comma-separated list of section headings.

    Returns:
        Dictionary with the structured outline.
    """
    section_list = [s.strip() for s in sections.split(",")]
    outline = {
        "title": title,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "sections": section_list,
        "section_count": len(section_list)
    }
    tool_context.state["research_outline"] = outline
    return {
        "status": "success",
        "outline": outline,
        "message": f"Outline created with {len(section_list)} sections."
    }


# ─────────────────────────────────────────────────────────────
# SPECIALIST AGENT 1 — Search only, no custom function tools
# Rule: google_search cannot share an agent with custom tools
# ─────────────────────────────────────────────────────────────

search_agent = Agent(
    model="gemini-2.5-flash",
    name="search_agent",
    description=(
        "Specialist web search agent. Searches the internet for "
        "current information, recent developments, statistics, "
        "and factual data on any topic."
    ),
    instruction="""
You are a specialist web search agent. Your only job is to search
the web and return comprehensive, well-organized findings.

[SEARCH STRATEGY]
- Run 2-3 searches per topic using different angle queries
- First search: broad overview — "topic overview 2025"
- Second search: specific details — "topic key statistics data"
- Third search: recent developments — "topic latest news trends"
- Report ALL relevant findings clearly, with source context
- Never answer from memory — always search first

[OUTPUT FORMAT]
Return findings as:
  SEARCH 1: [query used]
  Findings: [what you found]

  SEARCH 2: [query used]  
  Findings: [what you found]

  SYNTHESIS: [combined key insights across all searches]
""",
    tools=[google_search],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,  # Low — factual search needs consistency
    ),
)


# ─────────────────────────────────────────────────────────────
# SPECIALIST AGENT 2 — Code execution only, no other tools
# Rule: BuiltInCodeExecutor cannot share agent with custom tools
# ─────────────────────────────────────────────────────────────

code_agent = Agent(
    model="gemini-2.5-flash",
    name="code_agent",
    description=(
        "Specialist Python code execution agent. Writes and runs "
        "Python code for data analysis, calculations, visualizations, "
        "and algorithm demonstrations."
    ),
    instruction="""
You are a specialist Python code execution agent.
You write clean, well-commented Python and execute it immediately.

[CODE RULES]
- Always print() results explicitly — output is only captured via print
- Write defensive code with try/except for edge cases
- For visualizations: use matplotlib, add clear labels and titles,
  call plt.tight_layout() before showing
- For data analysis: use pandas and numpy where appropriate
- Comment your code so the user understands what each section does

[WHAT YOU CAN DO]
- Mathematical calculations and simulations
- Data analysis and statistical computations  
- Generate charts and visualizations
- Demonstrate algorithms step by step
- Process and transform structured data

After executing, explain:
1. What the code did
2. What the output means
3. Any interesting observations from the results
""",
    code_executor=BuiltInCodeExecutor(),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
    ),
)


# ─────────────────────────────────────────────────────────────
# ROOT AGENT — Orchestrates everything
# Has custom tools + delegates to specialists via AgentTool
# Rule: custom tools are fine here since no built-ins are mixed
# ─────────────────────────────────────────────────────────────

root_agent = Agent(
    model="gemini-2.5-flash",

    name="research_assistant",

    description=(
        "Master research assistant that coordinates web search, "
        "code execution, and note-taking to produce comprehensive "
        "research reports on any topic."
    ),

    instruction="""
You are ResearchBot, an expert research assistant that coordinates
a team of specialist agents to produce thorough research.

[YOUR TEAM]
- search_agent: Use for ALL web searches and current information
- code_agent: Use for data analysis, calculations, and visualizations
- save_research_note: Save important findings to session memory
- get_research_notes: Retrieve all notes saved this session
- create_research_outline: Build a structured report outline

[YOUR RESEARCH PROCESS]
1. DELEGATE SEARCH — send the topic to search_agent with clear 
   instructions on what angles to cover (2-3 different queries)

2. SAVE KEY FINDINGS — as search_agent returns results, use 
   save_research_note to preserve the most important facts

3. ANALYZE WITH CODE (when relevant) — if the research involves
   numbers, trends, or data worth visualizing, delegate to 
   code_agent with specific instructions on what to compute/show

4. OUTLINE & SYNTHESIZE — use create_research_outline to structure
   your findings, then write a comprehensive final response

[DELEGATION RULES]
- Always delegate searches to search_agent — never search yourself
- Give search_agent specific, detailed instructions including
  what angles to cover and what kind of data you need
- Give code_agent clear specs: what to compute, what to visualize,
  what data to use (provide the data explicitly if needed)

[RESPONSE FORMAT]
## Research Report: [Topic]

### Overview
[2-3 sentence executive summary]

### Key Findings
[Numbered list of the most important discoveries with data points]

### Analysis  
[Deeper synthesis — patterns, implications, what it all means]

### Data & Visualizations
[If code was run, explain what it showed]

### Sources
[Note which findings came from web searches]
""",

    tools=[
        # Specialist agents wrapped as tools — this is AgentTool pattern
        AgentTool(agent=search_agent),
        AgentTool(agent=code_agent),
        # Custom session tools — safe here, no built-ins on this agent
        save_research_note,
        get_research_notes,
        create_research_outline,
    ],

    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=4096,
    ),
)