from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db

router = APIRouter(prefix="/referrals", tags=["referrals"])


@router.post("/", response_model=schemas.ReferralOpportunityRead, status_code=status.HTTP_201_CREATED)
def create_referral_opportunity(
    data: schemas.ReferralOpportunityCreate,
    db: Session = Depends(get_db),
) -> schemas.ReferralOpportunityRead:

    job = db.query(models.Job).filter(models.Job.id == data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    conn = db.query(models.Connection).filter(models.Connection.id == data.connection_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    referral = models.ReferralOpportunity(
        job_id=data.job_id,
        connection_id=data.connection_id,
        note=data.note,
    )

    db.add(referral)
    db.commit()
    db.refresh(referral)

    return referral


@router.get("/", response_model=List[schemas.ReferralOpportunityRead])
def list_referral_opportunities(
    db: Session = Depends(get_db),
) -> List[schemas.ReferralOpportunityRead]:

    return db.query(models.ReferralOpportunity)\
        .order_by(models.ReferralOpportunity.created_at.desc())\
        .all()
