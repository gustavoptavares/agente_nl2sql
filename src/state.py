from typing import TypedDict, Optional, List, Any
from langchain_core.messages import BaseMessage

class GraphState(TypedDict, total=False):
    question: str
    intent: Optional[str]
    data_source: Optional[str]
    connection_string: Optional[str]
    schema: Optional[dict]
    rag_context: Optional[str]
    generated_sql: Optional[str]
    validated_sql: Optional[str]
    query_result: Optional[List[dict]]
    visualization: Optional[dict]
    answer: Optional[str]
    error: Optional[str]
    retry_count: int
    session_id: Optional[str]
    messages: List[BaseMessage]