from http import HTTPMethod, HTTPStatus
from uuid import UUID

import pytest

from prcp.models import (
    Environment,
    FailureReason,
    Probe,
    ProbeResult,
    ProbeStatus,
    Service,
    create_environment,
    create_http_probe,
    create_probe_result,
    create_service,
)


def test_create_environment_returns_environment() -> None:
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
        cluster="cluster-1",
    )

    assert isinstance(environment, Environment)
    assert environment.name == "preprod"
    assert environment.region == "us-south"
    assert environment.cluster == "cluster-1"


def test_create_environment_rejects_whitespace_only_name() -> None:
    with pytest.raises(ValueError, match="environment name is required"):
        create_environment(environment_name="   ")


def test_create_environment_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="environment name is required"):
        create_environment(environment_name="")


def test_create_environment_normalizes_name():
    env = create_environment("  PROD  ", region="eu-prod", cluster="k1")
    assert env.name == "prod"


def test_create_service_returns_service() -> None:
    service = create_service(
        service_name="payment-api",
        service_url="https://payment.example.com",
    )

    assert isinstance(service, Service)
    assert service.name == "payment-api"
    assert service.url == "https://payment.example.com"


def test_create_service_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="service name is required"):
        create_service(
            service_name="",
            service_url="https://payment.example.com",
        )


def test_create_service_rejects_invalid_url() -> None:
    with pytest.raises(
        ValueError, match="service URL must be a valid HTTP or HTTPS URL"
    ):
        create_service(
            service_name="payment-api",
            service_url="payment.example.com",
        )


def test_create_service_rejects_whitespace_only_name() -> None:
    with pytest.raises(ValueError, match="service name is required"):
        create_service("   ", "https://example.com")


def test_create_http_probe_returns_probe_with_defaults() -> None:
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )
    service = create_service(
        service_name="payment-api",
        service_url="https://payment.example.com",
    )

    probe = create_http_probe(
        environment=environment,
        service=service,
        method=HTTPMethod.GET,
        path="/health",
    )

    assert isinstance(probe, Probe)
    assert isinstance(probe.id, UUID)
    assert probe.environment == environment
    assert probe.service == service
    assert probe.method == HTTPMethod.GET
    assert probe.path == "/health"
    assert probe.expected_status_code == HTTPStatus.OK
    assert probe.timeout_seconds == 2.0


def test_create_http_probe_accepts_custom_values() -> None:
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )
    service = create_service(
        service_name="payment-api",
        service_url="https://payment.example.com",
    )

    probe = create_http_probe(
        environment=environment,
        service=service,
        method=HTTPMethod.POST,
        path="/ready",
        expected_status_code=HTTPStatus.NO_CONTENT,
        timeout_seconds=1.5,
    )

    assert probe.method == HTTPMethod.POST
    assert probe.path == "/ready"
    assert probe.expected_status_code == HTTPStatus.NO_CONTENT
    assert probe.timeout_seconds == 1.5


def test_create_http_probe_normalizes_path() -> None:
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )
    service = create_service(
        service_name="payment-api",
        service_url="https://payment.example.com",
    )

    probe = create_http_probe(
        environment=environment,
        service=service,
        method=HTTPMethod.GET,
        path="  health  ",
    )

    assert probe.path == "/health"


def test_create_http_probe_rejects_missing_environment() -> None:
    service = create_service(
        service_name="payment-api",
        service_url="https://payment.example.com",
    )

    with pytest.raises(ValueError, match="environment is required"):
        create_http_probe(
            environment=None,
            service=service,
            method=HTTPMethod.GET,
            path="/health",
        )


def test_create_http_probe_rejects_missing_service() -> None:
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )

    with pytest.raises(ValueError, match="service is required"):
        create_http_probe(
            environment=environment,
            service=None,
            method=HTTPMethod.GET,
            path="/health",
        )


def test_create_http_probe_rejects_invalid_url() -> None:
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )

    # Construct directly so create_service() does not reject it first.
    invalid_service = Service(
        name="payment-api",
        url="ftp://payment.example.com",
    )

    with pytest.raises(
        ValueError,
        match="probe URL must be a valid HTTP or HTTPS URL",
    ):
        create_http_probe(
            environment=environment,
            service=invalid_service,
            method=HTTPMethod.GET,
            path="/health",
        )


def test_create_http_probe_rejects_non_positive_timeout() -> None:
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )
    service = create_service(
        service_name="payment-api",
        service_url="https://payment.example.com",
    )

    with pytest.raises(
        ValueError,
        match="timeout seconds must be greater than zero",
    ):
        create_http_probe(
            environment=environment,
            service=service,
            method=HTTPMethod.GET,
            path="/health",
            timeout_seconds=0,
        )


def test_create_probe_result_returns_probe_result() -> None:
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )
    service = create_service(
        service_name="payment-api",
        service_url="https://payment.example.com",
    )
    probe = create_http_probe(
        environment=environment,
        service=service,
        method=HTTPMethod.GET,
        path="/health",
    )

    probe_result = create_probe_result(
        probe=probe,
        status=ProbeStatus.PASS,
        actual_status_code=200,
        failure_reason=None,
        latency_ms=25.5,
    )

    assert isinstance(probe_result, ProbeResult)
    assert probe_result.probe == probe
    assert probe_result.status == ProbeStatus.PASS
    assert probe_result.actual_status_code == 200
    assert probe_result.failure_reason is None
    assert probe_result.latency_ms == 25.5


def test_create_probe_result_can_store_failure_reason() -> None:
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )
    service = create_service(
        service_name="payment-api",
        service_url="https://payment.example.com",
    )
    probe = create_http_probe(
        environment=environment,
        service=service,
        method=HTTPMethod.GET,
        path="/health",
    )

    probe_result = create_probe_result(
        probe=probe,
        status=ProbeStatus.FAIL,
        actual_status_code=500,
        failure_reason=FailureReason.HTTP_ERROR,
        latency_ms=30.0,
    )

    assert probe_result.status == ProbeStatus.FAIL
    assert probe_result.actual_status_code == 500
    assert probe_result.failure_reason == FailureReason.HTTP_ERROR
