import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0",
    description="Sesame Health API - Version 1.0.0",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router with version prefix
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to Sesame Health API"}


if __name__ == "__main__":
    import uvicorn
    from uvicorn.config import LOGGING_CONFIG

    LOGGING_CONFIG["formatters"]["default"][
        "fmt"
    ] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=LOGGING_CONFIG)
