from enum import Enum


class RetrievalMethod(Enum):
    """Supported retrieval backends."""
    VECTOR_DB = "vector_db"
    BM25 = "bm25"
