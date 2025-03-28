from tests.integration.test_base import TestBase
from app.core.config import settings


class TestFiles(TestBase):
    def test_get_existing_image_file(self):
        headers = self.get_auth_headers()
        response = self.client.get(
            f"{settings.API_V1_STR}/files/test.jpg", headers=headers
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"

    def test_get_existing_pdf_file(self):
        headers = self.get_auth_headers()
        response = self.client.get(
            f"{settings.API_V1_STR}/files/test.pdf", headers=headers
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    def test_get_nonexistent_file(self):
        headers = self.get_auth_headers()
        response = self.client.get(
            f"{settings.API_V1_STR}/files/nonexistent.jpg", headers=headers
        )
        assert response.status_code == 404
        assert response.json()["detail"].startswith("File not found")
