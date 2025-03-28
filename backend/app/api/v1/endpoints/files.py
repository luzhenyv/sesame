from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.file_service import file_service

router = APIRouter()


@router.get("/{filename}", summary="Get uploaded file")
async def get_file(filename: str):
    """
    Serve uploaded files.

    - **filename**: Name of the file to retrieve
    """
    # Check both image and PDF directories
    image_path = file_service.image_path / filename
    pdf_path = file_service.pdf_path / filename

    if image_path.exists():
        return FileResponse(str(image_path))
    elif pdf_path.exists():
        return FileResponse(str(pdf_path))

    raise HTTPException(
        status_code=404, detail=f"File not found, image_path: {image_path}, pdf_path: {pdf_path}"
    )
