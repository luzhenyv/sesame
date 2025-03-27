from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.schemas.health_event import (
    HealthEventCreate,
    HealthEventUpdate,
    HealthEventResponse,
    HealthEventInDB,
    HealthEventFilter,
    PaginatedResponse,
)
from app.models.health_event import HealthEvent, EventType
from app.services.file_service import FileService
from app.core.config import settings

router = APIRouter()
file_service = FileService()


@router.post(
    "/", response_model=HealthEventResponse, summary="Create a new health event"
)
async def create_health_event(
    *,
    db: Session = Depends(get_db),
    title: str = Form(...),
    event_type: EventType = Form(...),
    description: str = Form(None),
    family_member_id: int = Form(...),
    date_time: datetime = Form(...),
    file: UploadFile = File(None),
):
    """
    Create a new health event with optional file attachment.

    - **title**: Event title
    - **event_type**: Type of event (checkup, medication, symptom)
    - **description**: Event description (optional)
    - **family_member_id**: ID of the family member
    - **date_time**: Date and time of the event
    - **file**: Optional file attachment (image or PDF)
    """
    # Create health event in database
    event_data = HealthEventCreate(
        title=title,
        event_type=event_type,
        description=description,
        family_member_id=family_member_id,
    )

    try:
        db_event = HealthEvent(**event_data.model_dump())
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Handle file upload if provided
    if file:
        try:
            file_path = await file_service.save_file(file, str(db_event.id))
            db_event.file_path = file_path
            db.commit()
            db.refresh(db_event)
        except ValueError as e:
            # If file upload fails, delete the created event
            db.delete(db_event)
            db.commit()
            raise HTTPException(status_code=400, detail=str(e))

    return db_event


@router.get("/", response_model=PaginatedResponse, summary="List health events")
def get_health_events(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    event_type: Optional[EventType] = Query(None, description="Filter by event type"),
    family_member_id: Optional[int] = Query(
        None, description="Filter by family member ID"
    ),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    search: Optional[str] = Query(None, description="Search in title and description"),
):
    """
    Get paginated list of health events with optional filtering.

    - **page**: Page number (1-based)
    - **size**: Number of items per page (1-100)
    - **event_type**: Filter by event type
    - **family_member_id**: Filter by family member ID
    - **start_date**: Filter by start date
    - **end_date**: Filter by end date
    - **search**: Search in title and description
    """
    # Build query
    query = db.query(HealthEvent)

    # Apply filters
    if event_type:
        query = query.filter(HealthEvent.event_type == event_type)
    if family_member_id:
        query = query.filter(HealthEvent.family_member_id == family_member_id)
    if start_date:
        query = query.filter(HealthEvent.date_time >= start_date)
    if end_date:
        query = query.filter(HealthEvent.date_time <= end_date)
    if search:
        search_filter = or_(
            HealthEvent.title.ilike(f"%{search}%"),
            HealthEvent.description.ilike(f"%{search}%"),
        )
        query = query.filter(search_filter)

    # Get total count
    total = query.count()

    # Calculate pagination
    total_pages = (total + size - 1) // size
    offset = (page - 1) * size

    # Get paginated results
    events = query.offset(offset).limit(size).all()

    return PaginatedResponse(
        items=events, total=total, page=page, size=size, pages=total_pages
    )


@router.get(
    "/{event_id}", response_model=HealthEventResponse, summary="Get health event by ID"
)
def get_health_event(event_id: int, db: Session = Depends(get_db)):
    """
    Get a specific health event by ID.

    - **event_id**: ID of the health event
    """
    event = db.query(HealthEvent).filter(HealthEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Health event not found")
    return event


@router.put(
    "/{event_id}", response_model=HealthEventResponse, summary="Update health event"
)
async def update_health_event(
    event_id: int,
    *,
    db: Session = Depends(get_db),
    title: str = Form(None),
    event_type: EventType = Form(None),
    description: str = Form(None),
    family_member_id: int = Form(None),
    file: UploadFile = File(None),
):
    """
    Update a health event and optionally its file attachment.

    - **event_id**: ID of the health event to update
    - **title**: New event title (optional)
    - **event_type**: New event type (optional)
    - **description**: New event description (optional)
    - **family_member_id**: New family member ID (optional)
    - **file**: New file attachment (optional)
    """
    event = db.query(HealthEvent).filter(HealthEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Health event not found")

    # Update event data
    update_data = HealthEventUpdate(
        title=title,
        event_type=event_type,
        description=description,
        family_member_id=family_member_id,
    )

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    # Handle file upload if provided
    if file:
        try:
            # Delete old file if exists
            if event.file_path:
                await file_service.delete_file(event.file_path)

            # Save new file
            file_path = await file_service.save_file(file, str(event_id))
            event.file_path = file_path
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", summary="Delete health event")
async def delete_health_event(event_id: int, db: Session = Depends(get_db)):
    """
    Delete a health event and its associated file.

    - **event_id**: ID of the health event to delete
    """
    event = db.query(HealthEvent).filter(HealthEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Health event not found")

    # Delete associated file if exists
    if event.file_path:
        await file_service.delete_file(event.file_path)

    db.delete(event)
    db.commit()
    return {"message": "Health event deleted successfully"}
