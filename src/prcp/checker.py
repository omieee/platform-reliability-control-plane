import time

import httpx

from prcp.models import (
    FAILURE_CONNECTION_ERROR,
    FAILURE_HTTP_STATUS_MISMATCH,
    FAILURE_NONE,
    FAILURE_TIMEOUT,
    STATUS_FAIL,
    STATUS_PASS,
    STATUS_UNKNOWN,
    create_probe_result,
)


def http_check(probe):
    start = time.perf_counter()

    try:
        response = httpx.get(
            probe["url"],
            timeout=probe["timeout_seconds"],
        )
        latency_ms = (time.perf_counter() - start) * 1000

        if response.status_code == probe["expected_status_code"]:
            return create_probe_result(
                service_name=probe["service_name"],
                status=STATUS_PASS,
                actual_status_code=response.status_code,
                failure_reason=FAILURE_NONE,
                latency_ms=latency_ms,
            )

        return create_probe_result(
            service_name=probe["service_name"],
            status=STATUS_FAIL,
            actual_status_code=response.status_code,
            failure_reason=FAILURE_HTTP_STATUS_MISMATCH,
            latency_ms=latency_ms,
        )

    except httpx.TimeoutException:
        latency_ms = (time.perf_counter() - start) * 1000

        return create_probe_result(
            service_name=probe["service_name"],
            status=STATUS_FAIL,
            actual_status_code=None,
            failure_reason=FAILURE_TIMEOUT,
            latency_ms=latency_ms,
        )

    except httpx.RequestError:
        latency_ms = (time.perf_counter() - start) * 1000

        return create_probe_result(
            service_name=probe["service_name"],
            status=STATUS_UNKNOWN,
            actual_status_code=None,
            failure_reason=FAILURE_CONNECTION_ERROR,
            latency_ms=latency_ms,
        )
