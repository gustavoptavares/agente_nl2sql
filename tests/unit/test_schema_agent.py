import pytest


class TestSchemaAgent:

    def test_introspect_sqlite_database(self, temp_sqlite_db):
        from src.agents.schema_agent import schema_agent

        state = {
            "data_source": "sqlite",
            "connection_string": temp_sqlite_db,
            "messages": []
        }

        result = schema_agent(state)

        assert result["schema"] is not None
        assert "tables" in result["schema"]
        assert len(result["schema"]["tables"]) == 2

    def test_introspect_csv_file(self, temp_csv_file):
        from src.agents.schema_agent import schema_agent

        state = {
            "data_source": "csv",
            "connection_string": temp_csv_file,
            "messages": []
        }

        result = schema_agent(state)

        assert result["schema"] is not None
        assert len(result["schema"]["tables"]) == 1

    def test_introspect_excel_file(self, temp_excel_file):
        from src.agents.schema_agent import schema_agent

        state = {
            "data_source": "excel",
            "connection_string": temp_excel_file,
            "messages": []
        }

        result = schema_agent(state)

        assert result["schema"] is not None
        assert len(result["schema"]["tables"]) >= 1

    def test_handles_invalid_connection(self):
        from src.agents.schema_agent import schema_agent

        state = {
            "data_source": "postgresql",
            "connection_string": "postgresql://invalid:invalid@localhost:9999/nonexistent",
            "messages": []
        }

        result = schema_agent(state)

        assert result["schema"]["tables"] == [] or result.get("error") is not None

    def test_introspect_database_returns_columns(self, temp_sqlite_db):
        from src.agents.schema_agent import introspect_database

        schema = introspect_database(temp_sqlite_db)

        assert len(schema["tables"]) == 2
        vendas_table = next(t for t in schema["tables"] if t["name"] == "vendas")
        assert len(vendas_table["columns"]) == 5

    def test_introspect_csv_returns_columns(self, temp_csv_file):
        from src.agents.schema_agent import introspect_csv

        schema = introspect_csv(temp_csv_file)

        assert len(schema["tables"]) == 1
        assert len(schema["tables"][0]["columns"]) == 4

    def test_introspect_excel_returns_columns(self, temp_excel_file):
        from src.agents.schema_agent import introspect_excel

        schema = introspect_excel(temp_excel_file)

        assert len(schema["tables"]) >= 1
        assert len(schema["tables"][0]["columns"]) == 3

    def test_unknown_data_source_returns_empty(self):
        from src.agents.schema_agent import schema_agent

        state = {
            "data_source": "unknown",
            "connection_string": "",
            "messages": []
        }

        result = schema_agent(state)

        assert result["schema"]["tables"] == []