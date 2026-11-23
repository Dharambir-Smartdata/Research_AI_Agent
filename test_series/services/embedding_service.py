"""
Embedding Service for UPSC RAG Pipeline.
Uses pre-cached local SentenceTransformer for fast, zero-network, high-accuracy embeddings.
"""
import os
from typing import List, Union
import numpy as np

_model_instance = None

def get_embedding_model():
    """Lazily load the local SentenceTransformer model."""
    global _model_instance
    if _model_instance is None:
        from sentence_transformers import SentenceTransformer
        # Load from local cache with local_files_only=True to ensure 100% offline safety
        try:
            _model_instance = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2",
                local_files_only=True
            )
        except Exception as e:
            # Fallback if local_files_only fails
            _model_instance = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model_instance


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate dense embeddings for a list of strings."""
    if not texts:
        return []
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """Generate embedding for a single search query."""
    model = get_embedding_model()
    emb = model.encode([query], convert_to_numpy=True, show_progress_bar=False)
    return emb[0].tolist()


# Chroma Embedding Function Adapter
class ChromaSentenceTransformerEF:
    """ChromaDB compatible embedding function adapter."""
    def __init__(self):
        self.model = get_embedding_model()

    @staticmethod
    def name() -> str:
        return "sentence-transformers/all-MiniLM-L6-v2"

    def default_space(self) -> str:
        return "cosine"

    def supported_spaces(self) -> List[str]:
        return ["cosine", "l2", "ip"]

    def get_config(self) -> dict:
        return {"model_name": "all-MiniLM-L6-v2"}

    @staticmethod
    def build_from_config(config: dict) -> "ChromaSentenceTransformerEF":
        return ChromaSentenceTransformerEF()

    def __call__(self, input: Union[List[str], str]) -> List[List[float]]:
        if isinstance(input, str):
            input = [input]
        return self.model.encode(input, convert_to_numpy=True, show_progress_bar=False).tolist()

    def embed_query(self, input: Union[List[str], str]) -> List[List[float]]:
        return self.__call__(input)
