from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from src.state import GraphState
from src.config import settings

EXPLANATION_PROMPT = """Você é um assistente que explica resultados de consultas SQL em linguagem natural.

Pergunta original: {question}
SQL executado: {sql}
Resultado: {result}
Erro (se houver): {error}

Forneça uma resposta clara e concisa em português. Se houver erro, explique o problema de forma amigável.
Se houver resultados, resuma os dados de forma compreensível."""

def get_llm():
    return ChatOpenAI(model=settings.LLM_MODEL, temperature=0.3)

def explanation_agent(state: GraphState) -> GraphState:
    question = state.get("question", "")
    sql = state.get("validated_sql", "")
    result = state.get("query_result", [])
    error = state.get("error", "")
    intent = state.get("intent", "")
    
    llm = get_llm()
    
    if intent == "GENERAL_QUESTION":
        prompt = f"Responda a seguinte pergunta de forma útil: {question}"
        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content
    else:
        result_str = str(result[:10]) if result else "Nenhum resultado"
        if result and len(result) > 10:
            result_str += f"\n... e mais {len(result) - 10} registros"
        
        prompt = EXPLANATION_PROMPT.format(
            question=question,
            sql=sql or "N/A",
            result=result_str,
            error=error or "Nenhum"
        )
        
        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content
    
    return {
        **state,
        "answer": answer,
        "messages": state.get("messages", []) + [AIMessage(content=answer)]
    }