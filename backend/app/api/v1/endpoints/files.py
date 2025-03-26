from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import os

router = APIRouter()


@router.get("/{filename}", summary="Get uploaded file")
async def get_file(filename: str):
    """
    Serve uploaded files.

    - **filename**: Name of the file to retrieve
    """
    # Check both image and PDF directories
    image_path = Path("storage/uploads/images") / filename
    pdf_path = Path("storage/uploads/pdfs") / filename

    if image_path.exists():
        return FileResponse(str(image_path))
    elif pdf_path.exists():
        return FileResponse(str(pdf_path))

    raise HTTPException(status_code=404, detail="File not found")
