from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db

router = APIRouter(prefix="/connections", tags=["connections"])


@router.post("/", response_model=schemas.ConnectionRead, status_code=status.HTTP_201_CREATED)
def create_connection(
    conn_in: schemas.ConnectionCreate,
    db: Session = Depends(get_db),
) -> schemas.ConnectionRead:
    connection = models.Connection(
        name=conn_in.name,
        company_guess=conn_in.company_guess,
        source=conn_in.source,
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection


@router.get("/", response_model=List[schemas.ConnectionRead])
def list_connections(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
) -> List[schemas.ConnectionRead]:
    query = db.query(models.Connection)

    if status:
        query = query.filter(models.Connection.status == status)

    return query.order_by(models.Connection.accepted_at.desc()).all()


@router.get("/{connection_id}", response_model=schemas.ConnectionRead)
def get_connection(
    connection_id: int,
    db: Session = Depends(get_db),
) -> schemas.ConnectionRead:
    connection = db.query(models.Connection).filter(models.Connection.id == connection_id).first()

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    return connection
