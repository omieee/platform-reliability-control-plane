from http import HTTPMethod

import pytest
from fastapi.testclient import TestClient

from prcp.models import (
    FailureReason,
    Probe,
    ProbeResult,
    ProbeStatus,
    create_environment,
    create_http_probe,
    create_probe_result,
    create_service,
)
from prcp.repository import (
    InMemoryProbeRepository,
    InMemoryProbeResultRepository,
)


def make_probe() -> Probe:
    service = create_service(
        service_name="payments",
        service_url="https://example.com",
    )

    environment = create_environment(
        environment_name="prod", region="local", cluster="local"
    )

    return create_http_probe(
        environment=environment,
        service=service,
        method=HTTPMethod.GET,
        path="/health",
    )


def make_result(
    probe: Probe,
    status: ProbeStatus,
) -> ProbeResult:
    if status == ProbeStatus.PASS:
        return create_probe_result(
            probe=probe,
            status=ProbeStatus.PASS,
            actual_status_code=200,
            failure_reason=None,
            latency_ms=10.0,
        )

    if status == ProbeStatus.FAIL:
        return create_probe_result(
            probe=probe,
            status=ProbeStatus.FAIL,
            actual_status_code=500,
            failure_reason=FailureReason.HTTP_ERROR,
            latency_ms=20.0,
        )

    return create_probe_result(
        probe=probe,
        status=ProbeStatus.UNKNOWN,
        actual_status_code=None,
        failure_reason=FailureReason.TIMEOUT,
        latency_ms=None,
    )


def test_run_probe_returns_and_stores_result(
    client: TestClient,
    probe_repository: InMemoryProbeRepository,
    probe_result_repository: InMemoryProbeResultRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    probe = make_probe()
    probe_repository.save(probe)

    expected_result = make_result(probe, ProbeStatus.PASS)

    monkeypatch.setattr(
        "prcp.api.main.http_check",
        lambda _: expected_result,
    )

    response = client.post(f"/probes/{probe.id}/run")

    assert response.status_code == 200
    assert response.json() == {
        "probe_id": str(probe.id),
        "status": "PASS",
        "actual_status_code": 200,
        "failure_reason": None,
        "latency_ms": 10.0,
    }

    stored_results = probe_result_repository.list_for_probe(probe.id)

    assert stored_results == [expected_result]


def test_run_unknown_probe_returns_404(
    client: TestClient,
) -> None:
    probe = make_probe()

    response = client.post(f"/probes/{probe.id}/run")

    assert response.status_code == 404


def test_get_results_returns_empty_list_for_probe_without_results(
    client: TestClient,
    probe_repository: InMemoryProbeRepository,
) -> None:
    probe = make_probe()
    probe_repository.save(probe)

    response = client.get(f"/probes/{probe.id}/results")

    assert response.status_code == 200
    assert response.json() == []


def test_get_results_returns_history_in_insertion_order(
    client: TestClient,
    probe_repository: InMemoryProbeRepository,
    probe_result_repository: InMemoryProbeResultRepository,
) -> None:
    probe = make_probe()
    probe_repository.save(probe)

    first_result = make_result(probe, ProbeStatus.PASS)
    second_result = make_result(probe, ProbeStatus.UNKNOWN)
    third_result = make_result(probe, ProbeStatus.FAIL)

    probe_result_repository.add(first_result)
    probe_result_repository.add(second_result)
    probe_result_repository.add(third_result)

    response = client.get(f"/probes/{probe.id}/results")

    assert response.status_code == 200

    results = response.json()

    assert [result["status"] for result in results] == [
        "PASS",
        "UNKNOWN",
        "FAIL",
    ]

    assert all(result["probe_id"] == str(probe.id) for result in results)


def test_get_results_for_unknown_probe_returns_404(
    client: TestClient,
) -> None:
    probe = make_probe()

    response = client.get(f"/probes/{probe.id}/results")

    assert response.status_code == 404
