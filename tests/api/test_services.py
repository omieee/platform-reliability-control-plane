from fastapi.testclient import TestClient

from prcp.api.main import app

testapp = TestClient(app=app)


def test_service_crete_returns_201() -> None:
    response = testapp.post(
        url="/services",
        json={"name": "payments-api", "url": "https://payments.demo.com"},
    )
    assert response.status_code == 201
    assert response.json() == {
        "name": "payments-api",
        "url": "https://payments.demo.com",
    }
