import os
import requests
from google.adk.agents import Agent

# ─────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────

def get_weather(city: str) -> dict:
    """Retrieves current weather data for a given city.

    Fetches real-time temperature, humidity, wind speed,
    and weather conditions from the OpenWeatherMap API.

    Args:
        city: The name of the city to get weather for.
              Examples: "London", "New York", "Tokyo"

    Returns:
        A dictionary with weather data or an error message.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "message": "Weather API key not configured."
        }

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric"   # Celsius — change to "imperial" for Fahrenheit
        }
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 404:
            return {
                "status": "error",
                "message": f"City '{city}' not found. Please check the spelling."
            }

        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"Weather service error (code {response.status_code})."
            }

        data = response.json()

        return {
            "status": "success",
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature_c": round(data["main"]["temp"], 1),
            "feels_like_c": round(data["main"]["feels_like"], 1),
            "humidity_percent": data["main"]["humidity"],
            "condition": data["weather"][0]["description"].title(),
            "wind_speed_kmh": round(data["wind"]["speed"] * 3.6, 1),
            "visibility_km": round(data.get("visibility", 0) / 1000, 1),
        }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Weather service timed out. Please try again."
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "message": "Could not connect to weather service. Check your internet."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def compare_weather(city1: str, city2: str) -> dict:
    """Compares the current weather between two cities.

    Fetches weather for both cities and returns a side-by-side
    comparison including which city is warmer and more humid.

    Args:
        city1: Name of the first city to compare.
        city2: Name of the second city to compare.

    Returns:
        A dictionary with weather data for both cities and comparison.
    """
    weather1 = get_weather(city1)
    weather2 = get_weather(city2)

    if weather1["status"] == "error":
        return weather1
    if weather2["status"] == "error":
        return weather2

    warmer_city = (
        city1 if weather1["temperature_c"] >= weather2["temperature_c"]
        else city2
    )
    temp_diff = abs(
        weather1["temperature_c"] - weather2["temperature_c"]
    )

    return {
        "status": "success",
        "city1": weather1,
        "city2": weather2,
        "comparison": {
            "warmer_city": warmer_city,
            "temperature_difference_c": round(temp_diff, 1),
            "more_humid_city": (
                city1 if weather1["humidity_percent"] >= weather2["humidity_percent"]
                else city2
            ),
        }
    }


def get_weather_advice(city: str) -> dict:
    """Gets weather-based activity and clothing advice for a city.

    Fetches current weather and returns practical recommendations
    for what to wear and what activities are suitable.

    Args:
        city: The name of the city to get advice for.

    Returns:
        A dictionary with weather data and practical recommendations.
    """
    weather = get_weather(city)

    if weather["status"] == "error":
        return weather

    temp = weather["temperature_c"]
    condition = weather["condition"].lower()

    # Clothing advice based on temperature
    if temp >= 30:
        clothing = "Light clothing, sunglasses, and sunscreen. Stay hydrated!"
    elif temp >= 20:
        clothing = "T-shirt and light pants. Very comfortable weather."
    elif temp >= 10:
        clothing = "Light jacket or sweater recommended."
    elif temp >= 0:
        clothing = "Warm coat, scarf, and gloves advised."
    else:
        clothing = "Heavy winter coat, thermal layers, boots essential."

    # Activity advice based on conditions
    if "rain" in condition or "drizzle" in condition:
        activity = "Bring an umbrella. Good day for indoor activities."
    elif "storm" in condition or "thunder" in condition:
        activity = "Stay indoors if possible. Avoid outdoor activities."
    elif "snow" in condition:
        activity = "Great for skiing or snowball fights! Roads may be slippery."
    elif "clear" in condition or "sunny" in condition:
        activity = "Perfect for outdoor activities — parks, hiking, sightseeing!"
    elif "cloud" in condition:
        activity = "Mild conditions. Most outdoor activities are fine."
    else:
        activity = "Check conditions before heading out."

    return {
        "status": "success",
        "city": weather["city"],
        "temperature_c": temp,
        "condition": weather["condition"],
        "clothing_advice": clothing,
        "activity_advice": activity,
    }


# ─────────────────────────────────────────────
# AGENT DEFINITION
# ─────────────────────────────────────────────

root_agent = Agent(
    model="gemini-2.5-flash",

    name="weather_bot",

    description=(
        "Real-time weather assistant that retrieves current weather conditions, "
        "compares weather between cities, and gives practical clothing and "
        "activity advice based on weather data."
    ),

    instruction="""
You are WeatherBot, a friendly and precise weather assistant powered by 
real-time data.

[TOOLS AVAILABLE]
- get_weather: Get current weather for any city
- compare_weather: Compare weather between two cities side by side
- get_weather_advice: Get clothing and activity recommendations for a city

[BEHAVIOR RULES]
1. ALWAYS use a tool before answering any weather question — never guess
2. If a city returns an error, tell the user clearly and ask them to 
   check the spelling
3. Always mention temperatures in Celsius (°C)
4. Be conversational but precise — give numbers, not just vague descriptions
5. For comparisons, always tell the user which city is warmer and by how much

[OUTPUT FORMAT]
For single city weather, present it like this:
  📍 London, UK
  🌡️  Temperature: 12.0°C (feels like 9.5°C)
  🌤️  Condition: Overcast Clouds
  💧 Humidity: 78%
  💨 Wind: 18.0 km/h
  👁️  Visibility: 8.0 km

[BOUNDARIES]
Only answer weather-related questions. For anything else, respond:
"I'm WeatherBot — specialized in weather data! Ask me about any city's 
current weather, and I'll tell you exactly what's going on there."
""",

    tools=[get_weather, compare_weather, get_weather_advice],
)