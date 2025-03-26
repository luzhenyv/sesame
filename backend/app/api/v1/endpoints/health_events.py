from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.health_event import (
    HealthEventCreate,
    HealthEventUpdate,
    HealthEventResponse,
    HealthEventInDB,
)
from app.models.health_event import HealthEvent
from app.services.file_service import FileService
from app.core.config import settings

router = APIRouter()
file_service = FileService()


@router.post(
    "/", response_model=HealthEventResponse, summary="Create a new health event"
)
async def create_health_event(
    *,
    db: Session = Depends(deps.get_db),
    title: str = Form(...),
    event_type: str = Form(...),
    description: str = Form(None),
    family_member_id: int = Form(...),
    file: UploadFile = File(None)
):
    """
    Create a new health event with optional file attachment.

    - **title**: Event title
    - **event_type**: Type of event (checkup, medication, symptom)
    - **description**: Event description (optional)
    - **family_member_id**: ID of the family member
    - **file**: Optional file attachment (image or PDF)
    """
    # Create health event in database
    event_data = HealthEventCreate(
        title=title,
        event_type=event_type,
        description=description,
        family_member_id=family_member_id,
    )

    db_event = HealthEvent(**event_data.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

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


@router.get("/", response_model=List[HealthEventResponse], summary="List health events")
def get_health_events(
    db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100
):
    """
    Get list of health events with pagination.

    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    events = db.query(HealthEvent).offset(skip).limit(limit).all()
    return events


@router.get(
    "/{event_id}", response_model=HealthEventResponse, summary="Get health event by ID"
)
def get_health_event(event_id: int, db: Session = Depends(deps.get_db)):
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
    db: Session = Depends(deps.get_db),
    title: str = Form(None),
    event_type: str = Form(None),
    description: str = Form(None),
    family_member_id: int = Form(None),
    file: UploadFile = File(None)
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
async def delete_health_event(event_id: int, db: Session = Depends(deps.get_db)):
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
