from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from digest.config.settings import settings
from digest.api.router import api_router
from digest.database.session import create_db_and_tables
from digest.prepare import prepare
from digest.retrieval.task_manager import task_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    task_manager.start_all_parsers()
    yield
    await task_manager.stop_all_parsers()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    prepare()
    create_db_and_tables()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
