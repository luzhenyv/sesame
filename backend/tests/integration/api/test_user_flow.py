import pytest
from fastapi import status


def test_complete_user_flow(client, test_user_data):
    # 1. Create a new user
    create_response = client.post("/api/users/", json=test_user_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    user_id = create_response.json()["id"]

    # 2. Get the created user
    get_response = client.get(f"/api/users/{user_id}")
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["email"] == test_user_data["email"]

    # 3. Update the user
    update_data = {"full_name": "Updated Test User"}
    update_response = client.patch(f"/api/users/{user_id}", json=update_data)
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json()["full_name"] == "Updated Test User"

    # 4. Verify the update
    verify_response = client.get(f"/api/users/{user_id}")
    assert verify_response.status_code == status.HTTP_200_OK
    assert verify_response.json()["full_name"] == "Updated Test User"

    # 5. Delete the user
    delete_response = client.delete(f"/api/users/{user_id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # 6. Verify deletion
    verify_deletion = client.get(f"/api/users/{user_id}")
    assert verify_deletion.status_code == status.HTTP_404_NOT_FOUND
