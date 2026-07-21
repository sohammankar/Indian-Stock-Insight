from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.alerts import store

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


class WatchlistItem(BaseModel):
    ticker: str


@router.get("")
def get_watchlist():
    return {"tickers": store.list_watchlist()}


@router.post("")
def add_ticker(item: WatchlistItem):
    symbol = item.ticker.strip().upper()
    if not symbol:
        raise HTTPException(status_code=400, detail="ticker must not be empty")
    store.add_to_watchlist(symbol)
    return {"tickers": store.list_watchlist()}


@router.delete("/{ticker}")
def remove_ticker(ticker: str):
    removed = store.remove_from_watchlist(ticker.strip().upper())
    if not removed:
        raise HTTPException(status_code=404, detail=f"{ticker.upper()} is not on the watchlist")
    return {"tickers": store.list_watchlist()}
