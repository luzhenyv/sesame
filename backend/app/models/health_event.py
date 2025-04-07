from datetime import datetime, UTC
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY, UUID
import enum
import uuid

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.family_member import FamilyMember
    from app.models.user import User


class EventType(str, enum.Enum):
    CHECKUP = "CHECKUP"
    MEDICATION = "MEDICATION"
    SYMPTOM = "SYMPTOM"


class HealthEvent(Base):
    __tablename__ = "health_events"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    family_member_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("family_members.id"), nullable=False
    )
    created_by_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )

    # File attachments
    file_paths: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)
    file_types: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)

    # Relationships
    family_member: Mapped["FamilyMember"] = relationship(
        "FamilyMember", back_populates="health_events", lazy="selectin"
    )
    created_by: Mapped["User"] = relationship("User", backref="created_health_events")
