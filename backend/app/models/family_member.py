from datetime import datetime, UTC
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
import uuid

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.health_event import HealthEvent
    from app.models.user import User


class MemberType(str, enum.Enum):
    HUMAN = "human"
    PET = "pet"


class FamilyMember(Base):
    __tablename__ = "family_members"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    member_type: Mapped[str] = mapped_column(Enum(MemberType), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    health_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Foreign Keys
    manager_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Relationships
    health_events: Mapped[List["HealthEvent"]] = relationship(
        "HealthEvent", back_populates="family_member", lazy="selectin"
    )
    manager: Mapped["User"] = relationship("User", back_populates="family_members")
