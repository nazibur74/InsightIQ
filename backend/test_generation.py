
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL_NAME = "gemini-3.5-flash-lite"

try:
    print(f"Testing {MODEL_NAME}...")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents="Reply with exactly: InsightIQ AI connection successful."
    )

    print("\nGemini response:")
    print(response.text)

except Exception as error:
    print("\nGemini request failed:")
    print(error)
