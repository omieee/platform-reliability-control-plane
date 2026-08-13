from http import HTTPMethod

import pytest

from prcp.gate import GateStatus, decide
from prcp.models import (
    FailureReason,
    ProbeResult,
    ProbeStatus,
    create_environment,
    create_http_probe,
    create_probe_result,
    create_service,
)


def make_result(status: ProbeStatus) -> ProbeResult:
    service = create_service("payments", "https://example.com")
    environment = create_environment("prod")
    probe = create_http_probe(
        environment=environment,
        service=service,
        method=HTTPMethod.GET,
        path="/health",
    )

    if status is ProbeStatus.PASS:
        return create_probe_result(
            probe=probe,
            status=status,
            actual_status_code=200,
            failure_reason=None,
            latency_ms=10.0,
        )

    if status is ProbeStatus.FAIL:
        return create_probe_result(
            probe=probe,
            status=status,
            actual_status_code=500,
            failure_reason=FailureReason.HTTP_ERROR,
            latency_ms=10.0,
        )

    return create_probe_result(
        probe=probe,
        status=status,
        actual_status_code=None,
        failure_reason=FailureReason.TIMEOUT,
        latency_ms=None,
    )


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ([], GateStatus.UNKNOWN),
        ([make_result(ProbeStatus.PASS)], GateStatus.PASS),
        (
            [
                make_result(ProbeStatus.PASS),
                make_result(ProbeStatus.FAIL),
            ],
            GateStatus.BLOCK,
        ),
        (
            [
                make_result(ProbeStatus.PASS),
                make_result(ProbeStatus.UNKNOWN),
            ],
            GateStatus.WARN,
        ),
        ([make_result(ProbeStatus.UNKNOWN)], GateStatus.UNKNOWN),
        ([make_result(ProbeStatus.FAIL)], GateStatus.BLOCK),
    ],
)
def test_gate(
    input_value: list[ProbeResult],
    expected: GateStatus,
) -> None:
    decision = decide(input_value)

    assert decision.status == expected
