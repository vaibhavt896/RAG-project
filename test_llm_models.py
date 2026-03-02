import os
import sys
sys.path.insert(0, '/Users/vaibhav/Downloads/RAG project')
from dotenv import load_dotenv
load_dotenv('/Users/vaibhav/Downloads/RAG project/.env')

import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Available generative models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  - {m.name}")
