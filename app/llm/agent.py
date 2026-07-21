from app.config import settings


def ask(question: str, history: list[dict] | None = None) -> dict:
    """Dispatch to the configured LLM provider (settings.llm_provider: 'groq' or 'anthropic')."""
    if settings.llm_provider == "anthropic":
        from app.llm.anthropic_agent import ask as ask_anthropic

        return ask_anthropic(question, history=history)

    from app.llm.groq_agent import ask as ask_groq

    return ask_groq(question, history=history)
