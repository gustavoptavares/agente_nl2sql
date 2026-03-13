from typing import List, Dict
from src.rag.qdrant_client import search_documents

def dense_search(query: str, top_k: int = 10, filter_dict: dict = None) -> List[Dict]:
    results = search_documents(query, top_k=top_k, filter_dict=filter_dict)
    
    for r in results:
        r["source"] = "dense"
    
    return results