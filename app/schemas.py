from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl, field_validator


# ---------- Job Schemas ----------

class JobBase(BaseModel):
    company: str
    role: str
    job_id: Optional[str] = None
    link: Optional[HttpUrl] = None
    deadline: Optional[date] = None
    status: str = "active"  # active / applied / closed

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        allowed = {"active", "applied", "closed"}
        if value not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return value


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    job_id: Optional[str] = None
    link: Optional[HttpUrl] = None
    deadline: Optional[date] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        allowed = {"active", "applied", "closed"}
        if value not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return value


class JobRead(JobBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------- Connection & Referral Schemas (for later use) ----------

class ConnectionRead(BaseModel):
    id: int
    name: str
    company_guess: Optional[str]
    source: str
    accepted_at: datetime
    status: str

    class Config:
        from_attributes = True


class ReferralOpportunityRead(BaseModel):
    id: int
    status: str
    created_at: datetime
    note: Optional[str]
    job: JobRead
    connection: ConnectionRead

    class Config:
        from_attributes = True
