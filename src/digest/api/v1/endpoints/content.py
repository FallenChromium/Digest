from fastapi import APIRouter, Depends
from sqlmodel import Session
from digest.database.repositories.content import ContentRepository
from digest.database.session import get_session

router = APIRouter()


@router.get("/content")
async def get_content(page: int = 1, page_size: int = 10, session: Session = Depends(get_session)):
    content_repository = ContentRepository(session)
    return content_repository.get_all_paged(page, page_size)

@router.get("/content/search")
async def search_content(query: str, session: Session = Depends(get_session)):
    content_repository = ContentRepository(session)
    return content_repository.search(query)

