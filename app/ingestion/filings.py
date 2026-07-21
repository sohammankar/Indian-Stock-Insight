from datetime import datetime, timedelta
from pathlib import Path

from nse import NSE

CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "nse_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _client() -> NSE:
    return NSE(download_folder=CACHE_DIR)


def get_announcements(symbol: str, days: int = 30) -> list[dict]:
    nse = _client()
    try:
        from_date = datetime.now() - timedelta(days=days)
        return nse.announcements(symbol=symbol.upper(), from_date=from_date, to_date=datetime.now())
    finally:
        nse.exit()


def get_board_meetings(symbol: str, days: int = 90) -> list[dict]:
    nse = _client()
    try:
        from_date = datetime.now() - timedelta(days=days)
        return nse.boardMeetings(symbol=symbol.upper(), from_date=from_date, to_date=datetime.now())
    finally:
        nse.exit()


def get_shareholding(symbol: str) -> list[dict]:
    nse = _client()
    try:
        return nse.shareholding(symbol=symbol.upper())
    finally:
        nse.exit()


def get_bulk_deals(days: int = 7) -> list[dict]:
    nse = _client()
    try:
        from_date = datetime.now() - timedelta(days=days)
        return nse.bulkdeals(option_type="bulk_deals", fromdate=from_date, todate=datetime.now())
    finally:
        nse.exit()


def get_block_deals() -> dict:
    nse = _client()
    try:
        return nse.blockDeals()
    finally:
        nse.exit()
