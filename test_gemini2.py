import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

for m in genai.list_models():
    if 'embedContent' in m.supported_generation_methods:
        print(f"Supported embedding model: {m.name}")

try:
    result = genai.embed_content(
        model="models/embedding-001",
        content="Hello world",
        task_type="retrieval_document"
    )
    print("\nSuccess with models/embedding-001!")
except Exception as e:
    print(f"\nError with models/embedding-001: {e}")

try:
    result = genai.embed_content(
        model="models/text-embedding-004",
        content="Hello world",
        task_type="retrieval_document"
    )
    print("\nSuccess with models/text-embedding-004!")
except Exception as e:
    print(f"\nError with models/text-embedding-004: {e}")
