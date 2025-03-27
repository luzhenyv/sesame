from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.health_event import EventType


class HealthEventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    event_type: EventType
    description: Optional[str] = None
    date_time: datetime = Field(default_factory=datetime.utcnow)
    family_member_id: int


class HealthEventCreate(HealthEventBase):
    pass


class HealthEventUpdate(HealthEventBase):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    event_type: Optional[EventType] = None
    description: Optional[str] = None
    date_time: Optional[datetime] = None
    family_member_id: Optional[int] = None


class HealthEventInDB(HealthEventBase):
    id: int
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HealthEventResponse(HealthEventInDB):
    file_url: Optional[str] = None


class HealthEventFilter(BaseModel):
    event_type: Optional[EventType] = None
    family_member_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None


class PaginatedResponse(BaseModel):
    items: List[HealthEventResponse]
    total: int
    page: int
    size: int
    pages: int
