import openai
from configs.llm import OPENAI_API_KEY, OPENAI_MODEL

import requests
import json


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
        print(e)
        return None



OLLAMA_HOST = "http://localhost:11434"

def call_ollama(prompt: str, model: str = "llama3.2:1b"):
    url = f"{OLLAMA_HOST}/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        res = requests.post(url, json=payload, stream=True)
        res.raise_for_status()

        full_response = ""
        for line in res.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                full_response += data.get("response", "")

        return full_response

    except Exception as e:
        return f"Ollama error: {str(e)}"


