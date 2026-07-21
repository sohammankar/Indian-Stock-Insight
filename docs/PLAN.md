# Roadmap

1. Prices + basic ticker dashboard (yfinance, FastAPI) — validate the pipeline
2. Corporate announcement / filing ingestion + LLM parsing for a handful of tickers
   — this is the differentiator (retail investors rarely see this synthesized)
3. LLM tool-calling layer ("why did X move today") over prices + filings
4. Bulk/block deal and shareholding pattern tracking, alerts
5. Migrate to a broker API (Kite Connect) for real-time data, add auth/watchlists/users
6. Evaluate direct NSE/BSE data licensing once there's traction
