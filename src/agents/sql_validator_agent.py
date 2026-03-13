import re
from langchain_core.messages import AIMessage
from src.state import GraphState
from src.config import settings

DANGEROUS_PATTERNS = [
    r";\s*(DROP|DELETE|TRUNCATE|ALTER|CREATE|INSERT|UPDATE)",
    r"--",
    r"/\*",
    r"UNION\s+SELECT",
    r"INTO\s+OUTFILE",
    r"LOAD_FILE",
]

def validate_sql(sql: str, schema: dict) -> tuple[bool, str]:
    if not sql or not sql.strip():
        return False, "SQL vazio"
    
    sql_upper = sql.upper()
    
    if not sql_upper.strip().startswith("SELECT"):
        return False, "Apenas consultas SELECT são permitidas"
    
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, sql_upper):
            return False, f"Padrão potencialmente perigoso detectado: {pattern}"
    
    if "SELECT *" in sql_upper:
        return False, "SELECT * não é permitido. Especifique as colunas."
    
    table_names = [t["name"].upper() for t in schema.get("tables", [])]
    from_match = re.search(r"FROM\s+(\w+)", sql_upper)
    if from_match:
        table_in_query = from_match.group(1)
        if table_in_query not in table_names and table_names:
            return False, f"Tabela '{table_in_query}' não encontrada no schema"
    
    if "LIMIT" not in sql_upper:
        sql = sql.rstrip(";") + f" LIMIT {settings.SQL_RESULT_LIMIT}"
    
    return True, sql

def sql_validator_agent(state: GraphState) -> GraphState:
    sql = state.get("generated_sql", "")
    schema = state.get("schema", {})
    retry_count = state.get("retry_count", 0)
    
    is_valid, result = validate_sql(sql, schema)
    
    if is_valid:
        return {
            **state,
            "validated_sql": result,
            "error": None,
            "messages": state.get("messages", []) + [AIMessage(content=f"SQL validado: {result}")]
        }
    else:
        return {
            **state,
            "validated_sql": None,
            "error": result,
            "retry_count": retry_count + 1,
            "messages": state.get("messages", []) + [AIMessage(content=f"Erro de validação: {result}")]
        }