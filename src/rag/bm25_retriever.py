from rank_bm25 import BM25Okapi
from typing import List, Dict
import re

_corpus: List[Dict] = []
_bm25: BM25Okapi = None
_tokenized_corpus: List[List[str]] = []

def tokenize(text: str) -> List[str]:
    text = text.lower()
    tokens = re.findall(r'\w+', text)
    return tokens

def index_documents(documents: List[Dict]):
    global _corpus, _bm25, _tokenized_corpus
    
    _corpus = documents
    _tokenized_corpus = [tokenize(doc.get("content", "")) for doc in documents]
    _bm25 = BM25Okapi(_tokenized_corpus)

def bm25_search(query: str, top_k: int = 10, filter_dict: dict = None) -> List[Dict]:
    global _corpus, _bm25
    
    if _bm25 is None or not _corpus:
        return []
    
    tokenized_query = tokenize(query)
    scores = _bm25.get_scores(tokenized_query)
    
    scored_docs = list(zip(_corpus, scores))
    
    if filter_dict:
        filtered = []
        for doc, score in scored_docs:
            metadata = doc.get("metadata", {})
            match = all(metadata.get(k) == v for k, v in filter_dict.items())
            if match:
                filtered.append((doc, score))
        scored_docs = filtered
    
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    
    results = []
    for doc, score in scored_docs[:top_k]:
        results.append({
            "content": doc.get("content", ""),
            "metadata": doc.get("metadata", {}),
            "score": float(score),
            "source": "bm25"
        })
    
    return results