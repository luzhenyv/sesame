from ..test_base import TestBase


class TestFamilyMembers(TestBase):
    def test_create_family_member(self):
        headers = self.get_auth_headers()
        response = self.client.post(
            "/family-members/",
            headers=headers,
            json={
                "name": "Jane Doe",
                "relationship": "child",
                "date_of_birth": "2020-01-01",
                "gender": "female",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Jane Doe"
        assert data["relationship"] == "child"

    def test_get_family_members(self):
        headers = self.get_auth_headers()
        # Create a family member first
        self.client.post(
            "/family-members/",
            headers=headers,
            json={
                "name": "Jane Doe",
                "relationship": "child",
                "date_of_birth": "2020-01-01",
                "gender": "female",
            },
        )

        response = self.client.get("/family-members/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Jane Doe"

    def test_get_family_member(self):
        headers = self.get_auth_headers()
        # Create a family member first
        create_response = self.client.post(
            "/family-members/",
            headers=headers,
            json={
                "name": "Jane Doe",
                "relationship": "child",
                "date_of_birth": "2020-01-01",
                "gender": "female",
            },
        )
        family_member_id = create_response.json()["id"]

        response = self.client.get(
            f"/family-members/{family_member_id}", headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Doe"

    def test_update_family_member(self):
        headers = self.get_auth_headers()
        # Create a family member first
        create_response = self.client.post(
            "/family-members/",
            headers=headers,
            json={
                "name": "Jane Doe",
                "relationship": "child",
                "date_of_birth": "2020-01-01",
                "gender": "female",
            },
        )
        family_member_id = create_response.json()["id"]

        response = self.client.put(
            f"/family-members/{family_member_id}",
            headers=headers,
            json={
                "name": "Jane Smith",
                "relationship": "child",
                "date_of_birth": "2020-01-01",
                "gender": "female",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Smith"

    def test_delete_family_member(self):
        headers = self.get_auth_headers()
        # Create a family member first
        create_response = self.client.post(
            "/family-members/",
            headers=headers,
            json={
                "name": "Jane Doe",
                "relationship": "child",
                "date_of_birth": "2020-01-01",
                "gender": "female",
            },
        )
        family_member_id = create_response.json()["id"]

        response = self.client.delete(
            f"/family-members/{family_member_id}", headers=headers
        )
        assert response.status_code == 204
