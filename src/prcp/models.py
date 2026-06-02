from dataclasses import dataclass
from enum import StrEnum
from http import HTTPStatus


class Status(StrEnum):
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
    name: str
    base_url: str | None


@dataclass
class Environment:
    name: str
    region: str | None
    cluster: str | None


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
    status: Status
    actual_status_code: HTTPStatus | None
    failure_reason: FailureReason | None
    timeout_seconds: float | None


def create_environment(
    name: str, region: str | None, cluster: str | None
) -> Environment:
    if not name:
        raise ValueError("environment name is required")
    env: Environment = Environment(name=name, region=region, cluster=cluster)
    return env


def create_service(name: str, base_url: str | None) -> Service:
    if not name:
        raise ValueError("service name is required")
    serv: Service = Service(name=name, base_url=base_url)
    return serv


def create_http_proble(
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
        expected_status_code=HTTPStatus.OK,
        timeout_seconds=timeout_seconds,
    )


def create_probe_result(probe: Probe) -> ProbeResult:
    return ProbeResult(
        probe=probe,
        status=Status.PASS,
        actual_status_code=HTTPStatus.OK,
        failure_reason=None,
        timeout_seconds=3.0,
    )
