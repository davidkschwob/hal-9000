# helper
def get_llm_client():
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError("CRITICAL: GROQ_API_KEY is missing")

    model = os.environ.get("GROQ_MODEL")
    if not model:
        raise ValueError("CRITICAL: GROQ_MODEL is missing")

    # instantiate using dotenv-specific api key and model name
    return Groq(api_key=api_key)
