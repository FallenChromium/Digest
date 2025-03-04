from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import List, Dict, Any
from time import time
from digest.database.repositories.content import ContentRepository
from digest.database.session import get_session

router = APIRouter()


@router.get("")
async def get_content(page: int = 1, page_size: int = 10, session: Session = Depends(get_session)):
    content_repository = ContentRepository(session)
    return content_repository.get_all_paged(page, page_size)

@router.get("/search")
async def search_content(query: str, session: Session = Depends(get_session)):
    content_repository = ContentRepository(session)
    return content_repository.search(query)

@router.get("/search/benchmark")
async def benchmark_search(
    query: str,
    similarity_threshold: float = Query(default=0.3, ge=0.0, le=1.0),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Benchmark different search approaches and return timing and relevance metrics.
    
    Returns:
    {
        "query": str,
        "results": {
            "full_text_search": {
                "time_ms": float,
                "results": List[Dict],
                "result_count": int
            },
            "trigram_search": {...},
            "combined_search": {...},
            "no_index_search": {...}
        },
        "analysis": {
            "fastest_method": str,
            "most_results": str,
            "recommendation": str
        }
    }
    """
    content_repository = ContentRepository(session)
    
    # Run different search methods and measure their performance
    results = {}
    
    # 1. Full-text search only
    start_time = time()
    fts_results = content_repository.search_fts_only(query)
    fts_time = (time() - start_time) * 1000
    results["full_text_search"] = {
        "time_ms": fts_time,
        "results": [
            {
                "id": str(r.id),
                "title": r.title,
                "rank": r.rank,
                "snippet": r.snippet
            } for r in fts_results[:5]
        ],
        "result_count": len(fts_results)
    }
    
    # 2. Trigram search only
    start_time = time()
    trgm_results = content_repository.search_trigram_only(query, similarity_threshold)
    trgm_time = (time() - start_time) * 1000
    results["trigram_search"] = {
        "time_ms": trgm_time,
        "results": [
            {
                "id": str(r.id),
                "title": r.title,
                "similarity": r.similarity
            } for r in trgm_results[:5]
        ],
        "result_count": len(trgm_results)
    }
    
    # 3. Combined search (current implementation)
    start_time = time()
    combined_results = content_repository.search(query, similarity_threshold)
    combined_time = (time() - start_time) * 1000
    results["combined_search"] = {
        "time_ms": combined_time,
        "results": [
            {
                "id": str(r.id),
                "title": r.title,
                "rank": getattr(r, 'rank', None),
                "similarity": getattr(r, 'similarity', None)
            } for r in combined_results[:5]
        ],
        "result_count": len(combined_results)
    }
    
    # 4. No index search (LIKE/ILIKE)
    start_time = time()
    no_index_results = content_repository.search_no_index(query)
    no_index_time = (time() - start_time) * 1000
    results["no_index_search"] = {
        "time_ms": no_index_time,
        "results": [
            {
                "id": str(r.id),
                "title": r.title
            } for r in no_index_results[:5]
        ],
        "result_count": len(no_index_results)
    }
    
    # Analysis
    times = {
        "full_text_search": fts_time,
        "trigram_search": trgm_time,
        "combined_search": combined_time,
        "no_index_search": no_index_time
    }
    
    counts = {
        "full_text_search": len(fts_results),
        "trigram_search": len(trgm_results),
        "combined_search": len(combined_results),
        "no_index_search": len(no_index_results)
    }
    
    fastest_method = min(times.items(), key=lambda x: x[1])[0]
    most_results = max(counts.items(), key=lambda x: x[1])[0]
    
    return {
        "query": query,
        "results": results,
        "analysis": {
            "fastest_method": fastest_method,
            "most_results": most_results,
            "recommendation": "combined_search" if combined_time < no_index_time * 0.8 else "needs_optimization",
            "timing_comparison": {
                "vs_no_index": {
                    "fts_speedup": no_index_time / fts_time if fts_time > 0 else 0,
                    "trgm_speedup": no_index_time / trgm_time if trgm_time > 0 else 0,
                    "combined_speedup": no_index_time / combined_time if combined_time > 0 else 0
                }
            }
        }
    }

