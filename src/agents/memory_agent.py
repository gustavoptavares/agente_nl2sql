from langchain_core.messages import AIMessage
from src.state import GraphState

def memory_agent(state: GraphState) -> GraphState:
    messages = state.get("messages", [])
    question = state.get("question", "")
    
    context_from_history = ""
    for msg in messages[-10:]:
        if hasattr(msg, 'content'):
            content = msg.content
        elif isinstance(msg, dict):
            content = msg.get('content', '')
        else:
            continue
        
        if "SQL gerado:" in content or "SQL validado:" in content:
            context_from_history += f"\n{content}"
    
    enhanced_context = f"""
Contexto do histórico da conversa:
{context_from_history}

Nova pergunta (follow-up): {question}
"""
    
    current_rag = state.get("rag_context", "")
    
    return {
        **state,
        "rag_context": (current_rag + "\n\n" + enhanced_context).strip(),
        "messages": messages + [AIMessage(content="Contexto de memória adicionado")]
    }