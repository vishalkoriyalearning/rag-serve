import openai
from google import genai
from configs.llm import OPENAI_API_KEY, OPENAI_MODEL, GEMINI_API_KEY, GEMINI_MODEL
import requests
import json

openai.api_key = OPENAI_API_KEY

def call_openai(prompt: str, api_key: str = None):
    try:
        if api_key:
            openai.api_key = api_key
        resp = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": "Answer with context:"},
                      {"role": "user", "content": prompt}],
            max_tokens=512
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"OpenAI error: {str(e)}"
    
def call_gemini(prompt: str, api_key: str = None):
    # Placeholder for Gemini API call
    try:
        client = genai.Client(api_key=api_key) if api_key else genai.Client()
        response = client.models.generate_content(
            model=GEMINI_MODEL if GEMINI_MODEL else "gemini-3-flash-preview",
            contents="Explain how AI works in a few words",
        )
        return(response.text)
    except Exception as e:
        return f"Gemini error: {str(e)}"


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


