import pytest
from unittest.mock import patch, MagicMock
import tempfile
import os


class TestEndToEnd:

    @pytest.fixture
    def sample_sales_db(self):
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
                    cidade VARCHAR(100)
                )
            """))
            conn.execute(text("""
                INSERT INTO clientes VALUES
                (1, 'João Silva', 'São Paulo'),
                (2, 'Maria Santos', 'Rio de Janeiro'),
                (3, 'Pedro Oliveira', 'Belo Horizonte')
            """))
            conn.execute(text("""
                INSERT INTO vendas VALUES
                (1, 1, 'Produto A', 100.0, '2024-01-15'),
                (2, 1, 'Produto B', 200.0, '2024-01-20'),
                (3, 2, 'Produto A', 150.0, '2024-02-10'),
                (4, 3, 'Produto C', 300.0, '2024-02-15'),
                (5, 2, 'Produto B', 250.0, '2024-03-01')
            """))
            conn.commit()

        yield f"sqlite:///{db_path}"
        os.unlink(db_path)

    @patch('src.agents.visualization_agent.get_llm')
    @patch('src.agents.explanation_agent.get_llm')
    @patch('src.agents.nl2sql_agent.get_llm')
    @patch('src.agents.router_agent.get_llm')
    @patch('src.agents.rag_agent.hybrid_search')
    def test_complete_sales_query(
        self,
        mock_hybrid,
        mock_router_llm,
        mock_sql_llm,
        mock_exp_llm,
        mock_viz_llm,
        sample_sales_db
    ):
        mock_hybrid.return_value = []

        mock_router = MagicMock()
        mock_router.invoke.return_value = MagicMock(content="DB_QUERY")
        mock_router_llm.return_value = mock_router

        mock_sql = MagicMock()
        mock_sql.invoke.return_value = MagicMock(
            content="SELECT cliente_id, SUM(valor) as total FROM vendas GROUP BY cliente_id ORDER BY total DESC"
        )
        mock_sql_llm.return_value = mock_sql

        mock_exp = MagicMock()
        mock_exp.invoke.return_value = MagicMock(
            content="O cliente 3 teve o maior total de vendas com R$ 300."
        )
        mock_exp_llm.return_value = mock_exp

        mock_viz = MagicMock()
        mock_viz.invoke.return_value = MagicMock(
            content='{"chart_type": "bar", "x_column": "cliente_id", "y_column": "total", "title": "Vendas por Cliente"}'
        )
        mock_viz_llm.return_value = mock_viz

        from src.graph import create_graph

        graph = create_graph()

        result = graph.invoke({
            "question": "Qual o total de vendas por cliente?",
            "data_source": "sqlite",
            "connection_string": sample_sales_db,
            "session_id": "e2e-test",
            "messages": [],
            "intent": None,
            "schema": None,
            "rag_context": None,
            "generated_sql": None,
            "validated_sql": None,
            "query_result": None,
            "answer": None,
            "visualization": None,
            "error": None,
            "retry_count": 0
        })

        assert result["intent"] == "DB_QUERY"
        assert result["query_result"] is not None
        assert len(result["query_result"]) == 3
        assert result["answer"] is not None
        assert result["visualization"] is not None
        assert result["error"] is None

    @patch('src.agents.visualization_agent.get_llm')
    @patch('src.agents.explanation_agent.get_llm')
    @patch('src.agents.nl2sql_agent.get_llm')
    @patch('src.agents.router_agent.get_llm')
    @patch('src.agents.rag_agent.hybrid_search')
    def test_query_with_join(
        self,
        mock_hybrid,
        mock_router_llm,
        mock_sql_llm,
        mock_exp_llm,
        mock_viz_llm,
        sample_sales_db
    ):
        mock_hybrid.return_value = []

        mock_router = MagicMock()
        mock_router.invoke.return_value = MagicMock(content="DB_QUERY")
        mock_router_llm.return_value = mock_router

        mock_sql = MagicMock()
        mock_sql.invoke.return_value = MagicMock(
            content="SELECT c.nome, SUM(v.valor) as total FROM vendas v JOIN clientes c ON v.cliente_id = c.id GROUP BY c.nome"
        )
        mock_sql_llm.return_value = mock_sql

        mock_exp = MagicMock()
        mock_exp.invoke.return_value = MagicMock(content="Vendas por nome do cliente.")
        mock_exp_llm.return_value = mock_exp

        mock_viz = MagicMock()
        mock_viz.invoke.return_value = MagicMock(
            content='{"chart_type": "bar", "x_column": "nome", "y_column": "total", "title": "Vendas"}'
        )
        mock_viz_llm.return_value = mock_viz

        from src.graph import create_graph

        graph = create_graph()

        result = graph.invoke({
            "question": "Mostre o total de vendas por nome do cliente",
            "data_source": "sqlite",
            "connection_string": sample_sales_db,
            "session_id": "e2e-test-2",
            "messages": [],
            "intent": None,
            "schema": None,
            "rag_context": None,
            "generated_sql": None,
            "validated_sql": None,
            "query_result": None,
            "answer": None,
            "visualization": None,
            "error": None,
            "retry_count": 0
        })

        assert result["query_result"] is not None
        assert result["error"] is None