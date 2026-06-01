import pytest

from prcp.models import (
    FAILURE_NONE,
    STATUS_PASS,
    create_http_probe,
    create_probe_result,
    create_service,
)


def test_create_service_returns_service_dict():
    service = create_service(
        name="payment-api",
        environment="preprod",
        base_url="https://payment.example.com",
    )

    assert service == {
        "name": "payment-api",
        "environment": "preprod",
        "base_url": "https://payment.example.com",
    }


def test_create_service_rejects_empty_name():
    with pytest.raises(ValueError, match="service name is required"):
        create_service(
            name="",
            environment="preprod",
            base_url="https://payment.example.com",
        )


def test_create_service_rejects_invalid_environment():
    with pytest.raises(ValueError, match="invalid environment"):
        create_service(
            name="payment-api",
            environment="qa",
            base_url="https://payment.example.com",
        )


def test_create_service_rejects_invalid_base_url():
    with pytest.raises(ValueError, match="base_url must start"):
        create_service(
            name="payment-api",
            environment="preprod",
            base_url="payment.example.com",
        )


def test_create_http_probe_returns_probe_dict_with_defaults():
    probe = create_http_probe(
        service_name="payment-api",
        url="https://payment.example.com/health",
    )

    assert probe == {
        "service_name": "payment-api",
        "url": "https://payment.example.com/health",
        "expected_status_code": 200,
        "timeout_seconds": 2.0,
    }


def test_create_http_probe_accepts_custom_expected_status_and_timeout():
    probe = create_http_probe(
        service_name="payment-api",
        url="https://payment.example.com/ready",
        expected_status_code=204,
        timeout_seconds=1.5,
    )

    assert probe["expected_status_code"] == 204
    assert probe["timeout_seconds"] == 1.5


def test_create_http_probe_rejects_empty_service_name():
    with pytest.raises(ValueError, match="service_name is required"):
        create_http_probe(
            service_name="",
            url="https://payment.example.com/health",
        )


def test_create_http_probe_rejects_invalid_url():
    with pytest.raises(ValueError, match="url must start"):
        create_http_probe(
            service_name="payment-api",
            url="payment.example.com/health",
        )


def test_create_http_probe_rejects_non_positive_timeout():
    with pytest.raises(ValueError, match="timeout_seconds must be greater than zero"):
        create_http_probe(
            service_name="payment-api",
            url="https://payment.example.com/health",
            timeout_seconds=0,
        )


def test_create_probe_result_returns_result_dict():
    result = create_probe_result(
        service_name="payment-api",
        status=STATUS_PASS,
        actual_status_code=200,
        failure_reason=FAILURE_NONE,
        latency_ms=25.5,
    )

    assert result == {
        "service_name": "payment-api",
        "status": STATUS_PASS,
        "actual_status_code": 200,
        "failure_reason": FAILURE_NONE,
        "latency_ms": 25.5,
    }
