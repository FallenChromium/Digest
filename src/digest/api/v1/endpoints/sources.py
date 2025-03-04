from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from digest.database.models.source import Source
from digest.database.repositories.sources import SourceRepository
from digest.database.session import get_session
from digest.retrieval.parsers.base import ParserRegistry
from digest.retrieval.task_manager import task_manager

router = APIRouter()


@router.post("")
async def create_source(config: Source, session: Session = Depends(get_session)
):
    source_repository = SourceRepository(session)
    try:
        source = source_repository.create(config)
        task_manager.start_parser(source.id)
        return source
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{source_id}")
async def get_source(source_id: str, session: Session = Depends(get_session)):
    source_repository = SourceRepository(session)
    source = source_repository.get_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID '{source_id}' does not exists",
        )
    return source


@router.get("")
async def get_all_sources(session: Session = Depends(get_session)):
    source_repository = SourceRepository(session)
    return source_repository.get_all()


@router.delete("/{source_id}")
async def delete_source(source_id: str, session: Session = Depends(get_session)):
    source_repository = SourceRepository(session)
    result = source_repository.delete(source_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID '{source_id}' does not exists",
        )

    task_manager.stop_parser(source_id)

# uh, that's probably not per REST spec but I don't want to duplicate the source id in the body
@router.put("")
async def update_source(source: Source, session: Session = Depends(get_session)):
    source_repository = SourceRepository(session)
    source = source_repository.update(source)
    return source

@router.patch("/{source_id}")
async def patch_source(source_id: str, source_new: Source, session: Session = Depends(get_session)):
    source_repository = SourceRepository(session)
    source = source_repository.get_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID '{source_id}' does not exists",
        )
    for key, value in source_new.model_dump().items():
        if not key == "id": 
            setattr(source, key, value)
    source = source_repository.update(source)
    return source


@router.get("/{source_id}/test")
async def test_source(source_id: str, session: Session = Depends(get_session)):
    source_repository = SourceRepository(session)
    source = source_repository.get_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID '{source_id}' does not exists",
        )
    print(ParserRegistry.list_parsers())
    parser = ParserRegistry.get_parser(source.parser_id)
    return await parser(source.id, source.config).test_connection()
