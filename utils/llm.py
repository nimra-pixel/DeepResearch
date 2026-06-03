"""
LLM factory with automatic fallback chain on rate limit.
Chain: llama-3.3-70b-versatile → llama-3.1-8b-instant → gemma2-9b-it
"""
from utils.config import get_settings

GROQ_FALLBACK_CHAIN = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
    "llama3-8b-8192",
]


def get_llm(temperature: float = None, max_tokens: int = None):
    s = get_settings()
    temp = temperature if temperature is not None else s.TEMPERATURE
    tokens = max_tokens or s.MAX_TOKENS

    if s.LLM_PROVIDER == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=s.GROQ_MODEL,
            temperature=temp,
            max_tokens=tokens,
            groq_api_key=s.GROQ_API_KEY,
        )
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(
        model=s.ANTHROPIC_MODEL,
        temperature=temp,
        max_tokens=tokens,
        anthropic_api_key=s.ANTHROPIC_API_KEY,
    )


def invoke_with_fallback(messages: list, temperature: float = 0.2,
                          max_tokens: int = 2048) -> str:
    """
    Invoke LLM with automatic model fallback on rate limit (429).
    Returns response content string.
    """
    s = get_settings()
    if s.LLM_PROVIDER != "groq":
        llm = get_llm(temperature=temperature, max_tokens=max_tokens)
        return llm.invoke(messages).content

    from langchain_groq import ChatGroq
    import time

    # Try each model in fallback chain
    tried = []
    for model in GROQ_FALLBACK_CHAIN:
        tried.append(model)
        try:
            llm = ChatGroq(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                groq_api_key=s.GROQ_API_KEY,
            )
            resp = llm.invoke(messages)
            if model != s.GROQ_MODEL:
                print(f"[LLM] Used fallback model: {model}")
            return resp.content
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "rate_limit" in err_str.lower():
                print(f"[LLM] Rate limit on {model} — trying next model")
                time.sleep(1)
                continue
            elif "401" in err_str or "auth" in err_str.lower():
                raise ValueError("Invalid Groq API key — check your .env file") from e
            else:
                print(f"[LLM] Error on {model}: {e}")
                continue

    raise RuntimeError(
        f"All models rate-limited: {tried}. "
        "Wait ~20 minutes or upgrade at console.groq.com/settings/billing"
    )
