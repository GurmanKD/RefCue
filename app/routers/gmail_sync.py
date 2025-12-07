from typing import Dict, Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..deps import get_db
from ..services.gmail_client import (
    get_gmail_service,
    fetch_linkedin_accept_emails,
    extract_name_and_company,
)

router = APIRouter(prefix="/gmail", tags=["gmail"])


@router.post("/sync")
def sync_linkedin_accepts(
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Sync recent LinkedIn 'accepted your invitation' emails from Gmail
    into the connections table.

    - Avoids duplicates using email_message_id (Gmail message ID).
    - Best-effort extraction of name and company.
    """
    service = get_gmail_service()
    emails = fetch_linkedin_accept_emails(service)

    created_connections: List[int] = []
    skipped_existing: List[str] = []

    for item in emails:
        msg_id = item["id"]

        existing = (
            db.query(models.Connection)
            .filter(models.Connection.email_message_id == msg_id)
            .first()
        )
        if existing:
            skipped_existing.append(msg_id)
            continue

        parsed = extract_name_and_company(
            subject=item["subject"],
            snippet=item["snippet"],
        )

        connection = models.Connection(
            name=parsed["name"],
            company_guess=parsed["company_guess"],
            source="linkedin_email",
            email_message_id=msg_id,
            raw_subject=item["subject"],
            raw_snippet=item["snippet"],
            accepted_at=item["internal_date"],
        )

        db.add(connection)
        db.commit()
        db.refresh(connection)

        created_connections.append(connection.id)

    return {
        "synced_count": len(created_connections),
        "created_connection_ids": created_connections,
        "skipped_existing_message_ids": skipped_existing,
        "total_emails_seen": len(emails),
    }
