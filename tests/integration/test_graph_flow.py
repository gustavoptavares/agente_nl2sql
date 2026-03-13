import pytest
from unittest.mock import patch, MagicMock


class TestGraphFlow:

    @patch('src.agents.visualization_agent.get_llm')
    @patch('src.agents.explanation_agent.get_llm')
    @patch('src.agents.nl2sql_agent.get_llm')
    @patch('src.agents.router_agent.get_llm')
    @patch('src.agents.rag_agent.hybrid_search')
    def test_full_db_query_flow(
        self,
        mock_hybrid,
        mock_router_llm,
        mock_sql_llm,
        mock_exp_llm,
        mock_viz_llm,
        temp_sqlite_db
    ):
        from src.graph import create_graph

        mock_hybrid.return_value = []

        mock_router = MagicMock()
        mock_router.invoke.return_value = MagicMock(content="DB_QUERY")
        mock_router_llm.return_value = mock_router

        mock_sql = MagicMock()
        mock_sql.invoke.return_value = MagicMock(
            content="SELECT cliente_id, SUM(valor) as total FROM vendas GROUP BY cliente_id"
        )
        mock_sql_llm.return_value = mock_sql

        mock_exp = MagicMock()
        mock_exp.invoke.return_value = MagicMock(
            content="Os resultados mostram vendas agrupadas por cliente."
        )
        mock_exp_llm.return_value = mock_exp

        mock_viz = MagicMock()
        mock_viz.invoke.return_value = MagicMock(
            content='{"chart_type": "bar", "x_column": "cliente_id", "y_column": "total", "title": "Vendas"}'
        )
        mock_viz_llm.return_value = mock_viz

        graph = create_graph()

        initial_state = {
            "question": "Quais são as vendas por cliente?",
            "data_source": "sqlite",
            "connection_string": temp_sqlite_db,
            "session_id": "test-session",
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
        }

        result = graph.invoke(initial_state)

        assert result["intent"] == "DB_QUERY"
        assert result["schema"] is not None
        assert result["validated_sql"] is not None
        assert result["query_result"] is not None
        assert result["answer"] is not None

    @patch('src.agents.explanation_agent.get_llm')
    @patch('src.agents.router_agent.get_llm')
    def test_general_question_flow(self, mock_router_llm, mock_exp_llm):
        from src.graph import create_graph

        mock_router = MagicMock()
        mock_router.invoke.return_value = MagicMock(content="GENERAL_QUESTION")
        mock_router_llm.return_value = mock_router

        mock_exp = MagicMock()
        mock_exp.invoke.return_value = MagicMock(
            content="Uma tabela SQL é uma estrutura de dados..."
        )
        mock_exp_llm.return_value = mock_exp

        graph = create_graph()

        initial_state = {
            "question": "O que é uma tabela SQL?",
            "data_source": "sqlite",
            "connection_string": None,
            "session_id": "test-session",
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
        }

        result = graph.invoke(initial_state)

        assert result["intent"] == "GENERAL_QUESTION"
        assert result["answer"] is not None

    @patch('src.agents.explanation_agent.get_llm')
    @patch('src.agents.nl2sql_agent.get_llm')
    @patch('src.agents.router_agent.get_llm')
    @patch('src.agents.rag_agent.hybrid_search')
    def test_follow_up_flow(
        self,
        mock_hybrid,
        mock_router_llm,
        mock_sql_llm,
        mock_exp_llm,
        temp_sqlite_db
    ):
        from src.graph import create_graph

        mock_hybrid.return_value = []

        mock_router = MagicMock()
        mock_router.invoke.return_value = MagicMock(content="FOLLOW_UP")
        mock_router_llm.return_value = mock_router

        mock_sql = MagicMock()
        mock_sql.invoke.return_value = MagicMock(
            content="SELECT id, valor FROM vendas WHERE data >= '2024-01-01'"
        )
        mock_sql_llm.return_value = mock_sql

        mock_exp = MagicMock()
        mock_exp.invoke.return_value = MagicMock(content="Resultado filtrado.")
        mock_exp_llm.return_value = mock_exp

        graph = create_graph()

        initial_state = {
            "question": "E se filtrar por 2024?",
            "data_source": "sqlite",
            "connection_string": temp_sqlite_db,
            "session_id": "test-follow-up",
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
        }

        result = graph.invoke(initial_state)

        assert result["intent"] == "FOLLOW_UP"