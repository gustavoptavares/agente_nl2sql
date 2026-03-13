import pytest


class TestSQLValidatorAgent:

    def test_validate_valid_select(self, sample_state):
        from src.agents.sql_validator_agent import sql_validator_agent

        sample_state["generated_sql"] = "SELECT id, valor FROM vendas WHERE valor > 100"
        result = sql_validator_agent(sample_state)

        assert result["validated_sql"] is not None
        assert result["error"] is None
        assert "LIMIT" in result["validated_sql"]

    def test_reject_drop_statement(self, sample_state):
        from src.agents.sql_validator_agent import sql_validator_agent

        sample_state["generated_sql"] = "DROP TABLE vendas"
        result = sql_validator_agent(sample_state)

        assert result["error"] is not None
        assert result["retry_count"] == 1

    def test_reject_delete_statement(self, sample_state):
        from src.agents.sql_validator_agent import sql_validator_agent

        sample_state["generated_sql"] = "DELETE FROM vendas WHERE id = 1"
        result = sql_validator_agent(sample_state)

        assert result["error"] is not None

    def test_reject_update_statement(self, sample_state):
        from src.agents.sql_validator_agent import sql_validator_agent

        sample_state["generated_sql"] = "UPDATE vendas SET valor = 0"
        result = sql_validator_agent(sample_state)

        assert result["error"] is not None

    def test_reject_insert_statement(self, sample_state):
        from src.agents.sql_validator_agent import sql_validator_agent

        sample_state["generated_sql"] = "INSERT INTO vendas VALUES (1, 2, 3)"
        result = sql_validator_agent(sample_state)

        assert result["error"] is not None

    def test_reject_empty_sql(self, sample_state):
        from src.agents.sql_validator_agent import sql_validator_agent

        sample_state["generated_sql"] = ""
        result = sql_validator_agent(sample_state)

        assert result["error"] is not None

    def test_reject_sql_injection_comment(self, sample_state):
        from src.agents.sql_validator_agent import sql_validator_agent

        sample_state["generated_sql"] = "SELECT id FROM vendas -- DROP TABLE vendas"
        result = sql_validator_agent(sample_state)

        assert result["error"] is not None

    def test_reject_select_star(self, sample_state):
        from src.agents.sql_validator_agent import sql_validator_agent

        sample_state["generated_sql"] = "SELECT * FROM vendas"
        result = sql_validator_agent(sample_state)

        assert result["error"] is not None

    def test_adds_limit_when_missing(self, sample_state):
        from src.agents.sql_validator_agent import sql_validator_agent

        sample_state["generated_sql"] = "SELECT id, valor FROM vendas"
        result = sql_validator_agent(sample_state)

        assert "LIMIT" in result["validated_sql"]

    def test_preserves_existing_limit(self, sample_state):
        from src.agents.sql_validator_agent import sql_validator_agent

        sample_state["generated_sql"] = "SELECT id, valor FROM vendas LIMIT 10"
        result = sql_validator_agent(sample_state)

        assert result["validated_sql"].count("LIMIT") == 1

    def test_increment_retry_count_on_error(self, sample_state):
        from src.agents.sql_validator_agent import sql_validator_agent

        sample_state["generated_sql"] = "DROP TABLE vendas"
        sample_state["retry_count"] = 1

        result = sql_validator_agent(sample_state)

        assert result["retry_count"] == 2

    def test_validate_sql_function_directly(self, sample_schema):
        from src.agents.sql_validator_agent import validate_sql

        is_valid, result = validate_sql(
            "SELECT id, valor FROM vendas WHERE valor > 50",
            sample_schema
        )

        assert is_valid is True
        assert "LIMIT" in result

    def test_reject_union_select_injection(self, sample_state):
        from src.agents.sql_validator_agent import sql_validator_agent

        sample_state["generated_sql"] = "SELECT id FROM vendas UNION SELECT password FROM users"
        result = sql_validator_agent(sample_state)

        assert result["error"] is not None

    def test_reject_table_not_in_schema(self, sample_state):
        from src.agents.sql_validator_agent import sql_validator_agent

        sample_state["generated_sql"] = "SELECT id FROM tabela_inexistente"
        result = sql_validator_agent(sample_state)

        assert result["error"] is not None