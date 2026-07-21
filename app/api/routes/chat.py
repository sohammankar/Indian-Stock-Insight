from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.llm.agent import ask

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str


@router.post("")
def chat(req: ChatRequest):
    try:
        return ask(req.question)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
