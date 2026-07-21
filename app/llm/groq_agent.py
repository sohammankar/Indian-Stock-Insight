import json

from groq import Groq

from app.config import settings
from app.llm.tools import TOOL_DEFINITIONS, execute_tool

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a research assistant for the Indian stock market (NSE).
Answer questions by calling the available tools to pull live prices, corporate
announcements, shareholding patterns, and bulk deals - then synthesize a clear,
grounded answer. Cite specific numbers and dates from the tool results. If the
tools don't have enough information to answer confidently, say so instead of
guessing. Keep answers concise and in plain language for a retail investor."""

MAX_TOOL_ROUNDS = 5


def _to_openai_tools() -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            },
        }
        for t in TOOL_DEFINITIONS
    ]


def _client() -> Groq:
    return Groq(api_key=settings.groq_api_key)


def ask(question: str) -> dict:
    client = _client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    trace = []
    tools = _to_openai_tools()

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=1024,
            messages=messages,
            tools=tools,
        )
        message = response.choices[0].message

        if not message.tool_calls:
            return {"answer": message.content or "", "trace": trace}

        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [tc.model_dump() for tc in message.tool_calls],
            }
        )

        for tc in message.tool_calls:
            tool_input = json.loads(tc.function.arguments)
            try:
                result = execute_tool(tc.function.name, tool_input)
                content = json.dumps(result, default=str)[:8000]
            except Exception as e:
                content = f"Error: {e}"
            trace.append({"tool": tc.function.name, "input": tool_input})
            messages.append(
                {"role": "tool", "tool_call_id": tc.id, "content": content}
            )

    return {"answer": "Reached max tool-call rounds without a final answer.", "trace": trace}
