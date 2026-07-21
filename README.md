# Indian Stock Insights

A platform for tracking Indian stock market data and answering questions about it —
starting with prices, expanding to corporate filings, bulk/block deals, and shareholding
pattern intelligence that most retail tools don't surface.

## Status

Early scaffold. See `docs/PLAN.md` for the roadmap.

## Run locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
