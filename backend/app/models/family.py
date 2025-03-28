from datetime import datetime, UTC
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Column, String, DateTime, Table, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.family_member import FamilyMember

# Association table for user-family relationship
family_users = Table(
    "family_users",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column(
        "family_id", UUID(as_uuid=True), ForeignKey("families.id"), primary_key=True
    ),
)


class Family(Base):
    __tablename__ = "families"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User", secondary=family_users, back_populates="families"
    )
    members: Mapped[List["FamilyMember"]] = relationship(
        "FamilyMember", back_populates="family"
    )
