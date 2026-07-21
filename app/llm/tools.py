from app.ingestion import filings, prices

TOOL_DEFINITIONS = [
    {
        "name": "get_quote",
        "description": "Get the current/latest price quote for an NSE-listed stock (day high/low, previous close, market cap, etc).",
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string", "description": "NSE symbol, e.g. TCS, RELIANCE"}},
            "required": ["ticker"],
        },
    },
    {
        "name": "get_price_history",
        "description": "Get historical OHLCV price data for an NSE-listed stock.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "NSE symbol, e.g. TCS"},
                "period": {
                    "type": "string",
                    "description": "yfinance period string, e.g. '5d', '1mo', '3mo', '1y'",
                    "default": "1mo",
                },
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_announcements",
        "description": "Get recent corporate announcements/filings for an NSE-listed company (press releases, results, board decisions).",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "NSE symbol, e.g. TCS"},
                "days": {"type": "integer", "description": "Lookback window in days", "default": 30},
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_shareholding",
        "description": "Get the latest shareholding pattern for an NSE-listed company: promoter holding %, public holding %, and remarks explaining structure/pledges.",
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string", "description": "NSE symbol, e.g. TCS"}},
            "required": ["ticker"],
        },
    },
    {
        "name": "get_bulk_deals",
        "description": "Get recent bulk deals across the whole market (large trades by named clients) - useful for spotting institutional/smart-money activity in a stock.",
        "input_schema": {
            "type": "object",
            "properties": {"days": {"type": "integer", "description": "Lookback window in days", "default": 7}},
        },
    },
    {
        "name": "get_block_deals",
        "description": "Get today's block deals across the whole market (single large negotiated trades) - another signal of institutional/smart-money activity.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_board_meetings",
        "description": "Get scheduled/recent board meetings for an NSE-listed company, including agenda (e.g. results, dividends, fundraising).",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "NSE symbol, e.g. TCS"},
                "days": {"type": "integer", "description": "Lookback window in days", "default": 90},
            },
            "required": ["ticker"],
        },
    },
]


def execute_tool(name: str, tool_input: dict):
    if name == "get_quote":
        return prices.get_quote(tool_input["ticker"])
    if name == "get_price_history":
        return prices.get_price_history(tool_input["ticker"], tool_input.get("period", "1mo"))
    if name == "get_announcements":
        return filings.get_announcements(tool_input["ticker"], days=tool_input.get("days", 30))
    if name == "get_shareholding":
        return filings.get_shareholding(tool_input["ticker"])
    if name == "get_bulk_deals":
        return filings.get_bulk_deals(days=tool_input.get("days", 7))
    if name == "get_block_deals":
        return filings.get_block_deals()
    if name == "get_board_meetings":
        return filings.get_board_meetings(tool_input["ticker"], days=tool_input.get("days", 90))
    raise ValueError(f"Unknown tool: {name}")
