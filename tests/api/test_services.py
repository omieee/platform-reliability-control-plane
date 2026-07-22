from fastapi.testclient import TestClient


def test_service_create_returns_201(client: TestClient) -> None:
    response = client.post(
        url="/services",
        json={"name": "payments-api", "url": "https://payments.demo.com"},
    )
    assert response.status_code == 201
    assert response.json() == {
        "name": "payments-api",
        "url": "https://payments.demo.com/",
    }


def test_service_name_empty_raise_value_error(client: TestClient) -> None:
    response = client.post(
        url="/services",
        json={"name": "  ", "url": "https://payments.demo.com"},
    )
    assert response.status_code == 422


def test_incorrect_service_url_raise_value_error(client: TestClient) -> None:
    response = client.post(
        url="/services",
        json={"name": "payments-api", "url": "ftp://payment.demo.com"},
    )
    assert response.status_code == 422


def test_list_services_returns_created_services(client: TestClient) -> None:
    client.post(
        url="/services",
        json={
            "name": "payments-api",
            "url": "https://payments.demo.com",
        },
    )

    response = client.get("/services")

    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "payments-api",
            "url": "https://payments.demo.com/",
        }
    ]


def test_get_service_by_name_is_success(client: TestClient) -> None:
    client.post(
        url="/services",
        json={
            "name": "payments-api",
            "url": "https://payments.demo.com",
        },
    )
    response = client.get(url="/services/payments-api")
    assert response.status_code == 200
    assert response.json() == {
        "name": "payments-api",
        "url": "https://payments.demo.com/",
    }


def test_get_service_by_name_raise_404_if_not_found(client: TestClient) -> None:
    response = client.get("/services/missing-service")

    assert response.status_code == 404
    assert response.json() == {"detail": "Service not found"}
