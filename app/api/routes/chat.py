from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.llm.agent import ask

router = APIRouter(prefix="/chat", tags=["chat"])


class HistoryTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[HistoryTurn] = []


@router.post("")
def chat(req: ChatRequest):
    try:
        return ask(req.question, history=[turn.model_dump() for turn in req.history])
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
