from functools import lru_cache
from importlib.resources import files
from typing import List, Dict, Any
import json
import pickle
import numpy as np


_PKG = "rag_agent.data"


@lru_cache(maxsize=None)
def load_json() -> List[Dict[str, Any]]:
    resource = files(_PKG) / "website_data.json"
    if not resource.is_file():
        raise FileNotFoundError(
            f"Error: index file {resource} not found. "
            "Please run etl/document-data-etl/bm25_tokenizer.py first."
        )

    with resource.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data


@lru_cache(maxsize=None)
def load_bm25_model_pkl() -> Any:  
    resource = files(_PKG) / "website_data.pkl"
    if not resource.is_file(): 
        raise FileNotFoundError(
            f"Error: index file {resource} not found. "
            "Please run etl/document-data-etl/bm25_tokenizer.py first."
        )

    with resource.open("rb") as f:
        bm25_model = pickle.load(f)
    return bm25_model   


@lru_cache(maxsize=None)
def load_doc_id_map_npy() -> np.ndarray:
    resource = files(_PKG) / "website_data_doc_id_map.npy"
    if not resource.is_file():
        raise FileNotFoundError(
            f"Error: index file {resource} not found. "
            "Please run etl/document-data-etl/bm25_tokenizer.py first."
        )

    with resource.open("rb") as f:
        doc_id_map = np.load(f)
    return doc_id_map