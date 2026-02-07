import os

# Keep unit tests hermetic:
# - Force LOCAL embeddings so we don't require OpenAI credentials for retrieval.
# - Blank hosted-provider keys so we don't accidentally make external API calls.
#
# This must run at import time (test collection) so dotenv won't overwrite it.
os.environ["PLATFORM"] = "LOCAL"
os.environ["OPENAI_API_KEY"] = ""
os.environ["GEMINI_API_KEY"] = ""
