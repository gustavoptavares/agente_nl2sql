from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import uuid
import os
import tempfile
import shutil
from src.graph import graph

router = APIRouter()

UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "nl2sql_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    question: str
    data_source: str = "sqlite"
    connection_string: Optional[str] = None
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sql: Optional[str] = None
    data: Optional[list] = None
    chart: Optional[dict] = None
    session_id: str

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    connection_string: str

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    if not request.connection_string:
        raise HTTPException(status_code=400, detail="Connection string is required")
    
    initial_state = {
        "question": request.question,
        "data_source": request.data_source,
        "connection_string": request.connection_string,
        "session_id": session_id,
        "messages": [],
        "retry_count": 0
    }
    
    config = {"configurable": {"thread_id": session_id}}
    
    try:
        result = graph.invoke(initial_state, config)
        
        return QueryResponse(
            answer=result.get("answer", "Não foi possível processar sua pergunta."),
            sql=result.get("validated_sql"),
            data=result.get("query_result"),
            chart=result.get("visualization"),
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1].lower()
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    if file_ext in [".db", ".sqlite", ".sqlite3"]:
        connection_string = f"sqlite:///{file_path}"
    else:
        connection_string = file_path
    
    return UploadResponse(
        file_id=file_id,
        filename=file.filename,
        connection_string=connection_string
    )

@router.get("/schema")
async def get_schema(connection_string: str, data_source: str = "sqlite"):
    try:
        if data_source in ["sqlite", "postgresql", "mysql"]:
            from sqlalchemy import create_engine, inspect
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
        
        elif data_source == "csv":
            import pandas as pd
            df = pd.read_csv(connection_string)
            table_name = os.path.basename(connection_string).replace(".csv", "")
            columns = [{"name": col, "type": str(df[col].dtype)} for col in df.columns]
            return {"tables": [{"name": table_name, "columns": columns}]}
        
        elif data_source in ["excel", "xlsx", "xls"]:
            import pandas as pd
            xl = pd.ExcelFile(connection_string)
            tables = []
            for sheet_name in xl.sheet_names:
                df = pd.read_excel(connection_string, sheet_name=sheet_name)
                columns = [{"name": col, "type": str(df[col].dtype)} for col in df.columns]
                tables.append({"name": sheet_name, "columns": columns})
            return {"tables": tables}
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported data source: {data_source}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/upload/{file_id}")
async def delete_file(file_id: str):
    for ext in [".db", ".sqlite", ".sqlite3", ".csv", ".xlsx", ".xls"]:
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"status": "deleted", "file_id": file_id}
    
    raise HTTPException(status_code=404, detail="File not found")