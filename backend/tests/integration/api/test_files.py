from tests.integration.test_base import TestBase


class TestFiles(TestBase):
    def test_get_existing_image_file(self):
        # Act
        response = self.client.get("/files/test.jpg")

        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"

    def test_get_existing_pdf_file(self):
        # Act
        response = self.client.get("/files/test.pdf")

        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    def test_get_nonexistent_file(self):
        # Act
        response = self.client.get("/files/nonexistent.jpg")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"].startswith("File not found")
