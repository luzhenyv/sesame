from datetime import date
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class FamilyMemberBase(BaseModel):
    name: str
    relationship: str
    date_of_birth: date
    gender: str


class FamilyMemberCreate(FamilyMemberBase):
    pass


class FamilyMemberUpdate(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None


class FamilyMemberResponse(FamilyMemberBase):
    id: UUID
    manager_id: int

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    items: List[FamilyMemberResponse]
    total: int
    page: int
    size: int
    pages: int
