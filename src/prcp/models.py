from dataclasses import dataclass
from enum import StrEnum
from http import HTTPStatus


class ProbeStatus(StrEnum):
    FAIL = "FAIL"
    PASS = "PASS"
    UNKNOWN = "UNKNOWN"


class FailureReason(StrEnum):
    TIMEOUT = "TIMEOUT"
    DNS_ERROR = "DNS_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    HTTP_ERROR = "HTTP_ERROR"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    UNKNOWN = "UNKNOWN"


@dataclass
class Service:
    service_name: str
    service_url: str


@dataclass
class Environment:
    environment_name: str
    region: str | None = None
    cluster: str | None = None


@dataclass
class Probe:
    environment: Environment
    service: Service
    url: str
    expected_status_code: HTTPStatus = HTTPStatus.OK
    timeout_seconds: float = 2.0


@dataclass
class ProbeResult:
    probe: Probe
    status: ProbeStatus
    actual_status_code: HTTPStatus | None
    failure_reason: FailureReason | None
    latency_ms: float | None


def create_environment(
    environment_name: str, region: str | None, cluster: str | None
) -> Environment:
    if not environment_name:
        raise ValueError("environment name is required")
    env: Environment = Environment(
        environment_name=environment_name, region=region, cluster=cluster
    )
    return env


def create_service(service_name: str, service_url: str) -> Service:
    if not service_name:
        raise ValueError("service name is required")
    if not service_url.startswith(("http://", "https://")):
        raise ValueError("service url must start with http:// or https://")
    serv: Service = Service(service_name=service_name, service_url=service_url)
    return serv


def create_http_probe(
    environment: Environment,
    service: Service,
    url: str,
    expected_status_code: HTTPStatus,
    timeout_seconds: float = 2.0,
) -> Probe:
    if not environment:
        raise ValueError("you need to have an environment up and ready")
    if not service:
        raise ValueError("you need to have a service up and ready")
    if not url.startswith(("http://", "https://")):
        raise ValueError("url must start with http:// or https://")
    if timeout_seconds <= 0:
        raise ValueError("timeout seconds must be greater than zero")

    return Probe(
        environment=environment,
        service=service,
        url=url,
        expected_status_code=expected_status_code,
        timeout_seconds=timeout_seconds,
    )


def create_probe_result(
    probe: Probe,
    status: ProbeStatus,
    actual_status_code: HTTPStatus | None,
    failure_reason: FailureReason | None,
    latency_ms: float | None,
) -> ProbeResult:
    return ProbeResult(
        probe=probe,
        status=status,
        actual_status_code=actual_status_code,
        failure_reason=failure_reason,
        latency_ms=latency_ms,
    )
