import time
from collections.abc import Callable

import httpx

from prcp.models import (
    FailureReason,
    Probe,
    ProbeResult,
    ProbeStatus,
    create_probe_result,
)

HttpGet = Callable[..., httpx.Response]


def http_check(
    probe: Probe,
    http_get: HttpGet = httpx.get,
) -> ProbeResult:
    start = time.perf_counter()

    try:
        response = http_get(probe.url, timeout=probe.timeout_seconds)
        latency_ms = (time.perf_counter() - start) * 1000

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
        latency_ms = (time.perf_counter() - start) * 1000

        return create_probe_result(
            probe=probe,
            status=ProbeStatus.FAIL,
            actual_status_code=None,
            failure_reason=FailureReason.TIMEOUT,
            latency_ms=latency_ms,
        )

    except httpx.RequestError:
        latency_ms = (time.perf_counter() - start) * 1000

        return create_probe_result(
            probe=probe,
            status=ProbeStatus.UNKNOWN,
            actual_status_code=None,
            failure_reason=FailureReason.CONNECTION_ERROR,
            latency_ms=latency_ms,
        )
