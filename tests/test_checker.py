from http import HTTPMethod, HTTPStatus
from unittest.mock import Mock, patch

import httpx

from prcp.checker import default_http_get, http_check
from prcp.models import (
    FailureReason,
    Probe,
    ProbeStatus,
    create_environment,
    create_http_probe,
    create_service,
)


def create_test_probe(
    expected_status_code: HTTPStatus = HTTPStatus.OK,
) -> Probe:
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )
    service = create_service(
        service_name="payment-api",
        service_url="https://payment.example.com",
    )

    return create_http_probe(
        environment=environment,
        service=service,
        method=HTTPMethod.GET,
        path="/health",
        expected_status_code=expected_status_code,
        timeout_seconds=2.0,
    )


def test_http_check_returns_pass_when_status_matches() -> None:
    def fake_http_get(url: str, timeout: float) -> httpx.Response:
        assert url == "https://payment.example.com/health"
        assert timeout == 2.0
        return httpx.Response(status_code=200)

    probe = create_test_probe(expected_status_code=HTTPStatus.OK)

    result = http_check(probe, http_get=fake_http_get)

    assert result.probe == probe
    assert result.status == ProbeStatus.PASS
    assert result.actual_status_code == 200
    assert result.failure_reason is None
    assert result.latency_ms is not None
    assert result.latency_ms >= 0


def test_http_check_returns_fail_when_status_does_not_match() -> None:
    def fake_http_get(url: str, timeout: float) -> httpx.Response:
        assert url == "https://payment.example.com/health"
        assert timeout == 2.0
        return httpx.Response(status_code=500)

    probe = create_test_probe(expected_status_code=HTTPStatus.OK)

    result = http_check(probe, http_get=fake_http_get)

    assert result.probe == probe
    assert result.status == ProbeStatus.FAIL
    assert result.actual_status_code == 500
    assert result.failure_reason == FailureReason.HTTP_ERROR
    assert result.latency_ms is not None
    assert result.latency_ms >= 0


def test_http_check_uses_custom_expected_status_code() -> None:
    def fake_http_get(url: str, timeout: float) -> httpx.Response:
        assert url == "https://payment.example.com/health"
        assert timeout == 2.0
        return httpx.Response(status_code=204)

    probe = create_test_probe(
        expected_status_code=HTTPStatus.NO_CONTENT,
    )

    result = http_check(probe, http_get=fake_http_get)

    assert result.status == ProbeStatus.PASS
    assert result.actual_status_code == 204
    assert result.failure_reason is None


def test_http_check_returns_fail_on_timeout() -> None:
    def fake_http_get(url: str, timeout: float) -> httpx.Response:
        assert url == "https://payment.example.com/health"
        assert timeout == 2.0
        raise httpx.TimeoutException("request timed out")

    probe = create_test_probe(expected_status_code=HTTPStatus.OK)

    result = http_check(probe, http_get=fake_http_get)

    assert result.probe == probe
    assert result.status == ProbeStatus.FAIL
    assert result.actual_status_code is None
    assert result.failure_reason == FailureReason.TIMEOUT
    assert result.latency_ms is not None
    assert result.latency_ms >= 0


def test_http_check_returns_unknown_on_request_error() -> None:
    def fake_http_get(url: str, timeout: float) -> httpx.Response:
        assert url == "https://payment.example.com/health"
        assert timeout == 2.0
        raise httpx.RequestError("connection failed")

    probe = create_test_probe(expected_status_code=HTTPStatus.OK)

    result = http_check(probe, http_get=fake_http_get)

    assert result.probe == probe
    assert result.status == ProbeStatus.UNKNOWN
    assert result.actual_status_code is None
    assert result.failure_reason == FailureReason.CONNECTION_ERROR
    assert result.latency_ms is not None
    assert result.latency_ms >= 0


def test_default_http_get_calls_httpx_get() -> None:
    expected_response = Mock(spec=httpx.Response)

    with patch(
        "prcp.checker.httpx.get",
        return_value=expected_response,
    ) as mock_get:
        response = default_http_get(
            url="https://payment.example.com/health",
            timeout=2.0,
        )

    mock_get.assert_called_once_with(
        "https://payment.example.com/health",
        timeout=2.0,
    )
    assert response is expected_response
