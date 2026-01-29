import openai
from configs.llm import OPENAI_API_KEY, OPENAI_MODEL

import requests
import json
import os


openai.api_key = OPENAI_API_KEY

def call_openai(prompt: str):
    try:
        resp = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": "Answer with context:"},
                      {"role": "user", "content": prompt}],
            max_tokens=512
        )
        return resp.choices[0].message.content
    except Exception as e:
        # Log error and fallback
        return None



OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")

def call_ollama(prompt: str, model: str = "llama3.2:1b"):
    url = f"{OLLAMA_HOST}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        res = requests.post(url, json=payload)
        res.raise_for_status()
        data = res.json()
        return data.get("response", "")
    except Exception as e:
        return f"Ollama error: {str(e)}"

