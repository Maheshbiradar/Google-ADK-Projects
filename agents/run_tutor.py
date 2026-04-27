import asyncio
from dotenv import load_dotenv
load_dotenv("greeter/.env")  # any agent's .env works

from google.adk.runners import InMemoryRunner
from google.genai import types
from tutor.agent import root_agent


async def main():
    runner = InMemoryRunner(agent=root_agent, app_name="tutor_app")
    session = await runner.session_service.create_session(
        app_name="tutor_app", user_id="mahesh"
    )

    message = types.Content(
        role="user",
        parts=[types.Part(text="Explain Python decorators.")],
    )

    async for event in runner.run_async(
        user_id="mahesh",
        session_id=session.id,
        new_message=message,
    ):
        if event.is_final_response() and event.content:
            print(event.content.parts[0].text)


asyncio.run(main())