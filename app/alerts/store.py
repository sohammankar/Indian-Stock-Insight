import json
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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS watchlist (
            symbol TEXT PRIMARY KEY
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS alert_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            symbol TEXT NOT NULL,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    return conn


def log_alert(alert: dict) -> None:
    with _lock, _connect() as conn:
        conn.execute(
            "INSERT INTO alert_log (type, symbol, payload) VALUES (?, ?, ?)",
            (alert["type"], alert["symbol"], json.dumps(alert)),
        )


def recent_alerts(limit: int = 50, only_watchlisted: bool = True) -> list[dict]:
    with _lock, _connect() as conn:
        if only_watchlisted:
            rows = conn.execute(
                """
                SELECT payload, created_at FROM alert_log
                WHERE symbol IN (SELECT symbol FROM watchlist)
                ORDER BY id DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT payload, created_at FROM alert_log ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        results = []
        for payload, created_at in rows:
            alert = json.loads(payload)
            alert["created_at"] = created_at
            results.append(alert)
        return results


def add_to_watchlist(symbol: str) -> None:
    with _lock, _connect() as conn:
        conn.execute("INSERT OR IGNORE INTO watchlist (symbol) VALUES (?)", (symbol,))


def remove_from_watchlist(symbol: str) -> bool:
    """Returns True if the symbol was present and got removed."""
    with _lock, _connect() as conn:
        cursor = conn.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol,))
        return cursor.rowcount > 0


def list_watchlist() -> list[str]:
    with _lock, _connect() as conn:
        rows = conn.execute("SELECT symbol FROM watchlist ORDER BY symbol").fetchall()
        return [r[0] for r in rows]


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
