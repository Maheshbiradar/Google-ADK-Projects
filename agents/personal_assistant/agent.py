import os
import requests
import datetime
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.code_executors import BuiltInCodeExecutor
from google.genai import types

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

# Centralized model strings — change here, updates everywhere
FAST_MODEL  = "gemini-flash-latest"   # all three agents use this
SMART_MODEL = "gemini-pro-latest"     # swap root_agent here for harder tasks

# Temperature per agent role
SEARCH_TEMP = 0.1   # factual search needs maximum consistency
CODE_TEMP   = 0.2   # code generation needs consistency but slight flexibility
ROOT_TEMP   = 0.3   # coordinator needs some flexibility to handle varied requests

# ─────────────────────────────────────────────
# SPECIALIST AGENT 1 — Search
# Rule: google_search cannot share agent with custom tools
# This agent has ONLY google_search — nothing else
# ─────────────────────────────────────────────

search_agent = Agent(
    model=FAST_MODEL,
    name="search_agent",
    description=(
        "Specialist web search agent. Searches the internet for "
        "current information, recent news, factual data, people, "
        "companies, events, and any topic requiring up-to-date "
        "information beyond training knowledge."
    ),
    instruction="""
You are a specialist web search agent. Your only job is to
search the web and return thorough, well-organized findings.

[SEARCH STRATEGY]
For every request, run 2 searches minimum:
  Search 1 → broad overview of the topic
  Search 2 → specific details, data, or recent developments

For complex topics run a third search from a different angle.

[OUTPUT FORMAT]
Return your findings clearly structured:

  SEARCH 1: [exact query you used]
  Key findings: [bullet points of what you found]

  SEARCH 2: [exact query you used]
  Key findings: [bullet points of what you found]

  SUMMARY: [2-3 sentence synthesis of all findings]

Always tell the user which information came from web search
vs what you already knew from training.
""",
    tools=[google_search],
    generate_content_config=types.GenerateContentConfig(
        temperature=SEARCH_TEMP,
    ),
)

# ─────────────────────────────────────────────
# SPECIALIST AGENT 2 — Code Execution
# Rule: BuiltInCodeExecutor cannot share agent with custom tools
# This agent uses code_executor — no tools list at all
# ─────────────────────────────────────────────

code_agent = Agent(
    model=FAST_MODEL,
    name="code_agent",
    description=(
        "Specialist Python code execution agent. Writes and runs "
        "Python code for complex calculations, data analysis, "
        "statistical computations, visualizations, and algorithm "
        "demonstrations. Use when math is too complex for a simple "
        "calculator or when the user wants to see code or a chart."
    ),
    instruction="""
You are a specialist Python code execution agent.
You write clean, well-commented Python and run it immediately.

[WHAT YOU DO]
- Complex mathematical calculations and simulations
- Statistical analysis on datasets
- Data visualizations with matplotlib
- Algorithm demonstrations step by step
- Any computation too complex for simple arithmetic

[CODE RULES]
1. Always print() results — output is only captured via print
2. Write defensive code — use try/except for edge cases
3. For charts: use clear titles, axis labels, plt.tight_layout()
4. Comment every logical section of your code
5. After running, explain what the output means in plain English

[OUTPUT FORMAT]
  WHAT I COMPUTED: [plain English explanation of the task]
  CODE RESULT: [the printed output]
  INTERPRETATION: [what these numbers/chart mean]
""",
    code_executor=BuiltInCodeExecutor(),
    generate_content_config=types.GenerateContentConfig(
        temperature=CODE_TEMP,
    ),
)

# ─────────────────────────────────────────────
# CUSTOM TOOLS — live on root_agent directly
# ─────────────────────────────────────────────

