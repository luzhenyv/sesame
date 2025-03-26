import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os

from tests.conftest import TEST_SERVER_URL


def test_get_existing_image_file(client):

    # Act
    response = client.get(f"{TEST_SERVER_URL}/api/v1/files/test.jpg")

    # Assert
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"


def test_get_existing_pdf_file(client):
    # Act
    response = client.get(f"{TEST_SERVER_URL}/api/v1/files/test.pdf")

    # Assert
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_get_nonexistent_file(client):
    # Act
    response = client.get(f"{TEST_SERVER_URL}/api/v1/files/nonexistent.jpg")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"].startswith("File not found")
