"""
Reranking Service for UPSC RAG Pipeline.
Refines retrieved candidates using cross-encoder scoring, keyword density, and duplicate suppression.
"""
from typing import List, Dict, Any

_cross_encoder = None

def get_cross_encoder():
    """Lazily load cross encoder model if available locally."""
    global _cross_encoder
    if _cross_encoder is None:
        try:
            from sentence_transformers import CrossEncoder
            _cross_encoder = CrossEncoder(
                "cross-encoder/ms-marco-MiniLM-L-6-v2",
                local_files_only=True
            )
        except Exception:
            _cross_encoder = False  # Mark as unavailable to prevent re-trying
    return _cross_encoder if _cross_encoder is not False else None


def rerank_chunks(
    query: str,
    chunks: List[Dict[str, Any]],
    top_k: int = 4,
    min_score_threshold: float = 0.25
) -> List[Dict[str, Any]]:
    """
    Rerank candidate chunks using Cross-Encoder or enhanced lexical-semantic scoring.
    Removes near-duplicate chunks.
    """
    if not chunks:
        return []

    # 1. Deduplicate chunks
    unique_chunks = []
    seen_texts = set()
    for c in chunks:
        # Simple fingerprint: first 60 chars of text
        fingerprint = c.get("text", "")[:60].lower().strip()
        if fingerprint not in seen_texts:
            seen_texts.add(fingerprint)
            unique_chunks.append(c)

    ce = get_cross_encoder()
    if ce is not None:
        try:
            pairs = [[query, c.get("text", "")] for c in unique_chunks]
            scores = ce.predict(pairs)
            for chunk, score in zip(unique_chunks, scores):
                chunk["rerank_score"] = round(float(score), 4)
            unique_chunks.sort(key=lambda x: x["rerank_score"], reverse=True)
            return unique_chunks[:top_k]
        except Exception:
            pass

    # Fallback Reranking: Cosine similarity + query term coverage
    query_terms = set(query.lower().split())
    for chunk in unique_chunks:
        text_lower = chunk.get("text", "").lower()
        term_matches = sum(1 for term in query_terms if term in text_lower)
        term_overlap = term_matches / max(len(query_terms), 1)
        sim = chunk.get("similarity_score", 0.5)
        # Hybrid combined score
        combined = (sim * 0.7) + (term_overlap * 0.3)
        chunk["rerank_score"] = round(combined, 4)

    unique_chunks.sort(key=lambda x: x["rerank_score"], reverse=True)
    return [c for c in unique_chunks[:top_k] if c.get("rerank_score", 0) >= min_score_threshold]
