import yfinance as yf


def get_price_history(ticker: str, period: str = "3mo") -> list[dict]:
    """Fetch OHLCV history for an NSE ticker (e.g. 'TCS' -> 'TCS.NS')."""
    symbol = ticker if ticker.endswith(".NS") else f"{ticker}.NS"
    hist = yf.Ticker(symbol).history(period=period)
    hist = hist.reset_index()
    return hist.to_dict(orient="records")


def get_quote(ticker: str) -> dict:
    symbol = ticker if ticker.endswith(".NS") else f"{ticker}.NS"
    info = yf.Ticker(symbol).fast_info
    return dict(info)
