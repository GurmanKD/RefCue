import os
from datetime import datetime
from typing import List, Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# We only need read-only access to Gmail
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Files expected in project root
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "credentials.json")
TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "token.json")


def get_gmail_credentials() -> Credentials:
    """
    Load Gmail API credentials (token.json).
    If missing/invalid, run OAuth flow using credentials.json.
    """
    creds: Optional[Credentials] = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh existing token
            creds.refresh(Request())
        else:
            # First-time auth: use credentials.json
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_FILE}. "
                    f"Download it from Google Cloud Console (OAuth 2.0 Client ID, Desktop app)."
                )

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def get_gmail_service():
    """
    Build a Gmail API service using stored credentials.
    """
    creds = get_gmail_credentials()
    service = build("gmail", "v1", credentials=creds)
    return service


def fetch_linkedin_accept_emails(
    service,
    max_results: int = 50,
) -> List[Dict[str, str]]:
    """
    Fetch recent LinkedIn "accepted your invitation" emails.

    Returns a list of dictionaries with:
    - id
    - threadId
    - subject
    - snippet
    - internal_date (as datetime)
    """
    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=max_results,
            q='"accepted your invitation" from:(notifications-noreply@linkedin.com)',
        )
        .execute()
    )

    messages = results.get("messages", [])
    parsed: List[Dict[str, str]] = []

    for msg in messages:
        msg_detail = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format="metadata", metadataHeaders=["Subject"])
            .execute()
        )

        headers = msg_detail.get("payload", {}).get("headers", [])
        subject = ""
        for h in headers:
            if h.get("name", "").lower() == "subject":
                subject = h.get("value", "")
                break

        snippet = msg_detail.get("snippet", "")

        internal_date_ms = int(msg_detail.get("internalDate", "0"))
        internal_date = datetime.utcfromtimestamp(internal_date_ms / 1000.0)

        parsed.append(
            {
                "id": msg["id"],
                "threadId": msg_detail.get("threadId", ""),
                "subject": subject,
                "snippet": snippet,
                "internal_date": internal_date,
            }
        )

    return parsed


def extract_name_and_company(subject: str, snippet: str) -> Dict[str, Optional[str]]:
    """
    Very simple heuristic to extract:
    - name: before 'accepted your invitation'
    - company_guess: try to pull from snippet if possible (best-effort).
    """
    name: Optional[str] = None
    company_guess: Optional[str] = None

    marker = "accepted your invitation"
    lower_subject = subject.lower()

    if marker in lower_subject:
        idx = lower_subject.index(marker)
        name_part = subject[:idx].strip()
        # Often LinkedIn subject looks like: "X accepted your invitation"
        name = name_part

    # For company_guess, LinkedIn snippets often include:
    # "... X is now a connection. X works at COMPANY ..."
    # We'll do a very naive approach:
    snippet_lower = snippet.lower()
    works_at_marker = "works at "
    if works_at_marker in snippet_lower:
        start = snippet_lower.index(works_at_marker) + len(works_at_marker)
        # Company is until next period or end
        sub = snippet[start:]
        end_idx = sub.find(".")
        if end_idx != -1:
            company_guess = sub[:end_idx].strip()
        else:
            company_guess = sub.strip()

    return {"name": name or "Unknown", "company_guess": company_guess}
