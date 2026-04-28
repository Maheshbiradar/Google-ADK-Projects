from datetime import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext


# ---------- Function Tool 1 ----------
def get_weather(city: str) -> dict:
    """Return the current weather for a given city.

    Use this whenever the user asks about weather, temperature, or
    conditions in a specific city. Always pass the city name as a string.

    Args:
        city: The name of the city, e.g. "Bangalore" or "New York".

    Returns:
        A dict with keys: status ("success" or "error"), report (str on success),
        error_message (str on error).
    """
    # Mock data — Day 12 we'll wire this to a real API.
    weather_db = {
        "bangalore": "28°C and partly cloudy.",
        "new york": "12°C and raining.",
        "london": "8°C and overcast.",
        "tokyo": "18°C and sunny.",
    }
    key = city.strip().lower()
    if key in weather_db:
        return {"status": "success", "report": f"The weather in {city} is {weather_db[key]}"}
    return {
        "status": "error",
        "error_message": f"No weather data available for {city}.",
    }


# ---------- Function Tool 2 ----------
def get_current_time(city: str) -> dict:
    """Return the current local time for a given city.

    Args:
        city: The city name, e.g. "Bangalore".

    Returns:
        A dict with keys: status, report (on success), error_message (on error).
    """
    tz_map = {
        "bangalore": "Asia/Kolkata",
        "new york": "America/New_York",
        "london": "Europe/London",
        "tokyo": "Asia/Tokyo",
    }
    key = city.strip().lower()
    if key not in tz_map:
        return {"status": "error", "error_message": f"No timezone for {city}."}
    now = datetime.now(ZoneInfo(tz_map[key]))
    return {
        "status": "success",
        "report": f"The current time in {city} is {now.strftime('%Y-%m-%d %H:%M:%S')}.",
    }


# ---------- Function Tool 3: with ToolContext ----------
def remember_last_city(city: str, tool_context: ToolContext) -> dict:
    """Save the city the user is asking about so we can default to it later.

    Call this after the user mentions a city, so subsequent questions
    without a city can fall back to it.

    Args:
        city: The city to remember.

    Returns:
        A dict confirming what was stored.
    """
    tool_context.state["last_city"] = city
    return {"status": "success", "stored": city}


# ---------- The Agent ----------
root_agent = LlmAgent(
    name="weather_bot",
    model="gemini-2.5-flash",
    description="Tells the weather and current time for major cities.",
    instruction=(
        "You are WeatherBot. When the user asks about weather or time, "
        "call the appropriate tool. After you learn the city the user cares "
        "about, call remember_last_city to store it. If the user asks a "
        "follow-up without naming a city, use the previously stored city "
        "from state if available: {last_city?}."
    ),
    tools=[get_weather, get_current_time, remember_last_city],
)