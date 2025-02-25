from fastapi import APIRouter

from app.api.v1.endpoints import feeds, users

api_router = APIRouter()

# Include routers from endpoints
api_router.include_router(feeds.router, prefix="/feeds", tags=["feeds"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

@api_router.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return {"status": "ok"} 