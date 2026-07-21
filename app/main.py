from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.alerts import scheduler
from app.api.routes import alerts, chat, filings, prices, watchlist

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.stop()


app = FastAPI(title="Indian Stock Insights", lifespan=lifespan)

app.include_router(prices.router)
app.include_router(filings.router)
app.include_router(chat.router)
app.include_router(alerts.router)
app.include_router(watchlist.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")
