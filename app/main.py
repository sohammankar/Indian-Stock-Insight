from fastapi import FastAPI

from app.api.routes import filings, prices

app = FastAPI(title="Indian Stock Insights")

app.include_router(prices.router)
app.include_router(filings.router)


@app.get("/health")
def health():
    return {"status": "ok"}
