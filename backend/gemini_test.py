from app.services.gemini_service import generate_ai_response

response = generate_ai_response(
    "Say hello to InsightIQ in one sentence."
)

print("\nGemini response:")
print(response)