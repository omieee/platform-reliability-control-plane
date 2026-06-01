VALID_ENVIRONMENTS = {"dev", "preprod", "prod"}

STATUS_PASS = "pass"
STATUS_FAIL = "fail"
STATUS_UNKNOWN = "unknown"

FAILURE_NONE = "none"
FAILURE_TIMEOUT = "timeout"
FAILURE_CONNECTION_ERROR = "connection_error"
FAILURE_HTTP_STATUS_MISMATCH = "http_status_mismatch"
FAILURE_UNKNOWN_ERROR = "unknown_error"


def create_service(name, environment, base_url):
    if not name:
        raise ValueError("service name is required")

    if environment not in VALID_ENVIRONMENTS:
        raise ValueError("invalid environment")

    if not base_url.startswith(("http://", "https://")):
        raise ValueError("base_url must start with http:// or https://")

    return {
        "name": name,
        "environment": environment,
        "base_url": base_url,
    }


def create_http_probe(service_name, url, expected_status_code=200, timeout_seconds=2.0):
    if not service_name:
        raise ValueError("service_name is required")

    if not url.startswith(("http://", "https://")):
        raise ValueError("url must start with http:// or https://")

    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero")

    return {
        "service_name": service_name,
        "url": url,
        "expected_status_code": expected_status_code,
        "timeout_seconds": timeout_seconds,
    }


def create_probe_result(
    service_name,
    status,
    actual_status_code,
    failure_reason,
    latency_ms,
):
    return {
        "service_name": service_name,
        "status": status,
        "actual_status_code": actual_status_code,
        "failure_reason": failure_reason,
        "latency_ms": latency_ms,
    }
