from fastapi import FastAPI

from .database import Base, engine

app = FastAPI(
    title="RefCue – Referral Opportunity Tracker",
    version="0.1.0",
    description=(
        "Track LinkedIn connection acceptances via Gmail and "
        "match them to your active job applications."
    ),
)


@app.on_event("startup")
def on_startup() -> None:
    # For dev: automatically create tables.
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok", "service": "refcue"}
