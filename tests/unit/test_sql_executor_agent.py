import pytest


class TestSQLExecutorAgent:

    def test_execute_sqlite_query(self, temp_sqlite_db):
        from src.agents.sql_executor_agent import sql_executor_agent

        state = {
            "validated_sql": "SELECT id, valor FROM vendas LIMIT 10",
            "data_source": "sqlite",
            "connection_string": temp_sqlite_db,
            "messages": []
        }

        result = sql_executor_agent(state)

        assert result["query_result"] is not None
        assert len(result["query_result"]) > 0
        assert result["error"] is None

    def test_execute_csv_query(self, temp_csv_file):
        from src.agents.sql_executor_agent import sql_executor_agent
        import os

        table_name = os.path.basename(temp_csv_file).replace(".csv", "")

        state = {
            "validated_sql": f'SELECT id, valor FROM "{table_name}" LIMIT 10',
            "data_source": "csv",
            "connection_string": temp_csv_file,
            "messages": []
        }

        result = sql_executor_agent(state)

        assert result["query_result"] is not None
        assert result["error"] is None

    def test_handles_empty_sql(self):
        from src.agents.sql_executor_agent import sql_executor_agent

        state = {
            "validated_sql": "",
            "data_source": "sqlite",
            "connection_string": "",
            "messages": []
        }

        result = sql_executor_agent(state)

        assert result["error"] is not None

    def test_handles_invalid_sql(self, temp_sqlite_db):
        from src.agents.sql_executor_agent import sql_executor_agent

        state = {
            "validated_sql": "SELECT col FROM nonexistent_table",
            "data_source": "sqlite",
            "connection_string": temp_sqlite_db,
            "messages": []
        }

        result = sql_executor_agent(state)

        assert result["error"] is not None

    def test_handles_none_sql(self):
        from src.agents.sql_executor_agent import sql_executor_agent

        state = {
            "validated_sql": None,
            "data_source": "sqlite",
            "connection_string": "",
            "messages": []
        }

        result = sql_executor_agent(state)

        assert result["error"] is not None

    def test_execute_sql_database_directly(self, temp_sqlite_db):
        from src.agents.sql_executor_agent import execute_sql_database

        result = execute_sql_database(temp_sqlite_db, "SELECT id, valor FROM vendas")

        assert len(result) == 3
        assert "id" in result[0]
        assert "valor" in result[0]

    def test_execute_returns_correct_data(self, temp_sqlite_db):
        from src.agents.sql_executor_agent import sql_executor_agent

        state = {
            "validated_sql": "SELECT cliente_id, SUM(valor) as total FROM vendas GROUP BY cliente_id",
            "data_source": "sqlite",
            "connection_string": temp_sqlite_db,
            "messages": []
        }

        result = sql_executor_agent(state)

        assert result["query_result"] is not None
        assert len(result["query_result"]) == 2