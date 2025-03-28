from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.health_event import EventType
from uuid import UUID


class HealthEventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    event_type: EventType
    description: Optional[str] = None
    date_time: datetime = Field(default_factory=datetime.utcnow)
    family_member_id: UUID


class HealthEventCreate(HealthEventBase):
    created_by_id: UUID


class HealthEventUpdate(HealthEventBase):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    event_type: Optional[EventType] = None
    description: Optional[str] = None
    date_time: Optional[datetime] = None
    family_member_id: Optional[UUID] = None


class HealthEventInDB(HealthEventBase):
    id: UUID
    file_paths: Optional[List[str]] = None
    file_types: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HealthEventResponse(HealthEventInDB):
    file_urls: Optional[List[str]] = None


class HealthEventFilter(BaseModel):
    event_type: Optional[EventType] = None
    family_member_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None


class PaginatedResponse(BaseModel):
    items: List[HealthEventResponse]
    total: int
    page: int
    size: int
    pages: int
