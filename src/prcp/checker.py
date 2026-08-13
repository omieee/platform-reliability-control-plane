from collections.abc import Callable
from time import perf_counter
from urllib.parse import urljoin

import httpx

from prcp.models import (
    FailureReason,
    Probe,
    ProbeResult,
    ProbeStatus,
    create_probe_result,
)

HttpGet = Callable[[str, float], httpx.Response]


def default_http_get(url: str, timeout: float) -> httpx.Response:
    return httpx.get(url, timeout=timeout)


def http_check(
    probe: Probe,
    http_get: HttpGet = default_http_get,
) -> ProbeResult:
    target_url = urljoin(
        probe.service.url.rstrip("/") + "/",
        probe.path.lstrip("/"),
    )

    started_at = perf_counter()

    try:
        response = http_get(
            target_url,
            probe.timeout_seconds,
        )

        latency_ms = (perf_counter() - started_at) * 1000

        if response.status_code == probe.expected_status_code:
            return create_probe_result(
                probe=probe,
                status=ProbeStatus.PASS,
                actual_status_code=response.status_code,
                failure_reason=None,
                latency_ms=latency_ms,
            )

        return create_probe_result(
            probe=probe,
            status=ProbeStatus.FAIL,
            actual_status_code=response.status_code,
            failure_reason=FailureReason.HTTP_ERROR,
            latency_ms=latency_ms,
        )

    except httpx.TimeoutException:
        latency_ms = (perf_counter() - started_at) * 1000

        return create_probe_result(
            probe=probe,
            status=ProbeStatus.UNKNOWN,
            actual_status_code=None,
            failure_reason=FailureReason.TIMEOUT,
            latency_ms=latency_ms,
        )

    except httpx.RequestError:
        latency_ms = (perf_counter() - started_at) * 1000

        return create_probe_result(
            probe=probe,
            status=ProbeStatus.UNKNOWN,
            actual_status_code=None,
            failure_reason=FailureReason.CONNECTION_ERROR,
            latency_ms=latency_ms,
        )
