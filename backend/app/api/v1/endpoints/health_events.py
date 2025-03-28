from typing import List, Optional
from datetime import datetime
from uuid import UUID
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
from app.models.user import User
from app.services.file_service import file_service
from app.api.deps import get_current_user

router = APIRouter()


@router.post(
    "/", response_model=HealthEventResponse, summary="Create a new health event"
)
async def create_health_event(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    title: str = Form(...),
    event_type: EventType = Form(...),
    description: Optional[str] = Form(None),
    family_member_id: UUID = Form(...),
    date_time: datetime = Form(...),
    files: List[UploadFile] = File(None),
):
    """
    Create a new health event with optional file attachments.

    - **title**: Event title
    - **event_type**: Type of event (CHECKUP, MEDICATION, SYMPTOM)
    - **description**: Event description (optional)
    - **family_member_id**: UUID of the family member
    - **date_time**: Date and time of the event
    - **files**: Optional file attachments (images or PDFs)
    """
    # Create health event in database
    event_data = HealthEventCreate(
        title=title,
        event_type=event_type,
        description=description,
        family_member_id=family_member_id,
        created_by_id=current_user.id,
        date_time=date_time,
    )

    try:
        db_event = HealthEvent(**event_data.model_dump())
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Handle file uploads if provided
    if files:
        try:
            file_paths = []
            file_types = []
            for file in files:
                file_path = await file_service.save_file(file, str(db_event.id))
                file_paths.append(file_path)
                file_types.append(file.content_type)

            db_event.file_paths = file_paths
            db_event.file_types = file_types
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
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    event_type: Optional[EventType] = Query(None, description="Filter by event type"),
    family_member_id: Optional[UUID] = Query(
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
    - **family_member_id**: Filter by family member UUID
    - **start_date**: Filter by start date
    - **end_date**: Filter by end date
    - **search**: Search in title and description
    """
    # Build query
    query = db.query(HealthEvent)

    # Only show events for family members managed by current user
    query = query.join(HealthEvent.family_member).filter(
        HealthEvent.family_member.has(manager_id=current_user.id)
    )

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
def get_health_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific health event by ID.

    - **event_id**: UUID of the health event
    """
    event = db.query(HealthEvent).filter(HealthEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Health event not found")

    # Check if user has access to this event
    if event.family_member.manager_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this event"
        )

    return event


@router.put(
    "/{event_id}", response_model=HealthEventResponse, summary="Update health event"
)
async def update_health_event(
    event_id: UUID,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    title: Optional[str] = Form(None),
    event_type: Optional[EventType] = Form(None),
    description: Optional[str] = Form(None),
    family_member_id: Optional[UUID] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
):
    """
    Update a health event and optionally its file attachments.

    - **event_id**: UUID of the health event to update
    - **title**: New event title (optional)
    - **event_type**: New event type (optional)
    - **description**: New event description (optional)
    - **family_member_id**: New family member UUID (optional)
    - **files**: New file attachments (optional)
    """
    event = db.query(HealthEvent).filter(HealthEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Health event not found")

    # Check if user has access to this event
    if event.family_member.manager_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to modify this event"
        )

    # Update event data
    update_data = HealthEventUpdate(
        title=title,
        event_type=event_type,
        description=description,
        family_member_id=family_member_id,
    )

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    # Handle file uploads if provided
    if files:
        try:
            # Delete old files if they exist
            if event.file_paths:
                for file_path in event.file_paths:
                    await file_service.delete_file(file_path)

            # Save new files
            file_paths = []
            file_types = []
            for file in files:
                file_path = await file_service.save_file(file, str(event_id))
                file_paths.append(file_path)
                file_types.append(file.content_type)

            event.file_paths = file_paths
            event.file_types = file_types
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", summary="Delete health event")
async def delete_health_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a health event and its associated files.

    - **event_id**: UUID of the health event to delete
    """
    event = db.query(HealthEvent).filter(HealthEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Health event not found")

    # Check if user has access to this event
    if event.family_member.manager_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this event"
        )

    # Delete associated files if they exist
    if event.file_paths:
        for file_path in event.file_paths:
            await file_service.delete_file(file_path)

    db.delete(event)
    db.commit()
    return {"message": "Health event deleted successfully"}
