from typing import List, Dict
from sentence_transformers import CrossEncoder
from src.config import settings

_reranker: CrossEncoder = None

def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    return _reranker

def rerank_documents(query: str, documents: List[Dict], top_k: int = None) -> List[Dict]:
    if not documents:
        return []
    
    reranker = get_reranker()
    
    pairs = [(query, doc.get("content", "")) for doc in documents]
    scores = reranker.predict(pairs)
    
    for doc, score in zip(documents, scores):
        doc["rerank_score"] = float(score)
    
    sorted_docs = sorted(documents, key=lambda x: x.get("rerank_score", 0), reverse=True)
    
    if top_k:
        return sorted_docs[:top_k]
    return sorted_docs