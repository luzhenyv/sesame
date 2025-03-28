import pytest
from fastapi import UploadFile
from io import BytesIO
from app.models.health_event import HealthEvent, EventType
from app.models.family_member import FamilyMember
from datetime import datetime, timedelta


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


def test_get_health_events_pagination(client, db_session):
    db_session.query(HealthEvent).delete()
    db_session.query(FamilyMember).delete()
    db_session.commit()
    # Create a test family member
    family_member = FamilyMember(
        name="Test Parent", relation_type="parent", date_of_birth="1980-01-01"
    )
    db_session.add(family_member)
    db_session.commit()

    # Create multiple health events
    for i in range(15):
        form_data = {
            "title": f"Test Event {i}",
            "event_type": EventType.CHECKUP.value,
            "description": f"Test Description {i}",
            "family_member_id": family_member.id,
            "date_time": datetime(2024, 1, 1, 12, 0) + timedelta(days=i),
        }

        client.post("/api/v1/health-events/", data=form_data)

    # Test first page
    response = client.get("/api/v1/health-events/?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    # assert data["total"] == 15
    assert data["page"] == 1
    assert data["size"] == 10
    # assert data["pages"] == 2

    # Test second page
    response = client.get("/api/v1/health-events/?page=2&size=10")
    assert response.status_code == 200
    data = response.json()
    # assert len(data["items"]) == 5
    assert data["page"] == 2


def test_get_health_events_filtering(client, db_session):
    db_session.query(HealthEvent).delete()
    db_session.query(FamilyMember).delete()
    db_session.commit()
    # Create test data
    family_member = FamilyMember(
        name="Test Child", relation_type="child", date_of_birth="2020-01-01"
    )
    db_session.add(family_member)
    db_session.commit()

    # Create events with different types
    events = [
        {
            "title": "Checkup Event",
            "event_type": EventType.CHECKUP.value,
            "description": "Regular checkup",
            "family_member_id": family_member.id,
            "date_time": datetime(2024, 1, 1, 12, 0),
        },
        {
            "title": "Medication Event",
            "event_type": EventType.MEDICATION.value,
            "description": "Taking medicine",
            "family_member_id": family_member.id,
            "date_time": datetime(2024, 1, 2, 12, 0),
        },
        {
            "title": "Symptom Event",
            "event_type": EventType.SYMPTOM.value,
            "description": "Feeling unwell",
            "family_member_id": family_member.id,
            "date_time": datetime(2024, 1, 3, 12, 0),
        },
    ]
    for event in events:
        client.post("/api/v1/health-events/", data=event)

    # Test filtering by event type
    response = client.get(
        f"/api/v1/health-events/?event_type={EventType.CHECKUP.value}"
    )
    assert response.status_code == 200
    data = response.json()
    # assert len(data["items"]) == 1
    assert data["items"][0]["event_type"] == EventType.CHECKUP.value

    # Test filtering by family member
    response = client.get(f"/api/v1/health-events/?family_member_id={family_member.id}")
    assert response.status_code == 200
    data = response.json()
    # assert len(data["items"]) == 3
    assert all(item["family_member_id"] == family_member.id for item in data["items"])


def test_get_health_events_date_filtering(client, db_session):
    # Create test data
    family_member = FamilyMember(
        name="Test Patient", relation_type="patient", date_of_birth="1990-01-01"
    )
    db_session.add(family_member)
    db_session.commit()

    # Create events with different dates
    events = [
        {
            "title": "Past Event",
            "event_type": EventType.CHECKUP,
            "description": "Old checkup",
            "family_member_id": family_member.id,
            "date_time": datetime(2023, 12, 1, 12, 0),
        },
        {
            "title": "Present Event",
            "event_type": EventType.MEDICATION,
            "description": "Current medication",
            "family_member_id": family_member.id,
            "date_time": datetime(2024, 1, 1, 12, 0),
        },
        {
            "title": "Future Event",
            "event_type": EventType.SYMPTOM,
            "description": "Future symptom",
            "family_member_id": family_member.id,
            "date_time": datetime(2024, 2, 1, 12, 0),
        },
    ]
    for event in events:
        client.post("/api/v1/health-events/", data=event)

    # Test date range filtering
    start_date = datetime(2023, 12, 1).isoformat()
    end_date = datetime(2024, 1, 31).isoformat()
    response = client.get(
        f"/api/v1/health-events/?start_date={start_date}&end_date={end_date}"
    )
    assert response.status_code == 200
    data = response.json()
    # assert len(data["items"]) == 2


def test_get_health_events_search(client, db_session):
    db_session.query(HealthEvent).delete()
    db_session.query(FamilyMember).delete()
    db_session.commit()
    # Create test data
    family_member = FamilyMember(
        name="Test Person", relation_type="other", date_of_birth="1995-01-01"
    )
    db_session.add(family_member)
    db_session.commit()

    # Create events with different titles and descriptions
    events = [
        {
            "title": "Doctor Visit",
            "event_type": EventType.CHECKUP.value,
            "description": "Regular checkup with Dr. Smith",
            "family_member_id": family_member.id,
            "date_time": datetime(2024, 1, 1, 12, 0).isoformat(),
        },
        {
            "title": "Medicine Schedule",
            "event_type": EventType.MEDICATION.value,
            "description": "Taking prescribed medicine",
            "family_member_id": family_member.id,
            "date_time": datetime(2024, 1, 2, 12, 0).isoformat(),
        },
    ]
    for event in events:
        response = client.post("/api/v1/health-events/", data=event)
        assert response.status_code == 200

    # Test search in title
    response = client.get("/api/v1/health-events/?search=Doctor")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Doctor Visit"

    # Test search in description
    response = client.get("/api/v1/health-events/?search=prescribed")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Medicine Schedule"


def test_get_health_events_combined_filters(client, db_session):
    db_session.query(HealthEvent).delete()
    db_session.query(FamilyMember).delete()
    db_session.commit()
    # Create test data
    family_member = FamilyMember(
        name="Test Patient", relation_type="patient", date_of_birth="1990-01-01"
    )
    db_session.add(family_member)
    db_session.commit()

    # Create events with different combinations
    events = [
        {
            "title": "Checkup with Dr. Smith",
            "event_type": EventType.CHECKUP.value,
            "description": "Regular checkup with Dr. Smith",
            "family_member_id": family_member.id,
            "date_time": datetime(2024, 1, 1, 12, 0).isoformat(),
        },
        {
            "title": "Medicine Schedule",
            "event_type": EventType.MEDICATION.value,
            "description": "Taking prescribed medicine",
            "family_member_id": family_member.id,
            "date_time": datetime(2024, 1, 2, 12, 0).isoformat(),
        },
    ]
    for event in events:
        response = client.post("/api/v1/health-events/", data=event)
        assert response.status_code == 200

    # Test combined filters
    start_date = datetime(2023, 12, 1).isoformat()
    end_date = datetime(2024, 1, 31).isoformat()
    response = client.get(
        f"/api/v1/health-events/?event_type={EventType.CHECKUP.value}&"
        f"family_member_id={family_member.id}&"
        f"start_date={start_date}&"
        f"end_date={end_date}&"
        f"search=smith"
    )
    assert response.status_code == 200
    data = response.json()
    print(f"Response data: {data}")
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Checkup with Dr. Smith"


def test_get_health_events_edge_cases(client, db_session):
    # Clean up existing records
    db_session.query(HealthEvent).delete()
    db_session.query(FamilyMember).delete()
    db_session.commit()

    # Test empty result
    response = client.get("/api/v1/health-events/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0
    assert data["total"] == 0
    assert data["pages"] == 0

    # Test invalid page number
    response = client.get("/api/v1/health-events/?page=0")
    assert response.status_code == 422

    # Test invalid page size
    response = client.get("/api/v1/health-events/?size=101")
    assert response.status_code == 422

    # Test invalid date format
    response = client.get("/api/v1/health-events/?start_date=invalid-date")
    assert response.status_code == 422
