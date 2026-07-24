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


def test_invalid_url_returns_validation_error(client: TestClient) -> None:
    response = client.post(
        url="/services",
        json={"name": "payments-api", "url": "ftp://payment.demo.com"},
    )
    assert response.status_code == 422
    body = response.json()

    assert body["type"] == "urn:prcp:error:validation-failed"
    assert body["title"] == "Validation failed"
    assert body["status"] == 422
    assert body["detail"] == "One or more request fields are invalid."
    assert body["instance"] == "/services"

    assert body["errors"][0]["field"] == "body.url"
    assert "URL scheme" in body["errors"][0]["message"]


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
    assert response.json() == {
        "detail": "Service not found",
        "instance": "/services/missing-service",
        "status": 404,
        "title": "Not Found",
        "type": "urn:prcp:error:http-404",
    }


def test_duplicate_service_returns_409(client: TestClient) -> None:
    payload = {
        "name": "payment-api",
        "url": "https://payments.example.com",
    }

    first_response = client.post("/services", json=payload)
    second_response = client.post("/services", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Service 'payment-api' already exists",
        "instance": "/services",
        "status": 409,
        "title": "Service already exists",
        "type": "urn:prcp:error:service-conflict",
    }


def test_duplicate_service_does_not_overwrite_original(client: TestClient) -> None:
    client.post(
        "/services",
        json={
            "name": "payment-api",
            "url": "https://version-one.example.com",
        },
    )

    duplicate_response = client.post(
        "/services",
        json={
            "name": "PAYMENT-API",
            "url": "https://version-two.example.com",
        },
    )

    stored_response = client.get("/services/payment-api")

    assert duplicate_response.status_code == 409
    assert stored_response.json()["url"] == "https://version-one.example.com/"
