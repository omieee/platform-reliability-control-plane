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


def test_list_services_returns_created_services() -> None:
    testapp.post(
        url="/services",
        json={
            "name": "payments-api",
            "url": "https://payments.demo.com",
        },
    )

    response = testapp.get("/services")

    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "payments-api",
            "url": "https://payments.demo.com",
        }
    ]


def test_get_service_by_name_is_success() -> None:
    testapp.post(
        url="/services",
        json={
            "name": "payments-api",
            "url": "https://payments.demo.com",
        },
    )
    response = testapp.get(url="/services/payments-api")
    assert response.status_code == 200
    assert response.json() == {
        "name": "payments-api",
        "url": "https://payments.demo.com",
    }


def test_get_service_by_name_raise_404_if_not_found() -> None:
    response = testapp.get("/services/missing-service")

    assert response.status_code == 404
    assert response.json() == {"detail": "Service not found"}
