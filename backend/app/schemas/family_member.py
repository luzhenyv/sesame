from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from app.models.family_member import MemberType


class FamilyMemberBase(BaseModel):
    name: str
    member_type: MemberType
    relation_type: str
    date_of_birth: Optional[date] = None
    health_score: Optional[int] = None
    notes: Optional[str] = None


class FamilyMemberCreate(FamilyMemberBase):
    pass


class FamilyMemberUpdate(BaseModel):
    name: Optional[str] = None
    member_type: Optional[MemberType] = None
    relation_type: Optional[str] = None
    date_of_birth: Optional[date] = None
    health_score: Optional[int] = None
    notes: Optional[str] = None


class FamilyMemberResponse(FamilyMemberBase):
    id: UUID
    manager_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    items: List[FamilyMemberResponse]
    total: int
    page: int
    size: int
    pages: int
