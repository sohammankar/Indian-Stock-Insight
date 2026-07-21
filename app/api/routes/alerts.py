from fastapi import APIRouter, HTTPException, Query

from app.alerts import store, tracker

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/check")
def check(
    tickers: str
    | None = Query(
        None, description="Comma-separated NSE symbols, e.g. TCS,INFY,RELIANCE. Defaults to the saved watchlist."
    )
):
    if tickers:
        ticker_list = [t.strip() for t in tickers.split(",") if t.strip()]
    else:
        ticker_list = store.list_watchlist()

    if not ticker_list:
        raise HTTPException(status_code=400, detail="No tickers provided and the watchlist is empty")
    try:
        return {"alerts": tracker.check_all(ticker_list)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/recent")
def recent(limit: int = 50):
    return {"alerts": store.recent_alerts(limit=limit)}
