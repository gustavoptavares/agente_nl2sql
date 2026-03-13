from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from src.state import GraphState
from src.config import settings

ROUTER_PROMPT = """Classifique a intenção do usuário em uma das categorias:
- DB_QUERY: Pergunta que requer consulta SQL ao banco de dados
- GENERAL_QUESTION: Pergunta geral que não requer SQL
- FOLLOW_UP: Pergunta de acompanhamento baseada em conversa anterior
- VISUALIZATION_REQUEST: Pedido para criar gráfico/visualização

Pergunta: {question}

Responda APENAS com uma das categorias acima, sem explicação."""

def get_llm():
    return ChatOpenAI(model=settings.LLM_MODEL, temperature=0)

def router_agent(state: GraphState) -> GraphState:
    question = state["question"]
    messages = state.get("messages", [])
    
    llm = get_llm()
    prompt = ROUTER_PROMPT.format(question=question)
    response = llm.invoke([HumanMessage(content=prompt)])
    
    intent = response.content.strip().upper()
    valid_intents = ["DB_QUERY", "GENERAL_QUESTION", "FOLLOW_UP", "VISUALIZATION_REQUEST"]
    if intent not in valid_intents:
        intent = "DB_QUERY"
    
    return {
        **state,
        "intent": intent,
        "messages": messages + [
            HumanMessage(content=question),
            AIMessage(content=f"Intent classificado: {intent}")
        ]
    }