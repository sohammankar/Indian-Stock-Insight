import json

import anthropic

from app.config import settings
from app.llm.tools import TOOL_DEFINITIONS, execute_tool

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """You are a research assistant for the Indian stock market (NSE).
Answer questions by calling the available tools to pull live prices, corporate
announcements, shareholding patterns, and bulk deals - then synthesize a clear,
grounded answer. Cite specific numbers and dates from the tool results. If the
tools don't have enough information to answer confidently, say so instead of
guessing. Keep answers concise and in plain language for a retail investor."""

MAX_TOOL_ROUNDS = 5


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def ask(question: str) -> dict:
    """Run the tool-calling loop for a single question. Returns the final answer text
    plus a trace of which tools were called, for transparency/debugging."""
    client = _client()
    messages = [{"role": "user", "content": question}]
    trace = []

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            text = "".join(block.text for block in response.content if block.type == "text")
            return {"answer": text, "trace": trace}

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            try:
                result = execute_tool(block.name, block.input)
                content = json.dumps(result, default=str)[:8000]
            except Exception as e:
                content = f"Error: {e}"
            trace.append({"tool": block.name, "input": block.input})
            tool_results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": content}
            )

        messages.append({"role": "user", "content": tool_results})

    return {"answer": "Reached max tool-call rounds without a final answer.", "trace": trace}
