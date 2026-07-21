from collections import defaultdict

from app.alerts import store
from app.ingestion import filings

SHAREHOLDING_ALERT_THRESHOLD_PCT = 0.5


def check_bulk_deals(tickers: list[str], days: int = 1) -> list[dict]:
    """Fetch recent market-wide bulk deals, filter to the watchlist, dedupe
    against deals we've already seen, and emit one aggregated alert per
    symbol+date (an active stock can have a dozen individual trades in a
    single day, which would otherwise flood the alert log with near-duplicates)."""
    watchlist = {t.upper() for t in tickers}
    deals = filings.get_bulk_deals(days=days)

    new_by_symbol_date = defaultdict(list)
    for deal in deals:
        symbol = deal.get("BD_SYMBOL")
        if symbol not in watchlist:
            continue

        is_new = store.record_bulk_deal_if_new(
            symbol=symbol,
            deal_date=deal.get("BD_DT_DATE", ""),
            client_name=deal.get("BD_CLIENT_NAME", ""),
            buy_sell=deal.get("BD_BUY_SELL", ""),
            qty=int(deal.get("BD_QTY_TRD", 0)),
            price=float(deal.get("BD_TP_WATP", 0)),
        )
        if is_new:
            new_by_symbol_date[(symbol, deal.get("BD_DT_DATE"))].append(deal)

    alerts = []
    for (symbol, date), group in new_by_symbol_date.items():
        buy_qty = sum(int(d.get("BD_QTY_TRD", 0)) for d in group if d.get("BD_BUY_SELL") == "BUY")
        sell_qty = sum(int(d.get("BD_QTY_TRD", 0)) for d in group if d.get("BD_BUY_SELL") == "SELL")
        total_value = sum(int(d.get("BD_QTY_TRD", 0)) * float(d.get("BD_TP_WATP", 0)) for d in group)
        clients = list(dict.fromkeys(d.get("BD_CLIENT_NAME") for d in group))

        alert = {
            "type": "bulk_deal",
            "symbol": symbol,
            "date": date,
            "num_trades": len(group),
            "buy_qty": buy_qty,
            "sell_qty": sell_qty,
            "total_value": round(total_value),
            "clients": clients[:3],
            "more_clients": max(0, len(clients) - 3),
        }
        store.log_alert(alert)
        alerts.append(alert)
    return alerts


def check_shareholding(tickers: list[str]) -> list[dict]:
    """Compare each ticker's latest promoter holding % against the last
    snapshot we recorded, and alert if it moved more than the threshold."""
    alerts = []
    for ticker in tickers:
        symbol = ticker.upper()
        rows = filings.get_shareholding(symbol)
        if not rows:
            continue

        latest = rows[0]
        period_date = latest.get("date", "")
        try:
            promoter_pct = float(latest.get("pr_and_prgrp", ""))
        except (TypeError, ValueError):
            continue

        previous = store.latest_shareholding_snapshot(symbol)
        store.record_shareholding_snapshot(symbol, period_date, promoter_pct)

        if previous is None or previous["period_date"] == period_date:
            continue  # first time seeing this symbol, or no new filing yet - just a baseline

        change = promoter_pct - previous["promoter_pct"]
        if abs(change) >= SHAREHOLDING_ALERT_THRESHOLD_PCT:
            alert = {
                "type": "shareholding_change",
                "symbol": symbol,
                "period_date": period_date,
                "previous_promoter_pct": previous["promoter_pct"],
                "current_promoter_pct": promoter_pct,
                "change_pct": round(change, 2),
            }
            store.log_alert(alert)
            alerts.append(alert)
    return alerts


def check_all(tickers: list[str]) -> list[dict]:
    return check_bulk_deals(tickers) + check_shareholding(tickers)
