import math
from google.adk.agents import Agent
from google.adk.tools import ToolContext


# ─────────────────────────────────────────────
# SECTION 1: BASIC MATH TOOLS
# ─────────────────────────────────────────────

def calculate(
    expression: str,
    tool_context: ToolContext
) -> dict:
    """Evaluates a mathematical expression safely.

    Handles basic arithmetic including +, -, *, /, ** (power),
    and parentheses for grouping. Also tracks calculation history.

    Args:
        expression: A math expression as a string.
                    Examples: "2 + 2", "10 * (3 + 4)", "2 ** 8"

    Returns:
        Dictionary with the result and updated history.
    """
    # Only allow safe mathematical characters
    allowed_chars = set("0123456789+-*/.() ")
    if not all(c in allowed_chars for c in expression):
        return {
            "status": "error",
            "message": (
                f"Expression contains invalid characters. "
                f"Only numbers and operators (+, -, *, /, **) are allowed."
            )
        }

    try:
        result = eval(expression)  # safe because we validated chars above

        # Track history using ToolContext state
        history = tool_context.state.get("calc_history", [])
        history.append({"expression": expression, "result": result})

        # Keep last 10 calculations only
        tool_context.state["calc_history"] = history[-10:]
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
            "message": "Division by zero is not allowed."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Could not evaluate expression: {str(e)}"
        }


def get_calculation_history(tool_context: ToolContext) -> dict:
    """Retrieves the history of all calculations in this session.

    Returns all previous expressions and their results,
    up to the last 10 calculations.

    Returns:
        Dictionary with the full calculation history.
    """
    history = tool_context.state.get("calc_history", [])

    if not history:
        return {
            "status": "success",
            "message": "No calculations yet in this session.",
            "history": []
        }

    return {
        "status": "success",
        "count": len(history),
        "history": history,
        "last_result": tool_context.state.get("last_result")
    }


# ─────────────────────────────────────────────
# SECTION 2: SCIENTIFIC MATH TOOLS
# ─────────────────────────────────────────────

