from google.adk.agents import Agent
import datetime

def get_current_time() -> dict:
    """Returns the current date and time.
    
    Returns:
        A dictionary with the current date and time information.
    """
    now = datetime.datetime.now()
    return {
        "status": "success",
        "date": now.strftime("%A, %B %d, %Y"),
        "time": now.strftime("%I:%M %p"),
        "timezone": "local"
    }

def get_greeting(name: str) -> dict:
    """Returns a personalized greeting for the given name.
    
    Args:
        name: The name of the person to greet.
        
    Returns:
        A dictionary with the greeting message.
    """
    return {
        "status": "success",
        "greeting": f"Hello, {name}! Welcome to Google ADK. You're going to build amazing things today."
    }

root_agent = Agent(
    model="gemini-2.5-flash", 
    name='hello_agent',
    description='A friendly greeter agent that welcomes users by name.',
    instruction= (
    "You are a warm, enthusiastic assistant helping developers "
    "learn Google ADK. When someone tells you their name, use the get_greeting "
    "tool to greet them personally. For any other questions, answer helpfully "
    "and encourage their learning journey."
    ),
    tools=[get_greeting, get_current_time],
)