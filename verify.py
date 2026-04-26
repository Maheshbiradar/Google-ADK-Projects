import os
from dotenv import load_dotenv
load_dotenv()

import google.adk
print("ADK version:", google.adk.__version__)
print("API key loaded:", bool(os.getenv("GOOGLE_API_KEY")))