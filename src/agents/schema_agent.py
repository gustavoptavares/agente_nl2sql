from sqlalchemy import create_engine, inspect
from langchain_core.messages import AIMessage
import pandas as pd
import os
from src.state import GraphState

def introspect_database(connection_string: str) -> dict:
    engine = create_engine(connection_string)
    inspector = inspect(engine)
    
    tables = []
    for table_name in inspector.get_table_names():
        columns = []
        for col in inspector.get_columns(table_name):
            columns.append({
                "name": col["name"],
                "type": str(col["type"])
            })
        tables.append({"name": table_name, "columns": columns})
    
    return {"tables": tables}

def introspect_csv(file_path: str) -> dict:
    df = pd.read_csv(file_path)
    table_name = os.path.basename(file_path).replace(".csv", "")
    
    columns = [{"name": col, "type": str(df[col].dtype)} for col in df.columns]
    return {"tables": [{"name": table_name, "columns": columns}]}

def introspect_excel(file_path: str) -> dict:
    xl = pd.ExcelFile(file_path)
    tables = []
    
    for sheet_name in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        columns = [{"name": col, "type": str(df[col].dtype)} for col in df.columns]
        clean_name = sheet_name.replace(" ", "_").replace("-", "_")
        tables.append({"name": clean_name, "columns": columns})
    
    return {"tables": tables}

def schema_agent(state: GraphState) -> GraphState:
    data_source = state.get("data_source", "sqlite")
    connection_string = state.get("connection_string", "")
    
    try:
        if data_source in ["postgresql", "mysql", "sqlite"]:
            schema = introspect_database(connection_string)
        elif data_source == "csv":
            schema = introspect_csv(connection_string)
        elif data_source in ["excel", "xlsx", "xls"]:
            schema = introspect_excel(connection_string)
        else:
            schema = {"tables": []}
        
        return {
            **state,
            "schema": schema,
            "messages": state.get("messages", []) + [AIMessage(content=f"Schema extraído: {len(schema['tables'])} tabelas")]
        }
    except Exception as e:
        return {
            **state,
            "schema": {"tables": []},
            "error": f"Schema extraction failed: {str(e)}",
            "messages": state.get("messages", []) + [AIMessage(content=f"Erro ao extrair schema: {str(e)}")]
        }