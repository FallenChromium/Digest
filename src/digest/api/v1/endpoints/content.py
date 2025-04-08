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

    """
    content_repository = ContentRepository(session)

    # Run different search methods and measure their performance
    results = {}

    # 1. Full-text search only
    start_time = time()
    fts_results = content_repository.search_fts_only(query, include_plan=True)
    fts_time = (time() - start_time) * 1000

    fts_plan = fts_results[0].query_plan if fts_results else {}
    results["full_text_search"] = {
        "time_ms": fts_time,
        "results": [
            {
                "id": r.id,
                "title": r.title,
                "rank": r.rank,
                "snippet": r.snippet
            } for r in fts_results[:5]
        ],
        "result_count": len(fts_results),
        "index_usage": fts_plan.get('index_usage', []) if isinstance(fts_plan, dict) else [],
        "scan_type": fts_plan.get('scan_type', 'unknown') if isinstance(fts_plan, dict) else 'unknown',
        "total_cost": fts_plan.get('total_cost', 0) if isinstance(fts_plan, dict) else 0,
        "actual_time": fts_plan.get('actual_time', 0) if isinstance(fts_plan, dict) else 0
    }

    # 2. Trigram search only
    start_time = time()
    trgm_results = content_repository.search_trigram_only(query, similarity_threshold, include_plan=True)
    trgm_time = (time() - start_time) * 1000

    # Extract query plan info
    trgm_plan = trgm_results[0].query_plan if trgm_results else {}
    results["trigram_search"] = {
        "time_ms": trgm_time,
        "results": [
            {
                "id": r.id,
                "title": r.title,
                "content": r.content,
                "similarity": r.similarity
            } for r in trgm_results[:5]
        ],
        "result_count": len(trgm_results),
        "index_usage": trgm_plan.get('index_usage', []) if isinstance(trgm_plan, dict) else [],
        "scan_type": trgm_plan.get('scan_type', 'unknown') if isinstance(trgm_plan, dict) else 'unknown',
        "total_cost": trgm_plan.get('total_cost', 0) if isinstance(trgm_plan, dict) else 0,
        "actual_time": trgm_plan.get('actual_time', 0) if isinstance(trgm_plan, dict) else 0
    }

    # 3. Combined search (current implementation)
    start_time = time()
    combined_results = content_repository.search(query, similarity_threshold, include_plan=True)
    combined_time = (time() - start_time) * 1000

    combined_plan = combined_results[0].query_plan if combined_results else {}
    results["combined_search"] = {
        "time_ms": combined_time,
        "results": [
            {
                "id": str(r.id),
                "title": r.title,
                "rank": r.rank,
            } for r in combined_results[:5]
        ],
        "result_count": len(combined_results),
        "index_usage": combined_plan.get('index_usage', []) if isinstance(combined_plan, dict) else [],
        "scan_type": combined_plan.get('scan_type', 'unknown') if isinstance(combined_plan, dict) else 'unknown',
        "total_cost": combined_plan.get('total_cost', 0) if isinstance(combined_plan, dict) else 0,
        "actual_time": combined_plan.get('actual_time', 0) if isinstance(combined_plan, dict) else 0
    }

    # 4. No index search (LIKE/ILIKE)
    start_time = time()
    no_index_results = content_repository.search_no_index(query, include_plan=True)
    no_index_time = (time() - start_time) * 1000

    no_index_plan = no_index_results[0].query_plan if no_index_results else {}
    results["no_index_search"] = {
        "time_ms": no_index_time,
        "results": [
            {
                "id": r.id,
                "title": r.title
            } for r in no_index_results[:5]
        ],
        "result_count": len(no_index_results),
        "index_usage": no_index_plan.get('index_usage', []) if isinstance(no_index_plan, dict) else [],
        "scan_type": no_index_plan.get('scan_type', 'unknown') if isinstance(no_index_plan, dict) else 'unknown',
        "total_cost": no_index_plan.get('total_cost', 0) if isinstance(no_index_plan, dict) else 0,
        "actual_time": no_index_plan.get('actual_time', 0) if isinstance(no_index_plan, dict) else 0
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

    # Calculate index effectiveness (speedup vs no-index)
    index_effectiveness = {
        method: (no_index_time / time_ms if time_ms > 0 else 0)
        for method, time_ms in times.items()
        if method != "no_index_search"
    }

    # Find most effective index
    most_efficient_index = max(
        index_effectiveness.items(),
        key=lambda x: x[1]
    )[0] if index_effectiveness else "none"

    fastest_method = min(times.items(), key=lambda x: x[1])[0]
    most_results = max(counts.items(), key=lambda x: x[1])[0]

    # Generate detailed analysis
    detailed_analysis = []
    for method, data in results.items():
        if method != "no_index_search":
            speedup = no_index_time / data["time_ms"] if data["time_ms"] > 0 else 0
            detailed_analysis.append(
                f"{method}: {speedup:.1f}x speedup vs no-index, "
                f"using {len(data['index_usage'])} indices"
            )

    return {
        "query": query,
        "results": results,
        "analysis": {
            "fastest_method": fastest_method,
            "most_results": most_results,
            "most_efficient_index": most_efficient_index,
            "index_effectiveness": index_effectiveness,
            "recommendation": (
                "combined_search"
                if combined_time < no_index_time * 0.8
                else "needs_optimization"
            ),
            "detailed_analysis": "\n".join(detailed_analysis),
            "timing_comparison": {
                "vs_no_index": {
                    "fts_speedup": no_index_time / fts_time if fts_time > 0 else 0,
                    "trgm_speedup": no_index_time / trgm_time if trgm_time > 0 else 0,
                    "combined_speedup": no_index_time / combined_time if combined_time > 0 else 0
                }
            }
        }
    }
