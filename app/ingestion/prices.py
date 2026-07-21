import yfinance as yf


def _nse_symbol(ticker: str) -> str:
    ticker = ticker.strip().upper()
    return ticker if ticker.endswith(".NS") else f"{ticker}.NS"


def get_price_history(ticker: str, period: str = "3mo") -> list[dict]:
    """Fetch OHLCV history for an NSE ticker (e.g. 'TCS' -> 'TCS.NS')."""
    hist = yf.Ticker(_nse_symbol(ticker)).history(period=period)
    hist = hist.reset_index()
    return hist.to_dict(orient="records")


def get_quote(ticker: str) -> dict:
    info = yf.Ticker(_nse_symbol(ticker)).fast_info
    return dict(info)
