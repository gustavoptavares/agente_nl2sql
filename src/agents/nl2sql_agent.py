from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from src.state import GraphState
from src.config import settings

NL2SQL_PROMPT = """Você é um especialista em SQL. Gere uma consulta SQL baseada na pergunta do usuário.

{context}

Pergunta: {question}

Regras:
1. Use apenas as tabelas e colunas do schema fornecido
2. Sempre use alias para colunas calculadas
3. Adicione LIMIT {limit} para evitar resultados muito grandes
4. Não use SELECT * - especifique as colunas
5. Retorne APENAS o SQL, sem explicações

SQL:"""

def get_llm():
    return ChatOpenAI(model=settings.LLM_MODEL, temperature=0)

def nl2sql_agent(state: GraphState) -> GraphState:
    question = state["question"]
    rag_context = state.get("rag_context", "")
    retry_count = state.get("retry_count", 0)
    
    llm = get_llm()
    prompt = NL2SQL_PROMPT.format(
        context=rag_context,
        question=question,
        limit=settings.SQL_RESULT_LIMIT
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    sql = response.content.strip()
    
    if sql.startswith("```sql"):
        sql = sql[6:]
    if sql.startswith("```"):
        sql = sql[3:]
    if sql.endswith("```"):
        sql = sql[:-3]
    sql = sql.strip()
    
    return {
        **state,
        "generated_sql": sql,
        "retry_count": retry_count,
        "messages": state.get("messages", []) + [AIMessage(content=f"SQL gerado: {sql}")]
    }