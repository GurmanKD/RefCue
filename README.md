# RefCue – Referral Opportunity Tracker

RefCue helps you track when your LinkedIn connection requests are accepted
and match those new connections to your active job applications.

✅ Track active job openings (company, role, job ID, link, deadline)  
✅ Parse "accepted your invitation" emails from LinkedIn (via Gmail)  
✅ Suggest referral opportunities when someone from a target company accepts

This is an MVP built with:

- FastAPI (Python backend)
- SQLite + SQLAlchemy (storage)
- Pydantic (request/response models)

## Quickstart (dev)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```