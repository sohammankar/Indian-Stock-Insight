from fastapi import APIRouter, HTTPException, Query

from app.alerts import tracker

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/check")
def check(tickers: str = Query(..., description="Comma-separated NSE symbols, e.g. TCS,INFY,RELIANCE")):
    ticker_list = [t.strip() for t in tickers.split(",") if t.strip()]
    if not ticker_list:
        raise HTTPException(status_code=400, detail="Provide at least one ticker")
    try:
        return {"alerts": tracker.check_all(ticker_list)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
