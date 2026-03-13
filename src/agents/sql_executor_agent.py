from sqlalchemy import create_engine, text
from langchain_core.messages import AIMessage
import pandas as pd
import duckdb
import tempfile
import os
from src.state import GraphState

def execute_sql_database(connection_string: str, sql: str) -> list[dict]:
    engine = create_engine(connection_string)
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = result.keys()
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]

def execute_sql_csv(file_path: str, sql: str) -> list[dict]:
    df = pd.read_csv(file_path)
    table_name = os.path.basename(file_path).replace(".csv", "")
    
    conn = duckdb.connect()
    conn.register(table_name, df)
    
    result = conn.execute(sql).fetchdf()
    return result.to_dict(orient="records")

def execute_sql_excel(file_path: str, sql: str) -> list[dict]:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db = tmp.name
    
    try:
        engine = create_engine(f"sqlite:///{tmp_db}")
        xl = pd.ExcelFile(file_path)
        
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            clean_name = sheet_name.replace(" ", "_").replace("-", "_")
            df.to_sql(clean_name, engine, index=False, if_exists="replace")
        
        return execute_sql_database(f"sqlite:///{tmp_db}", sql)
    finally:
        if os.path.exists(tmp_db):
            os.unlink(tmp_db)

def sql_executor_agent(state: GraphState) -> GraphState:
    sql = state.get("validated_sql", "")
    data_source = state.get("data_source", "sqlite")
    connection_string = state.get("connection_string", "")
    
    if not sql:
        return {
            **state,
            "error": "No SQL to execute",
            "messages": state.get("messages", []) + [AIMessage(content="Erro: Nenhum SQL para executar")]
        }
    
    try:
        if data_source in ["postgresql", "mysql", "sqlite"]:
            result = execute_sql_database(connection_string, sql)
        elif data_source == "csv":
            result = execute_sql_csv(connection_string, sql)
        elif data_source in ["excel", "xlsx", "xls"]:
            result = execute_sql_excel(connection_string, sql)
        else:
            result = []
        
        return {
            **state,
            "query_result": result,
            "error": None,
            "messages": state.get("messages", []) + [AIMessage(content=f"Consulta executada: {len(result)} registros")]
        }
        
    except Exception as e:
        return {
            **state,
            "error": f"SQL execution failed: {str(e)}",
            "query_result": None,
            "messages": state.get("messages", []) + [AIMessage(content=f"Erro na execução: {str(e)}")]
        }