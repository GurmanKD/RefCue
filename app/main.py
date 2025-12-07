from fastapi import FastAPI

app = FastAPI(
    title="RefCue – Referral Opportunity Tracker",
    version="0.1.0",
    description=(
        "Track LinkedIn connection acceptances via Gmail and "
        "match them to your active job applications."
    ),
)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok", "service": "refcue"}
