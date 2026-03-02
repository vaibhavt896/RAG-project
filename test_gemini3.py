import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content="Hello world",
        task_type="retrieval_document"
    )
    print("\nSuccess with models/gemini-embedding-001!")
    print(f"Embedding length: {len(result['embedding'])}")
except Exception as e:
    print(f"\nError: {e}")
