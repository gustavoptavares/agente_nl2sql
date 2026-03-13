import pytest
from unittest.mock import patch, MagicMock


class TestVisualizationAgent:

    @patch('src.agents.visualization_agent.get_llm')
    def test_creates_visualization(self, mock_get_llm, sample_state, sample_query_result):
        from src.agents.visualization_agent import visualization_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"chart_type": "bar", "x_column": "cliente_id", "y_column": "total_vendas", "title": "Vendas"}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["query_result"] = sample_query_result

        result = visualization_agent(sample_state)

        assert result["visualization"] is not None
        assert "chart_type" in result["visualization"]
        assert "data" in result["visualization"]

    def test_handles_empty_result(self, sample_state):
        from src.agents.visualization_agent import visualization_agent

        sample_state["query_result"] = []

        result = visualization_agent(sample_state)

        assert result["visualization"] is None

    @patch('src.agents.visualization_agent.get_llm')
    def test_creates_default_on_parse_error(self, mock_get_llm, sample_state, sample_query_result):
        from src.agents.visualization_agent import visualization_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "invalid json"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["query_result"] = sample_query_result

        result = visualization_agent(sample_state)

        assert result["visualization"] is not None
        assert result["visualization"]["chart_type"] == "bar"

    def test_handles_none_result(self, sample_state):
        from src.agents.visualization_agent import visualization_agent

        sample_state["query_result"] = None

        result = visualization_agent(sample_state)

        assert result["visualization"] is None

    @patch('src.agents.visualization_agent.get_llm')
    def test_parses_json_from_code_block(self, mock_get_llm, sample_state, sample_query_result):
        from src.agents.visualization_agent import visualization_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '```json\n{"chart_type": "line", "x_column": "cliente_id", "y_column": "total_vendas", "title": "Trend"}\n```'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["query_result"] = sample_query_result

        result = visualization_agent(sample_state)

        assert result["visualization"] is not None
        assert result["visualization"]["chart_type"] == "line"