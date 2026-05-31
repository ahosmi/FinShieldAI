"""FinShield AI — HuggingFace Embeddings (cached singleton)"""

from functools import lru_cache
from langchain_community.embeddings import HuggingFaceEmbeddings


@lru_cache(maxsize=1)
def get_embedder() -> HuggingFaceEmbeddings:
    """
    sentence-transformers/all-MiniLM-L6-v2:
    - 384-dimensional embeddings
    - Fast inference (CPU-friendly)
    - Strong semantic similarity for short paragraphs
    - ~22MB model size
    """
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
