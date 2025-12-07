from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


@router.post(
    "/",
    response_model=schemas.JobRead,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    job_in: schemas.JobCreate,
    db: Session = Depends(get_db),
) -> schemas.JobRead:
    job = models.Job(
        company=job_in.company,
        role=job_in.role,
        job_id=job_in.job_id,
        link=str(job_in.link) if job_in.link else None,
        deadline=job_in.deadline,
        status=job_in.status,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/", response_model=List[schemas.JobRead])
def list_jobs(
    db: Session = Depends(get_db),
    status_filter: Optional[str] = None,
    company: Optional[str] = None,
) -> List[schemas.JobRead]:
    query = db.query(models.Job)

    if status_filter:
        query = query.filter(models.Job.status == status_filter)

    if company:
        query = query.filter(models.Job.company.ilike(f"%{company}%"))

    return query.order_by(models.Job.created_at.desc()).all()


@router.get("/{job_id}", response_model=schemas.JobRead)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
) -> schemas.JobRead:
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return job


@router.put("/{job_id}", response_model=schemas.JobRead)
def update_job(
    job_id: int,
    job_in: schemas.JobUpdate,
    db: Session = Depends(get_db),
) -> schemas.JobRead:
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    update_data = job_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "link" and value is not None:
            setattr(job, field, str(value))
        else:
            setattr(job, field, value)

    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
) -> None:
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    db.delete(job)
    db.commit()
    return None
