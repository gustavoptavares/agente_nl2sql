import pytest
from unittest.mock import patch, MagicMock


class TestNL2SQLAgent:

    @patch('src.agents.nl2sql_agent.get_llm')
    def test_generates_sql(self, mock_get_llm, sample_state):
        from src.agents.nl2sql_agent import nl2sql_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "SELECT cliente_id, SUM(valor) as total FROM vendas GROUP BY cliente_id"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["rag_context"] = "Schema: vendas (id, cliente_id, valor)"
        result = nl2sql_agent(sample_state)

        assert result["generated_sql"] is not None
        assert "SELECT" in result["generated_sql"]

    @patch('src.agents.nl2sql_agent.get_llm')
    def test_strips_markdown_code_blocks(self, mock_get_llm, sample_state):
        from src.agents.nl2sql_agent import nl2sql_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "```sql\nSELECT id, valor FROM vendas\n```"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["rag_context"] = "Schema: vendas"
        result = nl2sql_agent(sample_state)

        assert "```" not in result["generated_sql"]
        assert "SELECT" in result["generated_sql"]

    @patch('src.agents.nl2sql_agent.get_llm')
    def test_strips_plain_code_blocks(self, mock_get_llm, sample_state):
        from src.agents.nl2sql_agent import nl2sql_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "```\nSELECT id FROM vendas\n```"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["rag_context"] = "Schema: vendas"
        result = nl2sql_agent(sample_state)

        assert "```" not in result["generated_sql"]

    @patch('src.agents.nl2sql_agent.get_llm')
    def test_preserves_retry_count(self, mock_get_llm, sample_state):
        from src.agents.nl2sql_agent import nl2sql_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "SELECT id FROM vendas"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["rag_context"] = "Schema: vendas"
        sample_state["retry_count"] = 2
        result = nl2sql_agent(sample_state)

        assert result["retry_count"] == 2

    @patch('src.agents.nl2sql_agent.get_llm')
    def test_adds_message(self, mock_get_llm, sample_state):
        from src.agents.nl2sql_agent import nl2sql_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "SELECT id FROM vendas"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["rag_context"] = "Schema: vendas"
        sample_state["messages"] = []
        result = nl2sql_agent(sample_state)

        assert len(result["messages"]) == 1
        assert "SQL gerado" in result["messages"][0].content