import pytest
from fastapi import UploadFile
from io import BytesIO
from app.models.health_event import HealthEvent, EventType
from app.models.family_member import FamilyMember, MemberType
from datetime import datetime, timedelta
from tests.integration.test_base import TestBase, client, db_session
import uuid
from app.core.config import settings


class TestHealthEvents(TestBase):
    def test_create_family_member_and_health_event(self, client, db_session):
        # Register and get a user
        headers = self.get_auth_headers()
        user_response = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
        user_id = user_response.json()["id"]

        # Create a test family member with all fields from migration
        family_member = FamilyMember(
            name="Jane Doe",
            member_type=MemberType.HUMAN,
            relation_type="mother",
            date_of_birth="1980-05-15",
            health_score=85,
            notes="Regular exercise, no chronic conditions",
            manager_id=user_id,
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

        # Make the request with auth headers
        response = client.post(
            "/api/v1/health-events/", data=form_data, headers=headers
        )

        # Assertions
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["title"] == form_data["title"]
        assert response_data["family_member_id"] == str(family_member_id)
        assert response_data["event_type"] == EventType.CHECKUP.value
        assert response_data["description"] == form_data["description"]

    def test_create_health_event_with_file(self, client, db_session):
        # Register and get a user
        headers = self.get_auth_headers()
        user_response = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
        user_id = user_response.json()["id"]

        # Create a test family member
        family_member = FamilyMember(
            name="Test Child",
            member_type=MemberType.HUMAN,
            relation_type="child",
            date_of_birth="2020-01-01",
            manager_id=user_id,
        )
        db_session.add(family_member)
        db_session.commit()
        db_session.refresh(family_member)

        # Create test file
        test_file = BytesIO(b"test file content")
        files = {"files": ("test.pdf", test_file, "application/pdf")}
        form_data = {
            "title": "Vaccination Record",
            "event_type": EventType.MEDICATION.value,
            "description": "Annual vaccination",
            "family_member_id": str(family_member.id),
            "date_time": datetime.now().isoformat(),
        }

        # Make the request with auth headers
        response = client.post(
            "/api/v1/health-events/", data=form_data, files=files, headers=headers
        )

        # Assertions
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["title"] == form_data["title"]
        assert response_data["file_paths"] is not None
        assert len(response_data["file_paths"]) > 0

    def test_create_health_event_invalid_family_member(self, client):
        # Test data with non-existent family member
        form_data = {
            "title": "Regular Checkup",
            "event_type": EventType.CHECKUP.value,
            "description": "Annual physical examination",
            "family_member_id": "99999",  # Non-existent ID
            "date_time": datetime.now().isoformat(),
        }

        # Make the request with auth headers
        headers = self.get_auth_headers()
        response = client.post(
            "/api/v1/health-events/", data=form_data, headers=headers
        )

        # Assertions
        assert response.status_code == 422  # Validation error for invalid UUID format

    def test_create_health_event_invalid_file_type(self, client, db_session):
        # Register and get a user
        headers = self.get_auth_headers()
        user_response = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
        user_id = user_response.json()["id"]

        # Create a test family member
        family_member = FamilyMember(
            name="Test Child",
            member_type=MemberType.HUMAN,
            relation_type="child",
            date_of_birth="2020-01-01",
            manager_id=user_id,
        )
        db_session.add(family_member)
        db_session.commit()
        db_session.refresh(family_member)

        # Create invalid file type
        test_file = BytesIO(b"test file content")
        files = {"files": ("test.exe", test_file, "application/x-msdownload")}
        form_data = {
            "title": "Vaccination Record",
            "event_type": EventType.MEDICATION.value,
            "description": "Annual vaccination",
            "family_member_id": str(family_member.id),
            "date_time": datetime.now().isoformat(),
        }

        # Make the request with auth headers
        response = client.post(
            "/api/v1/health-events/", data=form_data, files=files, headers=headers
        )

        # Assertions
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_get_health_events_pagination(self, client, db_session):
        # Register and get a user
        headers = self.get_auth_headers()
        user_response = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
        user_id = user_response.json()["id"]

        db_session.query(HealthEvent).delete()
        db_session.query(FamilyMember).delete()
        db_session.commit()
        # Create a test family member
        family_member = FamilyMember(
            name="Test Parent",
            member_type=MemberType.HUMAN,
            relation_type="parent",
            date_of_birth="1980-01-01",
            manager_id=user_id,
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

            client.post("/api/v1/health-events/", data=form_data, headers=headers)

        # Test first page
        response = client.get("/api/v1/health-events/?page=1&size=10", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["size"] == 10

        # Test second page
        response = client.get("/api/v1/health-events/?page=2&size=10", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2

    def test_get_health_events_filtering(self, client, db_session):
        # Register and get a user
        headers = self.get_auth_headers()
        user_response = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
        user_id = user_response.json()["id"]

        db_session.query(HealthEvent).delete()
        db_session.query(FamilyMember).delete()
        db_session.commit()
        # Create test data
        family_member = FamilyMember(
            name="Test Child",
            member_type=MemberType.HUMAN,
            relation_type="child",
            date_of_birth="2020-01-01",
            manager_id=user_id,
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
            client.post("/api/v1/health-events/", data=event, headers=headers)

        # Test filtering by event type
        response = client.get(
            "/api/v1/health-events/?event_type=checkup", headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["event_type"] == EventType.CHECKUP.value

    def test_get_health_events_date_filtering(self, client, db_session):
        # Register and get a user
        headers = self.get_auth_headers()
        user_response = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
        user_id = user_response.json()["id"]

        # Create test data
        family_member = FamilyMember(
            name="Test Patient",
            member_type=MemberType.HUMAN,
            relation_type="patient",
            date_of_birth="1990-01-01",
            manager_id=user_id,
        )
        db_session.add(family_member)
        db_session.commit()

        # Create events with different dates
        events = [
            {
                "title": "Past Event",
                "event_type": EventType.CHECKUP.value,
                "description": "Old checkup",
                "family_member_id": family_member.id,
                "date_time": datetime(2023, 1, 1, 12, 0),
            },
            {
                "title": "Present Event",
                "event_type": EventType.MEDICATION.value,
                "description": "Current medication",
                "family_member_id": family_member.id,
                "date_time": datetime(2023, 6, 1, 12, 0),
            },
            {
                "title": "Future Event",
                "event_type": EventType.SYMPTOM.value,
                "description": "Future symptom",
                "family_member_id": family_member.id,
                "date_time": datetime(2025, 1, 1, 12, 0),
            },
        ]
        for event in events:
            client.post("/api/v1/health-events/", data=event, headers=headers)

        # Test filtering by date range
        start_date = datetime(2022, 12, 31).isoformat()
        end_date = datetime(2024, 1, 2).isoformat()
        response = client.get(
            f"/api/v1/health-events/?start_date={start_date}&end_date={end_date}",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

    def test_get_health_events_search(self, client, db_session):
        # Register and get a user
        headers = self.get_auth_headers()
        user_response = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
        user_id = user_response.json()["id"]

        db_session.query(HealthEvent).delete()
        db_session.query(FamilyMember).delete()
        db_session.commit()
        # Create test data
        family_member = FamilyMember(
            name="Test Person",
            member_type=MemberType.HUMAN,
            relation_type="other",
            date_of_birth="1995-01-01",
            manager_id=user_id,
        )
        db_session.add(family_member)
        db_session.commit()

        # Create events with different titles
        events = [
            {
                "title": "Doctor Visit",
                "event_type": EventType.CHECKUP.value,
                "description": "Regular checkup with doctor",
                "family_member_id": family_member.id,
                "date_time": datetime(2024, 1, 1, 12, 0),
            },
            {
                "title": "Pharmacy Visit",
                "event_type": EventType.MEDICATION.value,
                "description": "Picking up medicine",
                "family_member_id": family_member.id,
                "date_time": datetime(2024, 1, 2, 12, 0),
            },
        ]
        for event in events:
            client.post("/api/v1/health-events/", data=event, headers=headers)

        # Test search by title
        response = client.get("/api/v1/health-events/?search=doctor", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert "doctor" in data["items"][0]["title"].lower()

    def test_get_health_events_combined_filters(self, client, db_session):
        # Register and get a user
        headers = self.get_auth_headers()
        user_response = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
        user_id = user_response.json()["id"]

        db_session.query(HealthEvent).delete()
        db_session.query(FamilyMember).delete()
        db_session.commit()
        # Create test data
        family_member = FamilyMember(
            name="Test Patient",
            member_type=MemberType.HUMAN,
            relation_type="patient",
            date_of_birth="1990-01-01",
            manager_id=user_id,
        )
        db_session.add(family_member)
        db_session.commit()

        # Create events with different attributes
        events = [
            {
                "title": "Morning Checkup",
                "event_type": EventType.CHECKUP.value,
                "description": "Early morning checkup",
                "family_member_id": family_member.id,
                "date_time": datetime(2024, 1, 1, 9, 0),
            },
            {
                "title": "Evening Medication",
                "event_type": EventType.MEDICATION.value,
                "description": "Night medication",
                "family_member_id": family_member.id,
                "date_time": datetime(2024, 1, 1, 20, 0),
            },
        ]
        for event in events:
            client.post("/api/v1/health-events/", data=event, headers=headers)

        # Test combined filters
        start_date = datetime(2024, 1, 1, 0, 0).isoformat()
        end_date = datetime(2024, 1, 1, 12, 0).isoformat()
        response = client.get(
            f"/api/v1/health-events/?event_type=CHECKUP&start_date={start_date}&end_date={end_date}",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Morning Checkup"

    def test_get_health_events_edge_cases(self, client, db_session):
        # Clean up existing records
        db_session.query(HealthEvent).delete()
        db_session.query(FamilyMember).delete()
        db_session.commit()

        # Test empty result with auth headers
        headers = self.get_auth_headers()
        response = client.get("/api/v1/health-events/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0
