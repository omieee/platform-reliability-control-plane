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


def test_service_name_empty_raise_value_error() -> None:
    response = testapp.post(
        url="/services",
        json={"name": "  ", "url": "https://payments.demo.com"},
    )
    assert response.status_code == 422


def test_incorrect_service_url_raise_value_error() -> None:
    response = testapp.post(
        url="/services",
        json={"name": "payments-api", "url": "ftp://payment.demo.com"},
    )
    assert response.status_code == 422
