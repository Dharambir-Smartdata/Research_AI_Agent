"""
Vector Store Service using persistent ChromaDB with subject isolation and metadata filtering.
"""
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb

from test_series.services.embedding_service import embed_texts, embed_query

CHROMA_PERSIST_DIR = Path(__file__).resolve().parent.parent / "vector_db" / "chroma"
CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

COLLECTION_NAME = "upsc_knowledge_base"

_chroma_client = None
_collection_instance = None

def get_chroma_client():
    """Singleton Chroma PersistentClient."""
    global _chroma_client
    if _chroma_client is None:
        CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
    return _chroma_client


def get_upsc_collection():
    """Get or create the UPSC collection with cosine distance."""
    global _collection_instance
    if _collection_instance is None:
        client = get_chroma_client()
        _collection_instance = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection_instance


def add_chunks_to_vector_store(chunks: List[Dict[str, Any]]) -> int:
    """
    Store chunk texts, dense embeddings, and metadata into the vector database.
    """
    if not chunks:
        return 0

    collection = get_upsc_collection()
    
    ids = []
    documents = []
    metadatas = []

    for i, c in enumerate(chunks):
        cid = c.get("chunk_id") or f"chk_{i}_{c.get('subject')}_{c.get('page_number', 1)}"
        ids.append(cid)
        documents.append(c.get("text", ""))
        
        meta = {
            "exam": str(c.get("exam", "UPSC")),
            "subject": str(c.get("subject", "General")),
            "source_type": str(c.get("source_type", "study_material")),
            "document_name": str(c.get("document_name", "")),
            "page_number": int(c.get("page_number", 1)),
            "section_heading": str(c.get("section_heading", ""))[:120],
        }
        if "year" in c:
            meta["year"] = int(c["year"])
        metadatas.append(meta)

    # Compute dense embeddings using local SentenceTransformer
    embeddings = embed_texts(documents)

    # Upsert with embeddings to avoid duplicate key errors
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )
    return len(ids)


def query_vector_store(
    query_text: str,
    subject: str,
    source_type: Optional[str] = None,
    n_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Retrieve top-k chunks with strict subject isolation and optional source_type filter.
    """
    collection = get_upsc_collection()
    
    # Construct metadata filter
    if source_type:
        where_filter = {
            "$and": [
                {"subject": {"$eq": subject}},
                {"source_type": {"$eq": source_type}}
            ]
        }
    else:
        where_filter = {"subject": {"$eq": subject}}

    # Compute query vector
    q_emb = embed_query(query_text)

    results = collection.query(
        query_embeddings=[q_emb],
        n_results=n_results,
        where=where_filter
    )

    matched_chunks = []
    if results and results.get("documents") and results["documents"][0]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)
        ids = results["ids"][0] if results.get("ids") else [""] * len(docs)

        for doc, meta, dist, cid in zip(docs, metas, distances, ids):
            # Cosine similarity = 1 - distance
            score = round(1.0 - float(dist), 4)
            matched_chunks.append({
                "chunk_id": cid,
                "text": doc,
                "metadata": meta,
                "similarity_score": score,
                "document_name": meta.get("document_name", ""),
                "page_number": meta.get("page_number", 1),
                "source_type": meta.get("source_type", "")
            })

    return matched_chunks


def get_subject_stats() -> Dict[str, Any]:
    """Retrieve indexed document and chunk counts per subject."""
    collection = get_upsc_collection()
    total_chunks = collection.count()

    # Query all metadatas to compute subject breakdowns
    stats = {}
    if total_chunks > 0:
        all_data = collection.get(include=["metadatas"])
        for meta in all_data.get("metadatas", []):
            subj = meta.get("subject", "Other")
            src = meta.get("source_type", "study_material")
            doc = meta.get("document_name", "")

            if subj not in stats:
                stats[subj] = {
                    "total_chunks": 0,
                    "study_material_chunks": 0,
                    "pyq_chunks": 0,
                    "documents": set()
                }
            stats[subj]["total_chunks"] += 1
            if src == "previous_year_questions":
                stats[subj]["pyq_chunks"] += 1
            else:
                stats[subj]["study_material_chunks"] += 1
            if doc:
                stats[subj]["documents"].add(doc)

        for s in stats:
            stats[s]["document_count"] = len(stats[s]["documents"])
            stats[s]["documents"] = list(stats[s]["documents"])

    return {
        "total_chunks": total_chunks,
        "subjects": stats
    }


def clear_subject_chunks(subject: str) -> int:
    """Clear all chunks for a given subject (for re-ingestion)."""
    collection = get_upsc_collection()
    collection.delete(where={"subject": {"$eq": subject}})
    return 1
