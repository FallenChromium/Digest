from fastapi import APIRouter, HTTPException, status

from digest.retrieval.models import SourceConfig
from digest.retrieval.sources.repository import repository as source_repository
from digest.retrieval.task_manager import task_manager

router = APIRouter()


@router.post("")
async def create_source(config: SourceConfig):
    try:
        source = source_repository.add(config.model_dump())
        task_manager.start_parser(source.config.id)
        return source
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("{source_id}")
async def get_source(source_id: str):
    source = source_repository.get(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID '{source_id}' does not exists",
        )
    return source


@router.get("")
async def get_all_sources():
    return source_repository.get_all()


@router.delete("{source_id}")
async def delete_source(source_id: str):
    result = source_repository.delete(source_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID '{source_id}' does not exists",
        )

    task_manager.stop_parser(source_id)
