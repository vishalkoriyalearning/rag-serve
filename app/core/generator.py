import openai
from subprocess import Popen, PIPE
from configs.llm import OPENAI_API_KEY, OPENAI_MODEL, OLLAMA_MODEL

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

def call_ollama(prompt: str):
    # Simple shell call to Ollama CLI
    process = Popen(
        ["ollama", "generate", OLLAMA_MODEL, prompt], stdout=PIPE, stderr=PIPE
    )
    out, _ = process.communicate()
    return out.decode("utf-8")
