from google.adk.agents import LlmAgent
from google.adk.tools import google_search

root_agent = LlmAgent(
    name="searcher",
    model="gemini-2.5-flash",
    description="Searches the web for up-to-date information.",
    instruction=(
        "You are a research assistant. For any factual question that may "
        "depend on recent information, use google_search. Cite the sources "
        "you used at the end of your reply."
    ),
    tools=[google_search],
)