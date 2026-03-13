from langgraph.graph import StateGraph, END, START
from src.state import GraphState
from src.agents.router_agent import router_agent
from src.agents.schema_agent import schema_agent
from src.agents.rag_agent import rag_agent
from src.agents.nl2sql_agent import nl2sql_agent
from src.agents.sql_validator_agent import sql_validator_agent
from src.agents.sql_executor_agent import sql_executor_agent
from src.agents.explanation_agent import explanation_agent
from src.agents.visualization_agent import visualization_agent
from src.agents.memory_agent import memory_agent
from src.config import settings

def should_generate_sql(state: GraphState) -> str:
    intent = state.get("intent")
    if intent == "DB_QUERY":
        return "schema_agent"
    elif intent == "FOLLOW_UP":
        return "memory_agent"
    elif intent == "VISUALIZATION_REQUEST":
        return "visualization_agent"
    else:
        return "explanation_agent"

def should_retry(state: GraphState) -> str:
    if state.get("error") and state.get("retry_count", 0) < settings.MAX_RETRIES:
        return "nl2sql_agent"
    elif state.get("error"):
        return "explanation_agent"
    return "sql_executor_agent"

def should_visualize(state: GraphState) -> str:
    if state.get("query_result") and len(state.get("query_result", [])) > 0:
        return "visualization_agent"
    return "explanation_agent"

def create_graph():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("router_agent", router_agent)
    workflow.add_node("schema_agent", schema_agent)
    workflow.add_node("rag_agent", rag_agent)
    workflow.add_node("nl2sql_agent", nl2sql_agent)
    workflow.add_node("sql_validator_agent", sql_validator_agent)
    workflow.add_node("sql_executor_agent", sql_executor_agent)
    workflow.add_node("explanation_agent", explanation_agent)
    workflow.add_node("visualization_agent", visualization_agent)
    workflow.add_node("memory_agent", memory_agent)
    
    workflow.add_edge(START, "router_agent")
    
    workflow.add_conditional_edges(
        "router_agent",
        should_generate_sql,
        {
            "schema_agent": "schema_agent",
            "memory_agent": "memory_agent",
            "visualization_agent": "visualization_agent",
            "explanation_agent": "explanation_agent"
        }
    )
    
    workflow.add_edge("schema_agent", "rag_agent")
    workflow.add_edge("rag_agent", "nl2sql_agent")
    workflow.add_edge("nl2sql_agent", "sql_validator_agent")
    
    workflow.add_conditional_edges(
        "sql_validator_agent",
        should_retry,
        {
            "nl2sql_agent": "nl2sql_agent",
            "sql_executor_agent": "sql_executor_agent",
            "explanation_agent": "explanation_agent"
        }
    )
    
    workflow.add_conditional_edges(
        "sql_executor_agent",
        should_visualize,
        {
            "visualization_agent": "visualization_agent",
            "explanation_agent": "explanation_agent"
        }
    )
    
    workflow.add_edge("visualization_agent", "explanation_agent")
    workflow.add_edge("memory_agent", "rag_agent")
    workflow.add_edge("explanation_agent", END)
    
    return workflow.compile()

graph = create_graph()