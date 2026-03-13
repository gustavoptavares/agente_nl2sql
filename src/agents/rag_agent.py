from langchain_core.messages import AIMessage
from src.state import GraphState
from src.rag.hybrid_retriever import hybrid_search

def format_schema(schema: dict) -> str:
    if not schema or "tables" not in schema:
        return "Schema não disponível"
    
    lines = []
    for table in schema.get("tables", []):
        table_name = table.get("name", "unknown")
        columns = table.get("columns", [])
        col_strs = [f"  - {c['name']} ({c['type']})" for c in columns]
        lines.append(f"Tabela: {table_name}")
        lines.extend(col_strs)
    
    return "\n".join(lines)

def rag_agent(state: GraphState) -> GraphState:
    question = state["question"]
    schema = state.get("schema", {})
    data_source = state.get("data_source", "sqlite")
    
    schema_str = format_schema(schema)
    context_parts = [f"Schema do banco:\n{schema_str}"]
    
    try:
        rag_docs = hybrid_search(
            query=question,
            top_k=5,
            filter_dict={"db_type": data_source} if data_source else None
        )
        
        if rag_docs:
            rag_content = "\n\n".join([doc.get("content", "") for doc in rag_docs])
            context_parts.append(f"Documentos relevantes:\n{rag_content}")
    except Exception:
        pass
    
    examples = """
Exemplos de SQL:
- "Total de vendas por cliente" -> SELECT cliente_id, SUM(valor) as total FROM vendas GROUP BY cliente_id
- "Vendas do último mês" -> SELECT * FROM vendas WHERE data >= DATE('now', '-1 month')
- "Top 10 produtos mais vendidos" -> SELECT produto, COUNT(*) as qtd FROM vendas GROUP BY produto ORDER BY qtd DESC LIMIT 10
"""
    context_parts.append(examples)
    
    rag_context = "\n\n---\n\n".join(context_parts)
    
    return {
        **state,
        "rag_context": rag_context,
        "messages": state.get("messages", []) + [AIMessage(content="Contexto RAG preparado")]
    }