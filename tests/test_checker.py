import httpx

from prcp import checker
from prcp.models import (
    FAILURE_CONNECTION_ERROR,
    FAILURE_HTTP_STATUS_MISMATCH,
    FAILURE_NONE,
    FAILURE_TIMEOUT,
    STATUS_FAIL,
    STATUS_PASS,
    STATUS_UNKNOWN,
    create_http_probe,
)


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code


def test_http_check_returns_pass_when_status_matches(monkeypatch):
    def fake_get(url, timeout):
        return FakeResponse(status_code=200)

    monkeypatch.setattr(checker.httpx, "get", fake_get)

    probe = create_http_probe(
        service_name="payment-api",
        url="https://payment.example.com/health",
    )

    result = checker.http_check(probe)

    assert result["service_name"] == "payment-api"
    assert result["status"] == STATUS_PASS
    assert result["actual_status_code"] == 200
    assert result["failure_reason"] == FAILURE_NONE
    assert result["latency_ms"] >= 0


def test_http_check_returns_fail_when_status_does_not_match(monkeypatch):
    def fake_get(url, timeout):
        return FakeResponse(status_code=500)

    monkeypatch.setattr(checker.httpx, "get", fake_get)

    probe = create_http_probe(
        service_name="payment-api",
        url="https://payment.example.com/health",
    )

    result = checker.http_check(probe)

    assert result["service_name"] == "payment-api"
    assert result["status"] == STATUS_FAIL
    assert result["actual_status_code"] == 500
    assert result["failure_reason"] == FAILURE_HTTP_STATUS_MISMATCH
    assert result["latency_ms"] >= 0


def test_http_check_uses_expected_status_code(monkeypatch):
    def fake_get(url, timeout):
        return FakeResponse(status_code=204)

    monkeypatch.setattr(checker.httpx, "get", fake_get)

    probe = create_http_probe(
        service_name="payment-api",
        url="https://payment.example.com/ready",
        expected_status_code=204,
    )

    result = checker.http_check(probe)

    assert result["status"] == STATUS_PASS
    assert result["actual_status_code"] == 204
    assert result["failure_reason"] == FAILURE_NONE


def test_http_check_returns_fail_on_timeout(monkeypatch):
    def fake_get(url, timeout):
        raise httpx.TimeoutException("request timed out")

    monkeypatch.setattr(checker.httpx, "get", fake_get)

    probe = create_http_probe(
        service_name="payment-api",
        url="https://payment.example.com/health",
        timeout_seconds=1.0,
    )

    result = checker.http_check(probe)

    assert result["service_name"] == "payment-api"
    assert result["status"] == STATUS_FAIL
    assert result["actual_status_code"] is None
    assert result["failure_reason"] == FAILURE_TIMEOUT
    assert result["latency_ms"] >= 0


def test_http_check_returns_unknown_on_request_error(monkeypatch):
    def fake_get(url, timeout):
        raise httpx.RequestError("connection failed")

    monkeypatch.setattr(checker.httpx, "get", fake_get)

    probe = create_http_probe(
        service_name="payment-api",
        url="https://payment.example.com/health",
    )

    result = checker.http_check(probe)

    assert result["service_name"] == "payment-api"
    assert result["status"] == STATUS_UNKNOWN
    assert result["actual_status_code"] is None
    assert result["failure_reason"] == FAILURE_CONNECTION_ERROR
    assert result["latency_ms"] >= 0
