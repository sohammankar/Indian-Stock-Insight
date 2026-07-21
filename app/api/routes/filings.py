from fastapi import APIRouter, HTTPException

from app.ingestion import filings

router = APIRouter(prefix="/filings", tags=["filings"])


@router.get("/{symbol}/announcements")
def announcements(symbol: str, days: int = 30):
    try:
        return filings.get_announcements(symbol.upper(), days=days)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/{symbol}/board-meetings")
def board_meetings(symbol: str, days: int = 90):
    try:
        return filings.get_board_meetings(symbol.upper(), days=days)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/{symbol}/shareholding")
def shareholding(symbol: str):
    try:
        return filings.get_shareholding(symbol.upper())
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/bulk-deals")
def bulk_deals(days: int = 7):
    try:
        return filings.get_bulk_deals(days=days)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/block-deals")
def block_deals():
    try:
        return filings.get_block_deals()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
