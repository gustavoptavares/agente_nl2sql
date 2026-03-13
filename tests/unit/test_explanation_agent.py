import pytest
from unittest.mock import patch, MagicMock


class TestExplanationAgent:

    @patch('src.agents.explanation_agent.get_llm')
    def test_generates_explanation(self, mock_get_llm, sample_state, sample_query_result):
        from src.agents.explanation_agent import explanation_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Os resultados mostram as vendas por cliente."
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["validated_sql"] = "SELECT cliente_id, SUM(valor) FROM vendas GROUP BY cliente_id"
        sample_state["query_result"] = sample_query_result
        sample_state["intent"] = "DB_QUERY"

        result = explanation_agent(sample_state)

        assert result["answer"] is not None
        assert len(result["answer"]) > 0

    @patch('src.agents.explanation_agent.get_llm')
    def test_handles_general_question(self, mock_get_llm, sample_state):
        from src.agents.explanation_agent import explanation_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "SQL é uma linguagem de consulta estruturada."
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["intent"] = "GENERAL_QUESTION"
        sample_state["question"] = "O que é SQL?"

        result = explanation_agent(sample_state)

        assert result["answer"] is not None

    @patch('src.agents.explanation_agent.get_llm')
    def test_handles_error_state(self, mock_get_llm, sample_state):
        from src.agents.explanation_agent import explanation_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Ocorreu um erro na consulta."
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["error"] = "SQL execution failed"
        sample_state["intent"] = "DB_QUERY"

        result = explanation_agent(sample_state)

        assert result["answer"] is not None

    @patch('src.agents.explanation_agent.get_llm')
    def test_adds_message(self, mock_get_llm, sample_state):
        from src.agents.explanation_agent import explanation_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Resposta gerada."
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        sample_state["intent"] = "DB_QUERY"
        sample_state["messages"] = []

        result = explanation_agent(sample_state)

        assert len(result["messages"]) == 1