from dataclasses import dataclass
from enum import IntEnum, StrEnum


class Status(StrEnum):
    FAIL = "FAIL"
    PASS = "PASS"
    UNKNOWN = "UNKNOWN"


class StatusCode(IntEnum):
    FAIL = 0
    PASS = 200
    UNKNOWN = -1


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
    expected_status_code: int = 200
    timeout_seconds: float = 2.0


@dataclass
class ProbeResult:
    probe: Probe
    status: Status
    actual_status_code: StatusCode
    failure_reason: FailureReason | None
    latency_ms: float | None


def create_environment(
    name: str, region: str | None, cluster: str | None
) -> Environment | ValueError:
    if not name:
        raise ValueError("environment name is required")
    env: Environment = Environment(name=name, region=region, cluster=cluster)
    return env


def create_service(name: str, base_url: str | None) -> Service | ValueError:
    if not name:
        raise ValueError("service name is required")
    serv: Service = Service(name=name, base_url=base_url)
    return serv


def create_http_proble(
    environment: Environment,
    service: Service,
    url: str,
    expected_status_code: int = 200,
    timeout_seconds: float = 2.0,
) -> Probe | TypeError:
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


def create_probe_result(probe: Probe) -> ProbeResult:
    return ProbeResult(
        probe=probe,
        status=Status.PASS,
        actual_status_code=StatusCode.PASS,
        failure_reason=None,
        latency_ms=3.0,
    )
