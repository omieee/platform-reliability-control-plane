from http import HTTPStatus

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


def test_create_environment_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="environment name is required"):
        create_environment(environment_name="")


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
        url="https://payment.example.com/health",
    )

    assert isinstance(probe, Probe)
    assert probe.environment == environment
    assert probe.service == service
    assert probe.url == "https://payment.example.com/health"
    assert probe.expected_status_code == HTTPStatus.OK
    assert probe.timeout_seconds == 2.0


def test_create_http_probe_accepts_custom_expected_status_and_timeout() -> None:
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
        url="https://payment.example.com/ready",
        expected_status_code=HTTPStatus.NO_CONTENT,
        timeout_seconds=1.5,
    )

    assert probe.expected_status_code == HTTPStatus.NO_CONTENT
    assert probe.timeout_seconds == 1.5


def test_create_http_probe_rejects_missing_environment() -> None:
    service = create_service(
        service_name="payment-api",
        service_url="https://payment.example.com",
    )

    with pytest.raises(ValueError, match="environment"):
        create_http_probe(
            environment=None,
            service=service,
            url="https://payment.example.com/health",
        )


def test_create_http_probe_rejects_missing_service() -> None:
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )

    with pytest.raises(ValueError, match="service"):
        create_http_probe(
            environment=environment,
            service=None,
            url="https://payment.example.com/health",
        )


def test_create_http_probe_rejects_invalid_url() -> None:
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )
    service = create_service(
        service_name="payment-api",
        service_url="https://payment.example.com",
    )

    with pytest.raises(ValueError, match="url must start"):
        create_http_probe(
            environment=environment,
            service=service,
            url="payment.example.com/health",
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

    with pytest.raises(ValueError, match="timeout seconds must be greater than zero"):
        create_http_probe(
            environment=environment,
            service=service,
            url="https://payment.example.com/health",
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
        url="https://payment.example.com/health",
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
        url="https://payment.example.com/health",
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
