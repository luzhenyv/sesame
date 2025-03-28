from tests.integration.test_base import TestBase


class TestAuth(TestBase):
    def test_register_user(self):
        response = self.client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
                "full_name": "Test User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert "hashed_password" not in data

    def test_register_duplicate_user(self):
        # Register first user
        self.client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
                "full_name": "Test User",
            },
        )

        # Try to register same email
        response = self.client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
                "full_name": "Test User",
            },
        )
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_login(self):
        # Register user first
        self.client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
                "full_name": "Test User",
            },
        )

        # Login
        response = self.client.post(
            "/auth/token",
            data={"username": "test@example.com", "password": "testpassword123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self):
        response = self.client.post(
            "/auth/token",
            data={"username": "wrong@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_logout(self):
        # Register and login first
        self.client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
                "full_name": "Test User",
            },
        )

        login_response = self.client.post(
            "/auth/token",
            data={"username": "test@example.com", "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # Test logout
        response = self.client.post(
            "/auth/logout", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"
