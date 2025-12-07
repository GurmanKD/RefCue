from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Date,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company: Mapped[str] = mapped_column(String(255), index=True)
    role: Mapped[str] = mapped_column(String(255))
    job_id: Mapped[Optional[str]] = mapped_column(
        String(255), index=True, nullable=True
    )
    link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="active", index=True
    )  # active / applied / closed

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    referral_opportunities: Mapped[List["ReferralOpportunity"]] = relationship(
        "ReferralOpportunity",
        back_populates="job",
        cascade="all, delete-orphan",
    )


class Connection(Base):
    __tablename__ = "connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    company_guess: Mapped[Optional[str]] = mapped_column(
        String(255), index=True, nullable=True
    )
    source: Mapped[str] = mapped_column(
        String(50), default="linkedin_email"
    )  # for future: linkedin_api, manual, etc.
    email_message_id: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True
    )  # Gmail message ID to avoid duplicates

    raw_subject: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    accepted_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )

    status: Mapped[str] = mapped_column(
        String(50), default="new"
    )  # new / processed

    referral_opportunities: Mapped[List["ReferralOpportunity"]] = relationship(
        "ReferralOpportunity",
        back_populates="connection",
        cascade="all, delete-orphan",
    )


class ReferralOpportunity(Base):
    __tablename__ = "referral_opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("jobs.id", ondelete="CASCADE"), index=True
    )
    connection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("connections.id", ondelete="CASCADE"), index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )

    status: Mapped[str] = mapped_column(
        String(50), default="new"
    )  # new / contacted / done / ignored

    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    job: Mapped[Job] = relationship("Job", back_populates="referral_opportunities")
    connection: Mapped[Connection] = relationship(
        "Connection", back_populates="referral_opportunities"
    )