def calculate_percentage(
    value: float,
    percentage: float,
    operation: str = "of"
) -> dict:
    """Performs percentage calculations.

    Supports finding a percentage of a number, what percentage
    one number is of another, and percentage increase or decrease.

    Args:
        value: The base number for the calculation.
        percentage: The percentage value (e.g., 20 for 20%).
        operation: Type of percentage operation. Options:
                   "of"       → what is X% of value? (default)
                   "what"     → value is what % of percentage?
                   "increase" → increase value by X%
                   "decrease" → decrease value by X%

    Returns:
        Dictionary with the percentage calculation result.
    """
    try:
        if operation == "of":
            result = (percentage / 100) * value
            explanation = f"{percentage}% of {value} = {result}"

        elif operation == "what":
            if percentage == 0:
                return {
                    "status": "error",
                    "message": "Cannot calculate percentage of zero."
                }
            result = (value / percentage) * 100
            explanation = f"{value} is {result:.2f}% of {percentage}"

        elif operation == "increase":
            result = value * (1 + percentage / 100)
            explanation = f"{value} increased by {percentage}% = {result}"

        elif operation == "decrease":
            result = value * (1 - percentage / 100)
            explanation = f"{value} decreased by {percentage}% = {result}"

        else:
            return {
                "status": "error",
                "message": (
                    f"Unknown operation '{operation}'. "
                    f"Use: 'of', 'what', 'increase', or 'decrease'."
                )
            }

        return {
            "status": "success",
            "result": round(result, 4),
            "explanation": explanation
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def solve_statistics(numbers: str) -> dict:
    """Calculates statistical measures for a list of numbers.

    Computes mean, median, mode, standard deviation, min, max,
    and range for the provided dataset.

    Args:
        numbers: Comma-separated list of numbers as a string.
                 Example: "4, 8, 15, 16, 23, 42"

    Returns:
        Dictionary with all statistical measures.
    """
    try:
        # Parse the comma-separated string into a list of floats
        num_list = [float(x.strip()) for x in numbers.split(",")]

        if len(num_list) < 2:
            return {
                "status": "error",
                "message": "Please provide at least 2 numbers."
            }

        n = len(num_list)
        mean = sum(num_list) / n
        sorted_nums = sorted(num_list)

        # Median calculation
        mid = n // 2
        median = (
            sorted_nums[mid] if n % 2 != 0
            else (sorted_nums[mid - 1] + sorted_nums[mid]) / 2
        )

        # Standard deviation
        variance = sum((x - mean) ** 2 for x in num_list) / n
        std_dev = math.sqrt(variance)

        # Mode (most frequent value)
        frequency = {}
        for num in num_list:
            frequency[num] = frequency.get(num, 0) + 1
        mode = max(frequency, key=frequency.get)

        return {
            "status": "success",
            "count": n,
            "mean": round(mean, 4),
            "median": round(median, 4),
            "mode": mode,
            "std_deviation": round(std_dev, 4),
            "minimum": min(num_list),
            "maximum": max(num_list),
            "range": max(num_list) - min(num_list),
            "sum": sum(num_list)
        }

    except ValueError:
        return {
            "status": "error",
            "message": (
                "Could not parse numbers. "
                "Please use comma-separated values like: 1, 2, 3, 4"
            )
        }


# ─────────────────────────────────────────────
# SECTION 3: UNIT CONVERSION TOOLS
# ─────────────────────────────────────────────

def convert_units(
    value: float,
    from_unit: str,
    to_unit: str
) -> dict:
    """Converts a value between different units of measurement.

    Supports length (km, m, cm, mm, miles, feet, inches),
    weight (kg, g, lb, oz), temperature (celsius, fahrenheit, kelvin),
    and volume (liters, ml, gallons, cups).

    Args:
        value: The numeric value to convert.
        from_unit: The unit to convert from (e.g., "km", "celsius", "kg").
        to_unit: The unit to convert to (e.g., "miles", "fahrenheit", "lb").

    Returns:
        Dictionary with the converted value and conversion details.
    """

    # Normalize to lowercase for consistent matching
    from_unit = from_unit.lower().strip()
    to_unit = to_unit.lower().strip()

    # ── LENGTH (base unit: meters) ──
    length_to_meters = {
        "km": 1000, "kilometers": 1000,
        "m": 1, "meters": 1,
        "cm": 0.01, "centimeters": 0.01,
        "mm": 0.001, "millimeters": 0.001,
        "miles": 1609.344, "mile": 1609.344,
        "feet": 0.3048, "ft": 0.3048, "foot": 0.3048,
        "inches": 0.0254, "inch": 0.0254, "in": 0.0254,
        "yards": 0.9144, "yard": 0.9144, "yd": 0.9144,
    }

    # ── WEIGHT (base unit: kilograms) ──
    weight_to_kg = {
        "kg": 1, "kilograms": 1, "kilogram": 1,
        "g": 0.001, "grams": 0.001, "gram": 0.001,
        "lb": 0.453592, "lbs": 0.453592, "pounds": 0.453592, "pound": 0.453592,
        "oz": 0.0283495, "ounces": 0.0283495, "ounce": 0.0283495,
        "tonne": 1000, "ton": 1000,
    }

    # ── VOLUME (base unit: liters) ──
    volume_to_liters = {
        "l": 1, "liters": 1, "liter": 1, "litre": 1,
        "ml": 0.001, "milliliters": 0.001, "milliliter": 0.001,
        "gallons": 3.78541, "gallon": 3.78541, "gal": 3.78541,
        "cups": 0.236588, "cup": 0.236588,
        "fl oz": 0.0295735, "fluid ounces": 0.0295735,
        "pint": 0.473176, "pints": 0.473176,
        "quart": 0.946353, "quarts": 0.946353,
    }

    try:
        # ── TEMPERATURE (special case — not linear conversion) ──
        temp_units = {"celsius", "fahrenheit", "kelvin", "c", "f", "k"}
        if from_unit in temp_units or to_unit in temp_units:
            # Normalize aliases
            from_unit = {"c": "celsius", "f": "fahrenheit", "k": "kelvin"}.get(from_unit, from_unit)
            to_unit   = {"c": "celsius", "f": "fahrenheit", "k": "kelvin"}.get(to_unit, to_unit)

            if from_unit == to_unit:
                return {"status": "success", "result": value,
                        "from": f"{value} {from_unit}", "to": f"{value} {to_unit}"}

            # Convert to Celsius first
            if from_unit == "fahrenheit":
                celsius = (value - 32) * 5 / 9
            elif from_unit == "kelvin":
                celsius = value - 273.15
            else:
                celsius = value

            # Convert Celsius to target
            if to_unit == "fahrenheit":
                result = celsius * 9 / 5 + 32
            elif to_unit == "kelvin":
                result = celsius + 273.15
            else:
                result = celsius

            return {
                "status": "success",
                "result": round(result, 4),
                "from": f"{value} {from_unit}",
                "to": f"{round(result, 4)} {to_unit}"
            }

        # ── LENGTH conversion ──
        if from_unit in length_to_meters and to_unit in length_to_meters:
            meters = value * length_to_meters[from_unit]
            result = meters / length_to_meters[to_unit]
            return {
                "status": "success",
                "result": round(result, 6),
                "from": f"{value} {from_unit}",
                "to": f"{round(result, 6)} {to_unit}",
                "category": "length"
            }

        # ── WEIGHT conversion ──
        if from_unit in weight_to_kg and to_unit in weight_to_kg:
            kg = value * weight_to_kg[from_unit]
            result = kg / weight_to_kg[to_unit]
            return {
                "status": "success",
                "result": round(result, 6),
                "from": f"{value} {from_unit}",
                "to": f"{round(result, 6)} {to_unit}",
                "category": "weight"
            }

        # ── VOLUME conversion ──
        if from_unit in volume_to_liters and to_unit in volume_to_liters:
            liters = value * volume_to_liters[from_unit]
            result = liters / volume_to_liters[to_unit]
            return {
                "status": "success",
                "result": round(result, 6),
                "from": f"{value} {from_unit}",
                "to": f"{round(result, 6)} {to_unit}",
                "category": "volume"
            }

        # ── Cross-category or unknown units ──
        return {
            "status": "error",
            "message": (
                f"Cannot convert '{from_unit}' to '{to_unit}'. "
                f"They may be different categories (e.g., length vs weight) "
                f"or unsupported units."
            )
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ─────────────────────────────────────────────
# AGENT DEFINITION
# ─────────────────────────────────────────────

root_agent = Agent(
    model="gemini-flash-latest",

    name="calculator_agent",

    description=(
        "A precise calculator and unit converter that handles arithmetic, "
        "percentages, statistics, and unit conversions across length, "
        "weight, temperature, and volume. Tracks calculation history."
    ),

    instruction="""
You are CalcBot, an expert calculator and unit converter assistant.

[TOOLS AVAILABLE]
- calculate: Evaluate any math expression. Use for arithmetic, algebra, powers.
- calculate_percentage: Handle percentage operations (find %, increase, decrease).
- solve_statistics: Compute mean, median, mode, std dev for a dataset.
- get_calculation_history: Retrieve all calculations done in this session.
- convert_units: Convert between length, weight, temperature, and volume units.

[BEHAVIOR RULES]
1. Always use a tool — never do math in your head or guess results
2. For multi-step problems, break them into individual tool calls
3. Show your working — explain what you calculated and why
4. Round results to a sensible number of decimal places for context
5. If a unit is ambiguous (e.g. "ton"), ask the user to clarify

[RESPONSE FORMAT]
After each calculation:
- State the result clearly and prominently
- Add a brief plain-English explanation of what it means
- For unit conversions, always show both the original and converted values

[SCOPE]
You handle math and unit conversions only. For anything else say:
"I am CalcBot — a specialist in calculations and conversions. 
What would you like me to calculate?"
""",

    tools=[
        calculate,
        calculate_percentage,
        solve_statistics,
        convert_units,
        get_calculation_history,
    ],
)