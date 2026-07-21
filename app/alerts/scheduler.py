import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.alerts import store, tracker
from app.config import settings

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _run_check() -> None:
    tickers = store.list_watchlist()
    if not tickers:
        return
    try:
        alerts = tracker.check_all(tickers)
        logger.info("Scheduled alert check found %d new alert(s) for %s", len(alerts), tickers)
    except Exception:
        logger.exception("Scheduled alert check failed")


def start() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = BackgroundScheduler()
    _scheduler.add_job(_run_check, "interval", minutes=settings.alerts_poll_minutes)
    _scheduler.start()


def stop() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
