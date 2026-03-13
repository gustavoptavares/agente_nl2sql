import pytest
from unittest.mock import patch, MagicMock


class TestRouterAgent:

    @patch('src.agents.router_agent.get_llm')
    def test_router_classifies_db_query(self, mock_get_llm, sample_state):
        from src.agents.router_agent import router_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "DB_QUERY"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["question"] = "Quais são as vendas de janeiro?"
        result = router_agent(sample_state)

        assert result["intent"] == "DB_QUERY"

    @patch('src.agents.router_agent.get_llm')
    def test_router_classifies_general_question(self, mock_get_llm, sample_state):
        from src.agents.router_agent import router_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "GENERAL_QUESTION"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["question"] = "O que é uma tabela SQL?"
        result = router_agent(sample_state)

        assert result["intent"] == "GENERAL_QUESTION"

    @patch('src.agents.router_agent.get_llm')
    def test_router_classifies_follow_up(self, mock_get_llm, sample_state):
        from src.agents.router_agent import router_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "FOLLOW_UP"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["question"] = "E se filtrar por 2023?"
        result = router_agent(sample_state)

        assert result["intent"] == "FOLLOW_UP"

    @patch('src.agents.router_agent.get_llm')
    def test_router_classifies_visualization(self, mock_get_llm, sample_state):
        from src.agents.router_agent import router_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "VISUALIZATION_REQUEST"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["question"] = "Faça um gráfico de barras"
        result = router_agent(sample_state)

        assert result["intent"] == "VISUALIZATION_REQUEST"

    @patch('src.agents.router_agent.get_llm')
    def test_router_defaults_to_db_query_on_invalid(self, mock_get_llm, sample_state):
        from src.agents.router_agent import router_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "INVALID_INTENT"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = router_agent(sample_state)

        assert result["intent"] == "DB_QUERY"

    @patch('src.agents.router_agent.get_llm')
    def test_router_adds_messages(self, mock_get_llm, sample_state):
        from src.agents.router_agent import router_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "DB_QUERY"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["messages"] = []
        result = router_agent(sample_state)

        assert len(result["messages"]) == 2