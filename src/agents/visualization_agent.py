from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import json
from src.state import GraphState
from src.config import settings

VIZ_PROMPT = """Analise os dados e sugira a melhor visualização.

Dados (primeiras linhas): {data}
Colunas disponíveis: {columns}

Responda em JSON com o formato:
{{
    "chart_type": "bar|line|pie|scatter",
    "x_column": "nome_coluna_x",
    "y_column": "nome_coluna_y",
    "title": "Título do gráfico"
}}

Escolha o tipo de gráfico mais apropriado para os dados."""

def get_llm():
    return ChatOpenAI(model=settings.LLM_MODEL, temperature=0)

def visualization_agent(state: GraphState) -> GraphState:
    result = state.get("query_result", [])
    
    if not result:
        return {
            **state,
            "visualization": None,
            "messages": state.get("messages", []) + [AIMessage(content="Sem dados para visualização")]
        }
    
    columns = list(result[0].keys()) if result else []
    data_sample = result[:5]
    
    prompt = VIZ_PROMPT.format(
        data=json.dumps(data_sample, default=str),
        columns=columns
    )
    
    try:
        llm = get_llm()
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        viz_config = json.loads(content)
        viz_config["data"] = result
        
        return {
            **state,
            "visualization": viz_config,
            "messages": state.get("messages", []) + [AIMessage(content=f"Visualização criada: {viz_config['chart_type']}")]
        }
    except Exception as e:
        default_viz = {
            "chart_type": "bar",
            "x_column": columns[0] if columns else None,
            "y_column": columns[1] if len(columns) > 1 else columns[0] if columns else None,
            "title": "Resultado da Consulta",
            "data": result
        }
        
        return {
            **state,
            "visualization": default_viz,
            "messages": state.get("messages", []) + [AIMessage(content="Visualização padrão criada")]
        }