from dataclasses import dataclass
from enum import StrEnum

from prcp.models import ProbeResult, ProbeStatus


class GateStatus(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class GateDecision:
    status: GateStatus


def decide(results: list[ProbeResult]) -> GateDecision:
    if any(result.status == ProbeStatus.FAIL for result in results):
        return GateDecision(status=GateStatus.BLOCK)

    if results and all(result.status == ProbeStatus.PASS for result in results):
        return GateDecision(status=GateStatus.PASS)

    if any(result.status == ProbeStatus.PASS for result in results):
        return GateDecision(status=GateStatus.WARN)

    return GateDecision(status=GateStatus.UNKNOWN)
