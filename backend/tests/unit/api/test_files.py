import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os


def test_get_existing_image_file(client, tmp_path):
    # Arrange
    # Create test image file
    image_dir = tmp_path / "storage" / "uploads" / "images"
    image_dir.mkdir(parents=True)
    test_image = image_dir / "test.jpg"
    test_image.write_bytes(b"test image content")

    # Act
    response = client.get("/api/v1/files/test.jpg")

    # Assert
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"


def test_get_existing_pdf_file(client, tmp_path):
    # Arrange
    # Create test PDF file
    pdf_dir = tmp_path / "storage" / "uploads" / "pdfs"
    pdf_dir.mkdir(parents=True)
    test_pdf = pdf_dir / "test.pdf"
    test_pdf.write_bytes(b"test pdf content")

    # Act
    response = client.get("/api/v1/files/test.pdf")

    # Assert
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_get_nonexistent_file(client):
    # Act
    response = client.get("/api/v1/files/nonexistent.jpg")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"
