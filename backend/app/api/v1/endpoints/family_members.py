from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.family_member import FamilyMember
from app.schemas.family_member import (
    FamilyMemberCreate,
    FamilyMemberUpdate,
    FamilyMemberResponse,
    PaginatedResponse,
)
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


@router.post(
    "/", response_model=FamilyMemberResponse, status_code=status.HTTP_201_CREATED
)
def create_family_member(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    family_member_in: FamilyMemberCreate,
):
    """
    Create a new family member.

    - **name**: Family member's name
    - **relationship**: Relationship to the user (e.g., "child", "spouse", "parent")
    - **date_of_birth**: Family member's date of birth
    - **gender**: Family member's gender
    """
    # Create family member
    db_family_member = FamilyMember(
        **family_member_in.model_dump(), manager_id=current_user.id
    )
    db.add(db_family_member)
    db.commit()
    db.refresh(db_family_member)

    return db_family_member


@router.get("/", response_model=PaginatedResponse)
def get_family_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Get list of family members for the current user.

    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    total = (
        db.query(FamilyMember)
        .filter(FamilyMember.manager_id == current_user.id)
        .count()
    )
    family_members = (
        db.query(FamilyMember)
        .filter(FamilyMember.manager_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return PaginatedResponse(
        items=family_members,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit,
    )


@router.get("/{family_member_id}", response_model=FamilyMemberResponse)
def get_family_member(
    family_member_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific family member by ID.

    - **family_member_id**: UUID of the family member
    """
    family_member = (
        db.query(FamilyMember)
        .filter(
            FamilyMember.id == family_member_id,
            FamilyMember.manager_id == current_user.id,
        )
        .first()
    )
    if not family_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Family member not found"
        )
    return family_member


@router.put("/{family_member_id}", response_model=FamilyMemberResponse)
def update_family_member(
    family_member_id: UUID,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    family_member_in: FamilyMemberUpdate,
):
    """
    Update a family member.

    - **family_member_id**: UUID of the family member to update
    - **name**: Updated name (optional)
    - **relationship**: Updated relationship (optional)
    - **date_of_birth**: Updated date of birth (optional)
    - **gender**: Updated gender (optional)
    """
    family_member = (
        db.query(FamilyMember)
        .filter(
            FamilyMember.id == family_member_id,
            FamilyMember.manager_id == current_user.id,
        )
        .first()
    )
    if not family_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Family member not found"
        )

    update_data = family_member_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(family_member, field, value)

    db.commit()
    db.refresh(family_member)
    return family_member


@router.delete("/{family_member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_family_member(
    family_member_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a family member.

    - **family_member_id**: UUID of the family member to delete
    """
    family_member = (
        db.query(FamilyMember)
        .filter(
            FamilyMember.id == family_member_id,
            FamilyMember.manager_id == current_user.id,
        )
        .first()
    )
    if not family_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Family member not found"
        )

    db.delete(family_member)
    db.commit()
    return None
