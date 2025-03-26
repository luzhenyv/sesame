import pytest
from fastapi.testclient import TestClient
from app.models.health_event import HealthEvent
from app.schemas.health_event import HealthEventCreate


def test_create_health_event_success(client, db_session):
    # Arrange
    event_data = {
        "title": "Test Health Event",
        "event_type": "checkup",
        "description": "Test description",
        "family_member_id": 1,
    }

    # Act
    response = client.post("/api/v1/health-events/", data=event_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == event_data["title"]
    assert data["event_type"] == event_data["event_type"]
    assert data["description"] == event_data["description"]
    assert data["family_member_id"] == event_data["family_member_id"]


def test_create_health_event_with_file(client, db_session):
    # Arrange
    event_data = {
        "title": "Test Health Event with File",
        "event_type": "checkup",
        "description": "Test description",
        "family_member_id": 1,
    }
    files = {"file": ("test.jpg", b"test image content", "image/jpeg")}

    # Act
    response = client.post("/api/v1/health-events/", data=event_data, files=files)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == event_data["title"]
    assert data["file_path"] is not None


def test_get_health_events(client, db_session):
    # Arrange
    # Create test events
    event1 = HealthEvent(
        title="Test Event 1",
        event_type="checkup",
        description="Test description 1",
        family_member_id=1,
    )
    event2 = HealthEvent(
        title="Test Event 2",
        event_type="medication",
        description="Test description 2",
        family_member_id=1,
    )
    db_session.add(event1)
    db_session.add(event2)
    db_session.commit()

    # Act
    response = client.get("/api/v1/health-events/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Test Event 1"
    assert data[1]["title"] == "Test Event 2"


def test_get_health_event_by_id(client, db_session):
    # Arrange
    event = HealthEvent(
        title="Test Event",
        event_type="checkup",
        description="Test description",
        family_member_id=1,
    )
    db_session.add(event)
    db_session.commit()

    # Act
    response = client.get(f"/api/v1/health-events/{event.id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Event"
    assert data["id"] == event.id


def test_get_nonexistent_health_event(client, db_session):
    # Act
    response = client.get("/api/v1/health-events/999")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Health event not found"


def test_update_health_event(client, db_session):
    # Arrange
    event = HealthEvent(
        title="Original Title",
        event_type="checkup",
        description="Original description",
        family_member_id=1,
    )
    db_session.add(event)
    db_session.commit()

    update_data = {
        "title": "Updated Title",
        "event_type": "medication",
        "description": "Updated description",
    }

    # Act
    response = client.put(f"/api/v1/health-events/{event.id}", data=update_data)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["event_type"] == "medication"
    assert data["description"] == "Updated description"


def test_delete_health_event(client, db_session):
    # Arrange
    event = HealthEvent(
        title="Test Event",
        event_type="checkup",
        description="Test description",
        family_member_id=1,
    )
    db_session.add(event)
    db_session.commit()

    # Act
    response = client.delete(f"/api/v1/health-events/{event.id}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Health event deleted successfully"

    # Verify event is deleted
    deleted_event = (
        db_session.query(HealthEvent).filter(HealthEvent.id == event.id).first()
    )
    assert deleted_event is None


def test_delete_nonexistent_health_event(client, db_session):
    # Act
    response = client.delete("/api/v1/health-events/999")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Health event not found"
