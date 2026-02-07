import openai
from google import genai
from configs.llm import OPENAI_API_KEY, OPENAI_MODEL, GEMINI_API_KEY, GEMINI_MODEL

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
    
def call_gemini(prompt: str, api_key: str = GEMINI_API_KEY):
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


