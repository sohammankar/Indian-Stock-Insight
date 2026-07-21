import threading
from datetime import datetime, timedelta
from pathlib import Path

from nse import NSE

CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "nse_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

IDLE_TIMEOUT = timedelta(minutes=15)

_client: NSE | None = None
_last_used: datetime | None = None
_client_lock = threading.Lock()


def _get_client() -> NSE:
    """Reuse one NSE client across calls so its cookie cache actually gets
    used instead of being wiped after every call, but recycle it after 15
    minutes of inactivity rather than holding one session open forever."""
    global _client, _last_used
    now = datetime.now()
    with _client_lock:
        if _client is not None and now - _last_used > IDLE_TIMEOUT:
            _client._session.close()
            _client = None
        if _client is None:
            _client = NSE(download_folder=CACHE_DIR)
        _last_used = now
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
