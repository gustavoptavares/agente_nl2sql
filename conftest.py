import pytest
import os
import sys
from unittest.mock import MagicMock, patch
import tempfile
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))

os.environ["OPENAI_API_KEY"] = "test-api-key"
os.environ["LANGCHAIN_API_KEY"] = "test-langchain-key"
os.environ["QDRANT_HOST"] = "localhost"
os.environ["QDRANT_PORT"] = "6333"
os.environ["LLM_MODEL"] = "gpt-4o-mini"

@pytest.fixture
def sample_schema():
    return {
        "tables": [
            {
                "name": "vendas",
                "columns": [
                    {"name": "id", "type": "INTEGER"},
                    {"name": "data", "type": "DATE"},
                    {"name": "cliente_id", "type": "INTEGER"},
                    {"name": "valor", "type": "FLOAT"},
                    {"name": "produto", "type": "VARCHAR"}
                ]
            },
            {
                "name": "clientes",
                "columns": [
                    {"name": "id", "type": "INTEGER"},
                    {"name": "nome", "type": "VARCHAR"},
                    {"name": "email", "type": "VARCHAR"}
                ]
            }
        ]
    }

@pytest.fixture
def sample_query_result():
    return [
        {"cliente_id": 1, "total_vendas": 15000.0},
        {"cliente_id": 2, "total_vendas": 12500.0},
        {"cliente_id": 3, "total_vendas": 9800.0}
    ]

@pytest.fixture
def sample_state(sample_schema):
    return {
        "question": "Quais são as vendas por cliente?",
        "data_source": "sqlite",
        "connection_string": "sqlite:///./test.db",
        "session_id": "test-session-123",
        "messages": [],
        "intent": None,
        "schema": sample_schema,
        "rag_context": None,
        "generated_sql": None,
        "validated_sql": None,
        "query_result": None,
        "answer": None,
        "visualization": None,
        "error": None,
        "retry_count": 0
    }

@pytest.fixture
def temp_csv_file():
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "produto": ["A", "B", "C"],
        "valor": [100.0, 200.0, 150.0],
        "quantidade": [10, 20, 15]
    })
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def temp_excel_file():
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "produto": ["A", "B", "C"],
        "valor": [100.0, 200.0, 150.0]
    })
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        df.to_excel(f.name, index=False)
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def temp_sqlite_db():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    from sqlalchemy import create_engine, text
    engine = create_engine(f"sqlite:///{db_path}")
    
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE vendas (
                id INTEGER PRIMARY KEY,
                cliente_id INTEGER,
                produto VARCHAR(100),
                valor REAL,
                data DATE
            )
        """))
        conn.execute(text("""
            CREATE TABLE clientes (
                id INTEGER PRIMARY KEY,
                nome VARCHAR(100),
                email VARCHAR(100)
            )
        """))
        conn.execute(text("""
            INSERT INTO vendas VALUES
            (1, 1, 'Produto A', 100.0, '2024-01-15'),
            (2, 1, 'Produto B', 200.0, '2024-01-20'),
            (3, 2, 'Produto A', 150.0, '2024-02-10')
        """))
        conn.execute(text("""
            INSERT INTO clientes VALUES
            (1, 'João Silva', 'joao@email.com'),
            (2, 'Maria Santos', 'maria@email.com')
        """))
        conn.commit()
    
    yield f"sqlite:///{db_path}"
    os.unlink(db_path)