def get_weather(city: str, tool_context: ToolContext) -> dict:
    """Gets current weather conditions for any city worldwide.

    Fetches real-time temperature, humidity, wind speed and
    conditions. Results are cached in session state so repeated
    requests for the same city do not make extra API calls.

    Args:
        city: Name of the city to get weather for.
              Examples: "London", "Tokyo", "Charlotte"

    Returns:
        Dictionary with current weather data for the city.
    """
    # ── Cache check ──────────────────────────────────────────
    # Read the weather cache from state
    # Keys are city names, values are weather dicts
    cache = tool_context.state.get("weather_cache", {})
    city_key = city.lower().strip()

    if city_key in cache:
        cached = cache[city_key]
        return {
            "status": "success",
            "source": "cache",
            "note": "From earlier this session",
            **cached
        }
    # ── Live API call ────────────────────────────────────────
    api_key = os.getenv("OPENWEATHER_API_KEY")

    # Graceful fallback if no API key configured
    if not api_key:
        return {
            "status": "error",
            "message": (
                "Weather API key not configured. "
                "Add OPENWEATHER_API_KEY to your .env file."
            )
        }

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric"
        }
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 404:
            return {
                "status": "error",
                "message": (
                    f"City '{city}' not found. "
                    f"Check the spelling and try again."
                )
            }

        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"Weather service error: {response.status_code}"
            }

        data = response.json()

        # ── Structure the result ──────────────────────────────
        weather_data = {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature_c": round(data["main"]["temp"], 1),
            "feels_like_c": round(data["main"]["feels_like"], 1),
            "humidity_pct": data["main"]["humidity"],
            "condition": data["weather"][0]["description"].title(),
            "wind_kmh": round(data["wind"]["speed"] * 3.6, 1),
            "visibility_km": round(
                data.get("visibility", 0) / 1000, 1
            ),
        }

        # ── Save to cache in state ────────────────────────────
        cache[city_key] = weather_data
        tool_context.state["weather_cache"] = cache

        return {
            "status": "success",
            "source": "live_api",
            **weather_data
        }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Weather service timed out. Try again."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }
    
def calculate(
    expression: str,
    tool_context: ToolContext
) -> dict:
    """Evaluates a mathematical expression and returns the result.

    Handles arithmetic operators: +, -, *, /, ** (power),
    and parentheses for grouping. Saves result to session
    so the user can reference it in follow-up calculations.

    Args:
        expression: A mathematical expression as a string.
                    Examples: "2 + 2", "(10 * 3) / 4", "2 ** 8"

    Returns:
        Dictionary with the evaluated result and history count.
    """
    # ── Input validation ──────────────────────────────────────
    # Whitelist only safe mathematical characters
    # This prevents code injection via eval()
    allowed = set("0123456789 +-*/().**")
    if not all(c in allowed for c in expression):
        return {
            "status": "error",
            "message": (
                "Expression contains invalid characters. "
                "Use only numbers and operators: + - * / ** ( )"
            )
        }

    try:
        # ── Evaluate ──────────────────────────────────────────
        # eval() is safe here because we validated characters above
        result = eval(expression)

        # ── Update state ──────────────────────────────────────
        # Keep a running history — last 10 calculations only
        history = tool_context.state.get("calc_history", [])
        entry = {
            "expression": expression,
            "result": result,
            "time": datetime.datetime.now().strftime("%H:%M:%S")
        }
        history.append(entry)
        tool_context.state["calc_history"] = history[-10:]

        # last_result enables chained calculations:
        # "calculate 500 * 1.08"  → last_result = 540.0
        # "now add 200 to that"   → agent reads last_result from state
        tool_context.state["last_result"] = result

        return {
            "status": "success",
            "expression": expression,
            "result": result,
            "history_count": len(history)
        }

    except ZeroDivisionError:
        return {
            "status": "error",
            "message": "Cannot divide by zero."
        }
    except SyntaxError:
        return {
            "status": "error",
            "message": (
                f"Invalid expression syntax: '{expression}'. "
                f"Check your operators and parentheses."
            )
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not evaluate: {str(e)}"
        }
    
def save_note(
    title: str,
    content: str,
    tool_context: ToolContext
) -> dict:
    """Saves a note to session memory for later recall.

    Stores any text content under a short title so the user
    can retrieve it later in the conversation. Overwrites
    a note with the same title if it already exists.

    Args:
        title: Short descriptive label for the note.
               Examples: "meeting agenda", "shopping list",
               "research findings", "task list"
        content: The full text content to save as the note.

    Returns:
        Dictionary confirming the note was saved.
    """
    notes = tool_context.state.get("notes", {})
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    # Normalize title for consistent key lookup
    # "Meeting Agenda" and "meeting agenda" find the same note
    title_key = title.lower().strip()

    notes[title_key] = {
        "title": title,
        "content": content,
        "saved_at": timestamp,
        "word_count": len(content.split())
    }

    tool_context.state["notes"] = notes

    return {
        "status": "success",
        "message": f"Note saved: '{title}'",
        "total_notes": len(notes),
        "word_count": notes[title_key]["word_count"]
    } 

def get_notes(tool_context: ToolContext) -> dict:
    """Retrieves all notes saved in this session.

    Returns all previously saved notes with their titles,
    content, timestamps, and word counts. Use when the
    user asks to see, recall, or review their notes.

    Returns:
        Dictionary with all saved notes and their details.
    """
    notes = tool_context.state.get("notes", {})

    if not notes:
        return {
            "status": "success",
            "message": (
                "No notes saved yet in this session. "
                "Ask me to save something and I will remember it."
            ),
            "notes": [],
            "count": 0
        }

    # Return as a list sorted by save time for easy reading
    note_list = sorted(
        notes.values(),
        key=lambda n: n["saved_at"]
    )

    return {
        "status": "success",
        "count": len(note_list),
        "notes": note_list
    }

