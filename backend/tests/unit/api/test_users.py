import pytest
from fastapi import status


def test_create_user(client, test_user_data):
    response = client.post("/api/users/", json=test_user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["full_name"] == test_user_data["full_name"]
    assert "id" in data
    assert "password" not in data


def test_create_user_invalid_email(client):
    invalid_data = {
        "email": "invalid-email",
        "password": "testpassword123",
        "full_name": "Test User",
    }
    response = client.post("/api/users/", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_user(client, test_user_data):
    # First create a user
    create_response = client.post("/api/users/", json=test_user_data)
    user_id = create_response.json()["id"]

    # Then get the user
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["full_name"] == test_user_data["full_name"]
