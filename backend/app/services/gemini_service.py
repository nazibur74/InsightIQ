
import os

from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Check your backend .env file."
    )

# Initialize Gemini client
client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.5-flash-lite"


import time

def generate_ai_response(prompt: str) -> str:
    """Generate a response using Gemini with retry handling."""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response.")

            return response.text

        except Exception as error:
            error_message = str(error)

            if "503" in error_message and attempt < 2:
                wait_time = 5 * (attempt + 1)
                print(
                    f"Gemini is temporarily unavailable. "
                    f"Retrying in {wait_time} seconds..."
                )
                time.sleep(wait_time)
                continue

            raise RuntimeError(
                f"Gemini API request failed: {error_message}"
            ) from error