# ─────────────────────────────────────────────
# ROOT AGENT — coordinator
# Holds custom tools directly + wraps specialists
# via AgentTool for delegation
# ─────────────────────────────────────────────

root_agent = Agent(
    model=FAST_MODEL,
    name="personal_assistant",
    description=(
        "A personal assistant that handles research via web search, "
        "calculations, note-taking, and weather lookups in one "
        "conversation. Delegates web search and code execution to "
        "specialist agents."
    ),
    instruction="""
You are Alex, a personal assistant that helps with research,
calculations, notes, and weather — all in one conversation.

[YOUR TOOLS AND WHEN TO USE EACH ONE]

DIRECT TOOLS — use these yourself immediately:
  get_weather  → any question about weather in a city
  calculate    → any arithmetic, math expression, or calculation
  save_note    → when user asks you to remember, save, or note
                 something down
  get_notes    → when user asks to see, recall, or review notes

DELEGATE TO SPECIALISTS — route these requests:
  search_agent → current events, news, factual research,
                 information about people, companies, topics
                 anything needing up-to-date web information
  code_agent   → complex computations, data analysis,
                 visualizations, algorithm demonstrations,
                 anything needing actual Python code to run

[ROUTING RULES — read carefully]

1. ALWAYS use get_weather for weather — never ask search_agent
   for weather, that wastes a full web search

2. ALWAYS use calculate for simple math — only delegate to
   code_agent when the problem needs actual code or visualization

3. For research: delegate to search_agent with a DETAILED
   request — tell it exactly what angles to cover, what
   data you need, and what format to return findings in

4. For notes: save_note immediately when user says anything
   like "remember this", "make a note", "save that",
   "don't forget" — no confirmation needed, just save it

5. CHAIN TOOLS when it makes sense:
   "Research solar panels and save the key findings as a note"
   → Step 1: delegate to search_agent
   → Step 2: save_note with the findings
   → Step 3: confirm both actions to user
   [HOW TO DELEGATE TO SPECIALISTS]

When calling search_agent, give it a rich, specific request:
  POOR:  "Search for electric cars"
  GOOD:  "Search for the current state of electric vehicle
          adoption in 2025 — cover: market share percentages,
          top selling models, charging infrastructure growth,
          and key challenges. Run at least 2 searches from
          different angles."

When calling code_agent, give it precise specs:
  POOR:  "Calculate compound interest"
  GOOD:  "Write and run Python to calculate compound interest
          for principal=$10000, rate=7%, years=20,
          compounded monthly. Print a year-by-year breakdown
          and the final amount. Show the formula used."

The quality of your delegation request directly determines
the quality of the specialist's output.

[STATE AND MEMORY AWARENESS]

You have access to session state through your tools.
Use this awareness naturally in conversation:

- After a calculation, you know the last_result — reference it:
  "That gives us 540. Want me to calculate tax on that?"

- After saving a note, reference it later:
  "I saved that under 'meeting notes' — want me to add to it?"

- Weather is cached — tell the user if you're using a cached
  result: "Based on what I checked earlier this session..."

- Calculation history exists — offer to show it:
  "I've done 3 calculations this session. Want a summary?"

[RESPONSE STYLE]
- Conversational and warm — you are an assistant, not a robot
- After tool calls, synthesize the result in plain English
- For research results, present findings clearly — do not
  just dump the raw search output
- For calculations, always state the result prominently
  then explain what it means if context helps
- Keep responses focused — do not over-explain

[SCOPE]
You handle: research, math, notes, weather.
For anything outside this scope, say:
"I am best at research, calculations, notes, and weather.
I can help you with any of those — what would you like?"
""",
tools=[
        # ── Specialist agents wrapped as tools ──────────────
        # AgentTool uses each agent's description to build
        # the schema the root LLM reads for routing decisions
        AgentTool(agent=search_agent),
        AgentTool(agent=code_agent),

        # ── Custom Python functions ──────────────────────────
        # Safe to coexist — no built-in tool constraint here
        get_weather,
        calculate,
        save_note,
        get_notes,
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=ROOT_TEMP,    # 0.3 — flexible enough for varied
                                  # user intents, consistent enough
                                  # for reliable tool routing
        max_output_tokens=4096,   # Higher than shopping agent —
                                  # research summaries can be long
    ),
)