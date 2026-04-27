from google.adk.agents import LlmAgent
from google.genai import types
from pydantic import BaseModel, Field


class Lesson(BaseModel):
    """Structured output schema for a tutoring response."""
    topic: str = Field(description="The topic being explained")
    explanation: str = Field(description="A clear explanation, 3-5 sentences")
    example: str = Field(description="A concrete example illustrating the concept")
    next_step: str = Field(description="What the learner should try next")
    difficulty: str = Field(description="beginner, intermediate, or advanced")


root_agent = LlmAgent(
    name="tutor",
    model="gemini-2.5-flash",
    description="A patient tutor that explains concepts with examples.",
    instruction=(
        "You are TutorBot, a clear and patient teacher. "
        "Explain whatever concept the user asks about. "
        "Always include one concrete example and one suggested next step. "
        "Match your depth to a learner who is at the intermediate level. "
        "Always include 'difficulty' as one of: beginner, intermediate, advanced."
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,         # lower = more focused, less creative
        max_output_tokens=600,
        top_p=0.95,
    ),
    output_schema=Lesson,        # forces JSON matching the Pydantic model
    output_key="last_lesson",    # also saves the response into state
)