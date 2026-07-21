import threading
from datetime import datetime, timedelta
from pathlib import Path

from nse import NSE

CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "nse_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

_client: NSE | None = None
_client_lock = threading.Lock()


def _get_client() -> NSE:
    """Reuse one NSE client for the process lifetime so its cookie cache
    actually gets used instead of being wiped after every call."""
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = NSE(download_folder=CACHE_DIR)
    return _client


def get_announcements(symbol: str, days: int = 30) -> list[dict]:
    from_date = datetime.now() - timedelta(days=days)
    return _get_client().announcements(symbol=symbol.upper(), from_date=from_date, to_date=datetime.now())


def get_board_meetings(symbol: str, days: int = 90) -> list[dict]:
    from_date = datetime.now() - timedelta(days=days)
    return _get_client().boardMeetings(symbol=symbol.upper(), from_date=from_date, to_date=datetime.now())


def get_shareholding(symbol: str) -> list[dict]:
    return _get_client().shareholding(symbol=symbol.upper())


def get_bulk_deals(days: int = 7) -> list[dict]:
    from_date = datetime.now() - timedelta(days=days)
    return _get_client().bulkdeals(option_type="bulk_deals", fromdate=from_date, todate=datetime.now())


def get_block_deals() -> dict:
    return _get_client().blockDeals()
