import os

import psycopg
from fastapi.testclient import TestClient

from prcp.api.main import app


def test_create_service_endpoint(monkeypatch):
    monkeypatch.setenv("PRCP_DSN", os.environ["PRCP_TEST_DSN"])
    client = TestClient(app)
    try:
        service_response = client.post(
            "/services",
            json={
                "name": "it-persist-check",
                "url": "https://payment.example.com",
            },
        )
        assert service_response.status_code == 201

        service_response = client.get("/services/it-persist-check")

        assert service_response.status_code == 200

        service_response = client.post(
            "/services",
            json={
                "name": "it-persist-check",
                "url": "https://payment.example.com",
            },
        )

        assert service_response.status_code == 409
    finally:
        with psycopg.connect(os.environ["PRCP_TEST_DSN"]) as conn:
            conn.execute("DELETE FROM service WHERE name = %s", ("it-persist-check",))
