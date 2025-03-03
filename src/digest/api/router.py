from fastapi import APIRouter

from digest.api.v1.endpoints import sources

api_router = APIRouter()
api_router.include_router(sources.router, prefix="/sources", tags=["Sources"])


@api_router.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return {"status": "ok"}
