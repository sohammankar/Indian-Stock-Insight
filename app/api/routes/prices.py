from fastapi import APIRouter, HTTPException

from app.ingestion.prices import get_price_history, get_quote

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/{ticker}/quote")
def quote(ticker: str):
    try:
        return get_quote(ticker.upper())
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{ticker}/history")
def history(ticker: str, period: str = "3mo"):
    try:
        return get_price_history(ticker.upper(), period)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
