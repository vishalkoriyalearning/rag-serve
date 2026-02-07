from __future__ import annotations

import os

import requests
from google import genai
from openai import OpenAI

from configs.llm import OPENAI_API_KEY, OPENAI_MODEL, GEMINI_API_KEY, GEMINI_MODEL

_default_openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else OpenAI()


def call_openai(prompt: str, api_key: str | None = None) -> str:
    try:
        client = OpenAI(api_key=api_key) if api_key else _default_openai_client
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Answer with context:"},
                {"role": "user", "content": prompt},
            ],
            max_tokens=512,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        return f"OpenAI error: {str(e)}"


def call_gemini(prompt: str, api_key: str | None = GEMINI_API_KEY) -> str:
    try:
        client = genai.Client(api_key=api_key) if api_key else genai.Client()
        response = client.models.generate_content(
            model=GEMINI_MODEL if GEMINI_MODEL else "gemini-3-flash-preview",
            contents=prompt,
        )
        return response.text or ""
    except Exception as e:
        return f"Gemini error: {str(e)}"


def call_ollama(prompt: str, host: str | None = None, model: str | None = None) -> str:
    host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = model or os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    url = f"{host.rstrip('/')}/api/generate"

    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        res = requests.post(url, json=payload, timeout=120)
        res.raise_for_status()

        data = res.json()
        return data.get("response", "") or ""
    except Exception as e:
        return f"Ollama error: {str(e)}"


