from http import HTTPMethod
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from prcp.api.schemas import ProbeCreate
from prcp.exceptions import DuplicateProbeError
from prcp.models import (
    create_environment,
    create_http_probe,
    create_service,
)
from prcp.repository import InMemoryProbeRepository


def test_probe_create_returns_201(client: TestClient) -> None:
    service_response = client.post(
        url="/services",
        json={
            "name": "payment-api",
            "url": "https://payment.example.com",
        },
    )
    assert service_response.status_code == 201

    environment_response = client.post(
        url="/environments",
        json={
            "name": "dev-us-south",
            "region": "us-south",
            "cluster": "dev-cluster",
        },
    )
    assert environment_response.status_code == 201

    probe_response = client.post(
        url="/probes",
        json={
            "service_name": "payment-api",
            "environment_name": "dev-us-south",
            "method": "GET",
            "path": "/health",
            "expected_status_code": 200,
            "timeout_seconds": 2.0,
        },
    )

    assert probe_response.status_code == 201

    response_body = probe_response.json()

    assert UUID(response_body["id"])
    assert response_body == {
        "id": response_body["id"],
        "service_name": "payment-api",
        "environment_name": "dev-us-south",
        "method": "GET",
        "path": "/health",
        "expected_status_code": 200,
        "timeout_seconds": 2.0,
    }


def test_probe_create_returns_404_when_service_not_found(
    client: TestClient,
) -> None:
    # Environment exists, but service does not.
    environment_response = client.post(
        url="/environments",
        json={
            "name": "dev-us-south",
            "region": "us-south",
            "cluster": "dev-cluster",
        },
    )
    assert environment_response.status_code == 201

    response = client.post(
        url="/probes",
        json={
            "service_name": "missing-service",
            "environment_name": "dev-us-south",
            "method": "GET",
            "path": "/health",
            "expected_status_code": 200,
            "timeout_seconds": 2.0,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "type": "urn:prcp:error:http-404",
        "title": "Not Found",
        "status": 404,
        "detail": "Service 'missing-service' not found",
        "instance": "/probes",
    }


def test_probe_create_returns_404_when_environment_not_found(
    client: TestClient,
) -> None:
    # Service exists, but environment does not.
    service_response = client.post(
        url="/services",
        json={
            "name": "payment-api",
            "url": "https://payment.example.com",
        },
    )
    assert service_response.status_code == 201

    response = client.post(
        url="/probes",
        json={
            "service_name": "payment-api",
            "environment_name": "missing-environment",
            "method": "GET",
            "path": "/health",
            "expected_status_code": 200,
            "timeout_seconds": 2.0,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "type": "urn:prcp:error:http-404",
        "title": "Not Found",
        "status": 404,
        "detail": "Environment 'missing-environment' not found",
        "instance": "/probes",
    }


@pytest.mark.parametrize(
    "field_name",
    ["service_name", "environment_name"],
)
def test_probe_create_rejects_empty_reference_name(
    field_name: str,
) -> None:
    payload = {
        "service_name": "payment-api",
        "environment_name": "dev-us-south",
        "method": "GET",
        "path": "/health",
    }
    payload[field_name] = "   "

    with pytest.raises(ValidationError) as exc_info:
        ProbeCreate(**payload)

    error = exc_info.value.errors()[0]

    assert error["loc"] == (field_name,)
    assert "name cannot be empty" in error["msg"]


def test_probe_create_returns_422_for_empty_service_name(
    client: TestClient,
) -> None:
    response = client.post(
        "/probes",
        json={
            "service_name": "   ",
            "environment_name": "dev-us-south",
            "method": "GET",
            "path": "/health",
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["errors"][0]["field"] == "body.service_name"
    assert "name cannot be empty" in body["errors"][0]["message"]


def test_duplicate_probe_error_contains_existing_probe_id() -> None:
    existing_probe_id = uuid4()

    error = DuplicateProbeError(existing_probe_id)

    assert error.existing_probe_id == existing_probe_id
    assert error.status == 409
    assert error.title == "Probe already exists"
    assert error.error_type == "urn:prcp:error:probe-conflict"
    assert error.detail == (f"Probe already exists with ID '{existing_probe_id}'")
    assert str(error) == (f"Probe already exists with ID '{existing_probe_id}'")


def test_probe_repository_duplicate_returns_existing_probe_id() -> None:
    repository = InMemoryProbeRepository()

    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )
    service = create_service(
        service_name="payment-api",
        service_url="https://payment.example.com",
    )

    first_probe = create_http_probe(
        environment=environment,
        service=service,
        method=HTTPMethod.GET,
        path="/health",
    )

    duplicate_probe = create_http_probe(
        environment=environment,
        service=service,
        method=HTTPMethod.GET,
        path="/health",
    )

    assert first_probe.id != duplicate_probe.id

    repository.save(first_probe)

    with pytest.raises(DuplicateProbeError) as exc_info:
        repository.save(duplicate_probe)

    assert exc_info.value.existing_probe_id == first_probe.id
    assert exc_info.value.detail == (f"Probe already exists with ID '{first_probe.id}'")
    assert repository.get_by_id(first_probe.id) == first_probe
    assert repository.get_by_id(duplicate_probe.id) is None
    assert repository.list_all() == [first_probe]
