import pytest
from fastapi import UploadFile
from io import BytesIO
from app.models.health_event import HealthEvent, EventType
from app.models.family_member import FamilyMember
from datetime import datetime


def test_create_family_member_and_health_event(client, db_session):
    # Create a test family member with all fields from migration
    family_member = FamilyMember(
        name="Jane Doe",
        relation_type="mother",
        date_of_birth="1980-05-15",
        health_score=85,
        notes="Regular exercise, no chronic conditions",
    )
    db_session.add(family_member)
    db_session.commit()
    db_session.refresh(family_member)

    # Store the ID before making the API request
    family_member_id = family_member.id

    # Verify family member was created
    assert family_member_id is not None

    # Create a health event for this family member
    form_data = {
        "title": "Annual Checkup",
        "event_type": EventType.CHECKUP.value,
        "description": "Routine physical examination",
        "family_member_id": str(family_member_id),
        "date_time": datetime(2025, 3, 26, 14, 30, 14).isoformat(),
    }

    # Make the request
    response = client.post("/api/v1/health-events/", data=form_data)

    # Assertions
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["title"] == form_data["title"]
    assert response_data["family_member_id"] == family_member_id
    assert response_data["event_type"] == EventType.CHECKUP.value
    assert response_data["description"] == form_data["description"]


def test_create_health_event_with_file(client, db_session):
    # Create a test family member
    family_member = FamilyMember(
        name="Test Child", relation_type="child", date_of_birth="2020-01-01"
    )
    db_session.add(family_member)
    db_session.commit()
    db_session.refresh(family_member)

    # Create test file
    test_file = BytesIO(b"test file content")
    files = {"file": ("test.pdf", test_file, "application/pdf")}
    form_data = {
        "title": "Vaccination Record",
        "event_type": EventType.MEDICATION.value,
        "description": "Annual vaccination",
        "family_member_id": str(family_member.id),
        "date_time": datetime.now().isoformat(),
    }

    # Make the request
    response = client.post("/api/v1/health-events/", data=form_data, files=files)

    # Assertions
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["title"] == form_data["title"]
    assert response_data["file_path"] is not None


def test_create_health_event_invalid_family_member(client):
    # Test data with non-existent family member
    form_data = {
        "title": "Regular Checkup",
        "event_type": EventType.CHECKUP.value,
        "description": "Annual physical examination",
        "family_member_id": "99999",  # Non-existent ID
        "date_time": datetime.now().isoformat(),
    }

    # Make the request
    response = client.post("/api/v1/health-events/", data=form_data)

    # Assertions
    assert response.status_code == 400


def test_create_health_event_invalid_file_type(client, db_session):
    # Create a test family member
    family_member = FamilyMember(
        name="Test Child", relation_type="child", date_of_birth="2020-01-01"
    )
    db_session.add(family_member)
    db_session.commit()
    db_session.refresh(family_member)

    # Create invalid file type
    test_file = BytesIO(b"test file content")
    files = {"file": ("test.exe", test_file, "application/x-msdownload")}
    form_data = {
        "title": "Vaccination Record",
        "event_type": EventType.MEDICATION.value,
        "description": "Annual vaccination",
        "family_member_id": str(family_member.id),
        "date_time": datetime.now().isoformat(),
    }

    # Make the request
    response = client.post("/api/v1/health-events/", data=form_data, files=files)

    # Assertions
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]
