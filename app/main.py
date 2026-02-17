from fastapi import FastAPI
from .routers import daily, static  # routers folder ke daily.py aur static.py

app = FastAPI(title="200 Scraper API Project")

# Routers include karo
app.include_router(daily.router, prefix="/api/daily", tags=["daily"])
app.include_router(static.router, prefix="/api/static", tags=["static"])

# Optional: health check
@app.get("/health")
def health_check():
    return {"status": "ok"}
