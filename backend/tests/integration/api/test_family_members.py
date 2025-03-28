from tests.integration.test_base import TestBase
from app.core.config import settings
from app.models.family_member import MemberType


class TestFamilyMembers(TestBase):
    def test_create_family_member(self):
        headers = self.get_auth_headers()
        response = self.client.post(
            f"{settings.API_V1_STR}/family-members/",
            headers=headers,
            json={
                "name": "John Doe",
                "member_type": MemberType.HUMAN,
                "relation_type": "father",
                "date_of_birth": "1980-01-01",
                "health_score": 90,
                "notes": "Healthy individual",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["relation_type"] == "father"
        assert data["date_of_birth"] == "1980-01-01"
        assert data["member_type"] == MemberType.HUMAN
        assert data["health_score"] == 90
        assert data["notes"] == "Healthy individual"

    def test_get_family_members(self):
        headers = self.get_auth_headers()
        # Create a family member first
        self.client.post(
            f"{settings.API_V1_STR}/family-members/",
            headers=headers,
            json={
                "name": "John Doe",
                "member_type": MemberType.HUMAN,
                "relation_type": "father",
                "date_of_birth": "1980-01-01",
                "health_score": 90,
                "notes": "Healthy individual",
            },
        )

        # Get all family members
        response = self.client.get(
            f"{settings.API_V1_STR}/family-members/", headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["items"], list)
        assert len(data["items"]) > 0
        assert data["items"][0]["name"] == "John Doe"
        assert data["total"] > 0
        assert data["page"] == 1
        assert data["size"] == 100
        assert data["pages"] > 0

    def test_get_family_member(self):
        headers = self.get_auth_headers()
        # Create a family member first
        create_response = self.client.post(
            f"{settings.API_V1_STR}/family-members/",
            headers=headers,
            json={
                "name": "John Doe",
                "member_type": MemberType.HUMAN,
                "relation_type": "father",
                "date_of_birth": "1980-01-01",
                "health_score": 90,
                "notes": "Healthy individual",
            },
        )
        family_member_id = create_response.json()["id"]

        # Get the specific family member
        response = self.client.get(
            f"{settings.API_V1_STR}/family-members/{family_member_id}", headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == family_member_id
        assert data["name"] == "John Doe"

    def test_update_family_member(self):
        headers = self.get_auth_headers()
        # Create a family member first
        create_response = self.client.post(
            f"{settings.API_V1_STR}/family-members/",
            headers=headers,
            json={
                "name": "John Doe",
                "member_type": MemberType.HUMAN,
                "relation_type": "father",
                "date_of_birth": "1980-01-01",
                "health_score": 90,
                "notes": "Healthy individual",
            },
        )
        family_member_id = create_response.json()["id"]

        # Update the family member
        response = self.client.put(
            f"{settings.API_V1_STR}/family-members/{family_member_id}",
            headers=headers,
            json={
                "name": "John Smith",
                "member_type": MemberType.HUMAN,
                "relation_type": "father",
                "date_of_birth": "1980-01-01",
                "health_score": 95,
                "notes": "Very healthy individual",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == family_member_id
        assert data["name"] == "John Smith"
        assert data["health_score"] == 95
        assert data["notes"] == "Very healthy individual"

    def test_delete_family_member(self):
        headers = self.get_auth_headers()
        # Create a family member first
        create_response = self.client.post(
            f"{settings.API_V1_STR}/family-members/",
            headers=headers,
            json={
                "name": "John Doe",
                "member_type": MemberType.HUMAN,
                "relation_type": "father",
                "date_of_birth": "1980-01-01",
                "health_score": 90,
                "notes": "Healthy individual",
            },
        )
        family_member_id = create_response.json()["id"]

        # Delete the family member
        response = self.client.delete(
            f"{settings.API_V1_STR}/family-members/{family_member_id}", headers=headers
        )
        assert response.status_code == 204

        # Verify the family member is deleted
        get_response = self.client.get(
            f"{settings.API_V1_STR}/family-members/{family_member_id}", headers=headers
        )
        assert get_response.status_code == 404
