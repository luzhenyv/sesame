from fastapi import APIRouter
from app.api.v1.endpoints import health_events, files, auth, family_members

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    family_members.router, prefix="/family-members", tags=["family-members"]
)
api_router.include_router(
    health_events.router, prefix="/health-events", tags=["health-events"]
)
api_router.include_router(files.router, prefix="/files", tags=["files"])
