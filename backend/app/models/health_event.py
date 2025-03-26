from datetime import datetime, UTC
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY
import enum

from app.db.base_class import Base


class EventType(str, enum.Enum):
    CHECKUP = "checkup"
    MEDICATION = "medication"
    SYMPTOM = "symptom"


class HealthEvent(Base):
    __tablename__ = "health_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    family_member_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("family_members.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )

    # File attachments
    file_paths: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)
    file_types: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)

    # Relationships
    family_member = relationship(
        "FamilyMember", back_populates="health_events", lazy="selectin"
    )
