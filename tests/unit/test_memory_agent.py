import pytest
from langchain_core.messages import AIMessage


class TestMemoryAgent:

    def test_adds_context_from_history(self, sample_state):
        from src.agents.memory_agent import memory_agent

        sample_state["messages"] = [
            AIMessage(content="SQL gerado: SELECT id FROM vendas"),
            AIMessage(content="SQL validado: SELECT id FROM vendas LIMIT 100")
        ]
        sample_state["question"] = "E se filtrar por 2024?"

        result = memory_agent(sample_state)

        assert result["rag_context"] is not None
        assert "SQL gerado" in result["rag_context"] or "SQL validado" in result["rag_context"]

    def test_handles_empty_history(self, sample_state):
        from src.agents.memory_agent import memory_agent

        sample_state["messages"] = []
        sample_state["question"] = "Nova pergunta"

        result = memory_agent(sample_state)

        assert result["rag_context"] is not None

    def test_adds_follow_up_question(self, sample_state):
        from src.agents.memory_agent import memory_agent

        sample_state["messages"] = []
        sample_state["question"] = "Agora filtre por 2023"

        result = memory_agent(sample_state)

        assert "follow-up" in result["rag_context"].lower() or "Agora filtre por 2023" in result["rag_context"]

    def test_appends_to_existing_rag_context(self, sample_state):
        from src.agents.memory_agent import memory_agent

        sample_state["messages"] = []
        sample_state["question"] = "Nova pergunta"
        sample_state["rag_context"] = "Contexto existente"

        result = memory_agent(sample_state)

        assert "Contexto existente" in result["rag_context"]

    def test_adds_message_to_list(self, sample_state):
        from src.agents.memory_agent import memory_agent

        sample_state["messages"] = []
        sample_state["question"] = "Test"

        result = memory_agent(sample_state)

        assert len(result["messages"]) == 1
        assert "memória" in result["messages"][0].content.lower() or "Contexto" in result["messages"][0].content