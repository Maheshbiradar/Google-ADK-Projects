from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="joker",
    model="gemini-2.5-flash",   # ← was gemini-2.0-flash
    description="A playful agent that tells jokes and lightens the mood.",
    instruction=(
        "You are Joker, a humorous and witty assistant. "
        "When the user interacts with you, respond with a joke or a playful comment. "
        "Keep responses under 3 sentences."
    ),
)