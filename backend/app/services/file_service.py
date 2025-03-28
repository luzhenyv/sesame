import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile

from app.core.config import settings


class FileService:
    def __init__(self):
        self.base_path = Path(settings.ROOT_DIR) / "storage" / "uploads"
        self.image_path = self.base_path / "images"
        self.pdf_path = self.base_path / "pdfs"
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        self.image_path.mkdir(parents=True, exist_ok=True)
        self.pdf_path.mkdir(parents=True, exist_ok=True)

    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename."""
        return os.path.splitext(filename)[1].lower()

    def _is_valid_file_type(self, file_type: str) -> bool:
        """Check if file type is valid (image or PDF)."""
        valid_image_types = {".jpg", ".jpeg", ".png", ".gif"}
        valid_pdf_types = {".pdf"}
        return file_type in valid_image_types or file_type in valid_pdf_types

    def _get_storage_path(self, file_type: str) -> Path:
        """Get appropriate storage path based on file type."""
        if file_type in {".jpg", ".jpeg", ".png", ".gif"}:
            return self.image_path
        elif file_type == ".pdf":
            return self.pdf_path
        raise ValueError(f"Unsupported file type: {file_type}")

    async def save_file(self, file: UploadFile, event_id: str) -> str:
        """Save uploaded file and return the file path."""
        file_extension = self._get_file_extension(file.filename)

        if not self._is_valid_file_type(file_extension):
            raise ValueError(f"Invalid file type: {file_extension}")

        storage_path = self._get_storage_path(file_extension)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{event_id}_{timestamp}{file_extension}"
        file_path = storage_path / filename

        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return str(file_path)
        finally:
            file.file.close()

    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage."""
        try:
            os.remove(file_path)
            return True
        except FileNotFoundError:
            return False

    def get_file_url(self, file_path: str) -> str:
        """Generate a file URL for the stored file."""
        return f"/files/{os.path.basename(file_path)}"


file_service = FileService()