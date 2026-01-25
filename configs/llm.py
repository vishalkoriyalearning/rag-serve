import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2")  # GPT-5.2 as primary
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
