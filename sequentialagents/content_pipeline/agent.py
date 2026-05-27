from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="greeter",
    model="gemini-2.5-flash",   # ← was gemini-2.0-flash
    description="A friendly agent that greets users and asks how it can help.",
    instruction=(
        "You are Greeter, a warm and concise assistant. "
        "When the user says hello, greet them by name if they give one, "
        "and ask one specific question about what they need help with today. "
        "Keep responses under 3 sentences."
    ),
)