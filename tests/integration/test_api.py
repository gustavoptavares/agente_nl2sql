import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestAPI:

    @pytest.fixture
    def client(self):
        from src.api.main import app
        return TestClient(app)

    def test_health_check(self, client):
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client):
        response = client.get("/")

        assert response.status_code == 200
        assert "message" in response.json()

    def test_upload_csv_file(self, client, temp_csv_file):
        with open(temp_csv_file, "rb") as f:
            response = client.post(
                "/api/v1/upload",
                files={"file": ("test.csv", f, "text/csv")}
            )

        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert "filename" in data
        assert "connection_string" in data

    @patch('src.api.routers.nl2sql_router.graph')
    def test_query_endpoint(self, mock_graph, client):
        mock_graph.invoke.return_value = {
            "answer": "Resultado da consulta",
            "validated_sql": "SELECT id FROM test LIMIT 100",
            "query_result": [{"id": 1}],
            "visualization": None,
            "error": None
        }

        response = client.post(
            "/api/v1/query",
            json={
                "question": "Mostre todos os dados",
                "data_source": "sqlite",
                "connection_string": "sqlite:///./test.db"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "session_id" in data

    def test_query_endpoint_missing_connection_string(self, client):
        response = client.post(
            "/api/v1/query",
            json={
                "question": "Mostre todos os dados",
                "data_source": "sqlite"
            }
        )

        assert response.status_code == 400

    def test_schema_endpoint(self, client, temp_sqlite_db):
        response = client.get(
            "/api/v1/schema",
            params={"connection_string": temp_sqlite_db, "data_source": "sqlite"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "tables" in data
        assert len(data["tables"]) == 2

    def test_delete_nonexistent_file(self, client):
        response = client.delete("/api/v1/upload/nonexistent-id")

        assert response.status_code == 404