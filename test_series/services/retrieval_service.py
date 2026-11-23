"""
Hybrid Retrieval Service for UPSC RAG Pipeline.
Retrieves subject-specific study material chunks and performs reranking.
"""
from typing import List, Dict, Any, Optional
from test_series.services.vector_store_service import query_vector_store
from test_series.services.reranking_service import rerank_chunks

def retrieve_context_for_subject(
    subject: str,
    topic: Optional[str] = None,
    difficulty: str = "Medium",
    top_k: int = 4
) -> List[Dict[str, Any]]:
    """
    Retrieve and rerank relevant study material chunks for question generation.
    Strictly isolated to the target subject.
    """
    search_query = topic if topic else f"UPSC Core Principles and Concepts in {subject.replace('_', ' ')}"
    
    # Retrieve top 8 candidates from vector store
    candidates = query_vector_store(
        query_text=search_query,
        subject=subject,
        source_type="study_material",
        n_results=8
    )

    # If few study material candidates found, also allow general subject search
    if len(candidates) < 2:
        extra = query_vector_store(
            query_text=search_query,
            subject=subject,
            source_type=None,
            n_results=5
        )
        candidates.extend(extra)

    # Rerank and select top_k
    reranked = rerank_chunks(
        query=search_query,
        chunks=candidates,
        top_k=top_k,
        min_score_threshold=0.1
    )

    return reranked
