import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2")  # GPT-5.2 as primary

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")  # Gemini 2.5 Pro as primary
