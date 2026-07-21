import sqlite3
import threading
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "alerts.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_lock = threading.Lock()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS seen_bulk_deal (
            symbol TEXT NOT NULL,
            deal_date TEXT NOT NULL,
            client_name TEXT NOT NULL,
            buy_sell TEXT NOT NULL,
            qty INTEGER NOT NULL,
            price REAL NOT NULL,
            PRIMARY KEY (symbol, deal_date, client_name, buy_sell, qty, price)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS shareholding_snapshot (
            symbol TEXT NOT NULL,
            period_date TEXT NOT NULL,
            promoter_pct REAL NOT NULL,
            PRIMARY KEY (symbol, period_date)
        )
        """
    )
    return conn


def record_bulk_deal_if_new(symbol: str, deal_date: str, client_name: str, buy_sell: str, qty: int, price: float) -> bool:
    """Returns True if this deal hadn't been seen before (i.e. it's new)."""
    with _lock, _connect() as conn:
        try:
            conn.execute(
                "INSERT INTO seen_bulk_deal (symbol, deal_date, client_name, buy_sell, qty, price) VALUES (?, ?, ?, ?, ?, ?)",
                (symbol, deal_date, client_name, buy_sell, qty, price),
            )
            return True
        except sqlite3.IntegrityError:
            return False


def latest_shareholding_snapshot(symbol: str) -> dict | None:
    with _lock, _connect() as conn:
        row = conn.execute(
            "SELECT period_date, promoter_pct FROM shareholding_snapshot WHERE symbol = ? ORDER BY period_date DESC LIMIT 1",
            (symbol,),
        ).fetchone()
        return {"period_date": row[0], "promoter_pct": row[1]} if row else None


def record_shareholding_snapshot(symbol: str, period_date: str, promoter_pct: float) -> None:
    with _lock, _connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO shareholding_snapshot (symbol, period_date, promoter_pct) VALUES (?, ?, ?)",
            (symbol, period_date, promoter_pct),
        )
