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
        pytest.param(
            [],
            GateStatus.UNKNOWN,
            id="empty_results_produce_unknown",
        ),
        pytest.param(
            [make_result(ProbeStatus.PASS)],
            GateStatus.PASS,
            id="single_pass_produces_pass",
        ),
        pytest.param(
            [
                make_result(ProbeStatus.PASS),
                make_result(ProbeStatus.PASS),
            ],
            GateStatus.PASS,
            id="multiple_pass_produces_pass",
        ),
        pytest.param(
            [
                make_result(ProbeStatus.PASS),
                make_result(ProbeStatus.FAIL),
            ],
            GateStatus.BLOCK,
            id="pass_and_fail_produce_block",
        ),
        pytest.param(
            [
                make_result(ProbeStatus.PASS),
                make_result(ProbeStatus.UNKNOWN),
            ],
            GateStatus.WARN,
            id="pass_and_unknown_produce_warn",
        ),
        pytest.param(
            [make_result(ProbeStatus.UNKNOWN)],
            GateStatus.UNKNOWN,
            id="all_unknown_produces_unknown",
        ),
        pytest.param(
            [make_result(ProbeStatus.FAIL)],
            GateStatus.BLOCK,
            id="single_fail_produces_block",
        ),
        pytest.param(
            [
                make_result(ProbeStatus.FAIL),
                make_result(ProbeStatus.FAIL),
            ],
            GateStatus.BLOCK,
            id="multiple_fail_produces_block",
        ),
    ],
)
def test_gate(
    input_value: list[ProbeResult],
    expected: GateStatus,
) -> None:
    decision = decide(input_value)

    assert decision.status == expected
