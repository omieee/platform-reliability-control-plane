import os

import psycopg
from fastapi.testclient import TestClient

from prcp.api.main import app


def test_create_service_endpoint(monkeypatch):
    monkeypatch.setenv("PRCP_DSN", os.environ["PRCP_TEST_DSN"])
    client = TestClient(app)
    service_response = client.post(
        "/services",
        json={
            "name": "payment-api",
            "url": "https://payment.example.com",
        },
    )
    assert service_response.status_code == 201

    service_response = client.get("/services")

    assert service_response.status_code == 200

    service_response = client.post(
        "/services",
        json={
            "name": "payment-api",
            "url": "https://payment.example.com",
        },
    )

    assert service_response.status_code == 409

    with psycopg.connect(os.environ["PRCP_TEST_DSN"]) as conn:
        conn.execute("DELETE FROM service WHERE name = %s", ("payment-api",))
