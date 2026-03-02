import os
import sys
sys.path.insert(0, '/Users/vaibhav/Downloads/RAG project')
from dotenv import load_dotenv
load_dotenv('/Users/vaibhav/Downloads/RAG project/.env')

os.environ['EMBEDDING_MODEL'] = 'models/gemini-embedding-001'
os.environ['LLM_MODEL'] = 'gemini-1.5-flash'

print("Step 1: Testing LLM (generate_answer)...")
try:
    from src.generation.llm import generate_answer
    result = generate_answer(
        question="What is Bitcoin?",
        context="[1] Source: bitcoin.pdf\nBitcoin is a peer-to-peer electronic cash system."
    )
    print(f"LLM Success! Answer: {result['answer'][:100]}")
except Exception as e:
    print(f"LLM ERROR: {e}")

print("\nStep 2: Testing query expansion...")
try:
    from src.generation.llm import expand_query
    expansions = expand_query("What is Bitcoin?")
    print(f"Expansions: {expansions}")
except Exception as e:
    print(f"Expand query ERROR: {e}")

print("\nStep 3: Testing retriever search...")
try:
    from src.retrieval.hybrid import HybridRetriever
    retriever = HybridRetriever()
    results = retriever.search("What is Bitcoin?", top_k=3)
    print(f"Retriever results: {len(results)} found")
    if results:
        print(f"First result preview: {results[0]['content'][:100]}")
except Exception as e:
    print(f"Retriever ERROR: {e}")
