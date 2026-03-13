from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
from src.config import settings

_client: Optional[QdrantClient] = None
_encoder: Optional[SentenceTransformer] = None

def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    return _client

def get_encoder() -> SentenceTransformer:
    global _encoder
    if _encoder is None:
        _encoder = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _encoder

def ensure_collection():
    client = get_qdrant_client()
    encoder = get_encoder()
    
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]
    
    if settings.QDRANT_COLLECTION not in collection_names:
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=models.VectorParams(
                size=encoder.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE
            )
        )

def add_documents(documents: List[Dict]) -> bool:
    client = get_qdrant_client()
    encoder = get_encoder()
    ensure_collection()
    
    points = []
    for i, doc in enumerate(documents):
        content = doc.get("content", "")
        embedding = encoder.encode(content).tolist()
        
        points.append(models.PointStruct(
            id=i,
            vector=embedding,
            payload={
                "content": content,
                "metadata": doc.get("metadata", {})
            }
        ))
    
    client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
    return True

def search_documents(query: str, top_k: int = 10, filter_dict: dict = None) -> List[Dict]:
    client = get_qdrant_client()
    encoder = get_encoder()
    
    try:
        ensure_collection()
    except Exception:
        return []
    
    query_vector = encoder.encode(query).tolist()
    
    qdrant_filter = None
    if filter_dict:
        conditions = []
        for key, value in filter_dict.items():
            conditions.append(models.FieldCondition(
                key=f"metadata.{key}",
                match=models.MatchValue(value=value)
            ))
        qdrant_filter = models.Filter(must=conditions)
    
    results = client.search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=top_k,
        query_filter=qdrant_filter
    )
    
    return [
        {
            "content": r.payload.get("content", ""),
            "metadata": r.payload.get("metadata", {}),
            "score": r.score
        }
        for r in results
    ]