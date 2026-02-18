from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import daily, static

app = FastAPI(title="200 Scraper API Project")

origins = [
    "http://localhost:5173",  # local development
    "https://achyuta-shiksha.vercel.app",  # production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(daily.router, prefix="/api/daily", tags=["daily"])
app.include_router(static.router, prefix="/api/static", tags=["static"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
