import pytest
from unittest.mock import patch, MagicMock


class TestRAGAgent:

    def test_format_schema(self, sample_schema):
        from src.agents.rag_agent import format_schema

        result = format_schema(sample_schema)

        assert "Tabela: vendas" in result
        assert "Tabela: clientes" in result
        assert "cliente_id" in result
        assert "valor" in result

    def test_format_schema_empty(self):
        from src.agents.rag_agent import format_schema

        result = format_schema({})

        assert result == "Schema não disponível"

    def test_format_schema_none(self):
        from src.agents.rag_agent import format_schema

        result = format_schema(None)

        assert result == "Schema não disponível"

    @patch('src.agents.rag_agent.hybrid_search')
    def test_rag_agent_creates_context(self, mock_hybrid, sample_state, sample_schema):
        from src.agents.rag_agent import rag_agent

        mock_hybrid.return_value = [
            {"content": "Exemplo: SELECT cliente_id, SUM(valor) FROM vendas GROUP BY cliente_id"}
        ]

        sample_state["schema"] = sample_schema

        result = rag_agent(sample_state)

        assert result["rag_context"] is not None
        assert "Schema do banco" in result["rag_context"]
        assert "vendas" in result["rag_context"]

    @patch('src.agents.rag_agent.hybrid_search')
    def test_rag_agent_includes_examples(self, mock_hybrid, sample_state, sample_schema):
        from src.agents.rag_agent import rag_agent

        mock_hybrid.return_value = []
        sample_state["schema"] = sample_schema

        result = rag_agent(sample_state)

        assert "Exemplos de SQL" in result["rag_context"]

    @patch('src.agents.rag_agent.hybrid_search')
    def test_rag_agent_handles_hybrid_search_failure(self, mock_hybrid, sample_state, sample_schema):
        from src.agents.rag_agent import rag_agent

        mock_hybrid.side_effect = Exception("Qdrant not available")
        sample_state["schema"] = sample_schema

        result = rag_agent(sample_state)

        assert result["rag_context"] is not None
        assert "Schema do banco" in result["rag_context"]

    @patch('src.agents.rag_agent.hybrid_search')
    def test_rag_agent_adds_message(self, mock_hybrid, sample_state, sample_schema):
        from src.agents.rag_agent import rag_agent

        mock_hybrid.return_value = []
        sample_state["schema"] = sample_schema
        sample_state["messages"] = []

        result = rag_agent(sample_state)

        assert len(result["messages"]) == 1
        assert "RAG" in result["messages"][0].content