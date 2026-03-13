from typing import List, Dict
from src.rag.bm25_retriever import bm25_search
from src.rag.dense_retriever import dense_search
from src.rag.reranker import rerank_documents

def reciprocal_rank_fusion(results_list: List[List[Dict]], k: int = 60) -> List[Dict]:
    doc_scores = {}
    doc_data = {}
    
    for results in results_list:
        for rank, doc in enumerate(results):
            content = doc.get("content", "")
            doc_id = hash(content)
            
            if doc_id not in doc_scores:
                doc_scores[doc_id] = 0
                doc_data[doc_id] = doc
            
            doc_scores[doc_id] += 1 / (k + rank + 1)
    
    sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    
    return [
        {**doc_data[doc_id], "rrf_score": score}
        for doc_id, score in sorted_docs
    ]

def hybrid_search(query: str, top_k: int = 10, filter_dict: dict = None) -> List[Dict]:
    bm25_results = bm25_search(query, top_k=top_k * 2, filter_dict=filter_dict)
    dense_results = dense_search(query, top_k=top_k * 2, filter_dict=filter_dict)
    
    fused_results = reciprocal_rank_fusion([bm25_results, dense_results])
    
    reranked = rerank_documents(query, fused_results[:top_k * 2])
    
    return reranked[:top_k]