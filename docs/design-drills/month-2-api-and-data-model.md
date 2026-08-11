# Month 02 - API and Data Model

## Purpose

The purpose of this document is to define how probe results help PRCP make a gate decision about whether a rollout can proceed.

A `Probe` represents the health-check relationship between a service and an environment. A `ProbeResult` records what happened when that probe was executed.

The gate decision is derived from one or more `ProbeResult` values.

---

## Operational Contract

When PRCP cannot determine a service's health, it **stops the promotion by default**.

The cost is that a potentially healthy release may be delayed and require manual investigation, but PRCP avoids promoting a release when it does not have enough evidence to determine that the service is healthy.

---

## Probe Status

```python
class ProbeStatus(StrEnum):
    FAIL = "FAIL"
    PASS = "PASS"
    UNKNOWN = "UNKNOWN"
```

A probe result can have three possible statuses:

### PASS

The probe successfully observed the target and the result matched the probe's expected health condition.

Example:

- expected HTTP status code: `200`
- actual HTTP status code: `200`

### FAIL

The probe successfully observed the target, but the result did not satisfy the expected health condition.

Example:

- expected HTTP status code: `200`
- actual HTTP status code: `500`

### UNKNOWN

PRCP could not obtain enough reliable information to determine whether the target should be considered healthy or unhealthy.

Examples may include:

- timeout
- DNS resolution failure
- connection failure
- unexpected checker-side failure

---

## Failure Reasons

```python
class FailureReason(StrEnum):
    TIMEOUT = "TIMEOUT"
    DNS_ERROR = "DNS_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    HTTP_ERROR = "HTTP_ERROR"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    UNKNOWN = "UNKNOWN"
```

Each failure reason must map to a `ProbeStatus`.

| FailureReason | ProbeStatus | Why |
|---|---|---|
| `TIMEOUT` | `UNKNOWN` | The probe did not receive a valid response within the allowed time, so PRCP cannot establish the target's health. |
| `DNS_ERROR` | `UNKNOWN` | The target could not be resolved, so PRCP could not observe the service itself. |
| `CONNECTION_ERROR` | `UNKNOWN` | A connection to the target could not be established, so PRCP could not obtain a health result from the service. |
| `HTTP_ERROR` | `FAIL` | The target returned an HTTP response that violated the probe's expected health condition. |
| `INVALID_RESPONSE` | `FAIL` | The target responded, but the response was not valid according to the probe contract. |
| `UNKNOWN` | `UNKNOWN` | PRCP encountered a failure that it cannot classify more precisely, so service health cannot be established. |

> `DNS_ERROR` and `INVALID_RESPONSE` must either receive real execution semantics in the checker or be removed later. They should not remain permanently unused enum values.

---

## Probe Result

```python
@dataclass
class ProbeResult:
    probe: Probe
    status: ProbeStatus
    actual_status_code: int | None
    failure_reason: FailureReason | None
    latency_ms: float | None
```

A `ProbeResult` is the evidence used by the gate decision logic.

It records:

- which probe was executed
- whether the probe passed, failed, or remained unknown
- the actual HTTP status code when available
- the reason for failure when applicable
- the observed latency when available

Multiple probe results may contribute to one gate decision.

---

## Gate Status

The gate decision uses four possible states:

```python
class GateStatus(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    BLOCK = "BLOCK"
    UNKNOWN = "UNKNOWN"
```

### PASS

The available probe evidence indicates that the rollout is healthy enough to proceed.

### WARN

The available evidence contains successful probe results, but some results are still unknown.

The rollout may proceed with caution and should surface the uncertainty for manual review or alerting.

### BLOCK

At least one confirmed probe failure exists.

The rollout must not proceed.

### UNKNOWN

PRCP does not have enough evidence to determine whether the rollout is healthy.

By default, `UNKNOWN` does **not** permit promotion.

---

## Gate Decision Table

| Probe results | GateStatus | Why |
|---|---|---|
| Empty | `UNKNOWN` | No probe evidence exists, so PRCP cannot determine health. |
| All `PASS` | `PASS` | Every available probe result confirms the expected health condition. |
| `PASS` + one `FAIL` | `BLOCK` | At least one confirmed probe failure is enough to block promotion. |
| `PASS` + one `UNKNOWN` | `WARN` | Some health evidence is positive, but the overall result is not fully known. |
| All `UNKNOWN` | `UNKNOWN` | No probe established either confirmed health or confirmed failure. |
| Multiple `FAIL` | `BLOCK` | Confirmed probe failures exist, so promotion must be blocked. |
| Three probes registered but only one result returned | `UNKNOWN` | Probe coverage is incomplete, so PRCP does not have enough evidence to determine overall health. |

---

## Promotion Behaviour

`GateStatus` represents the decision produced from probe evidence.

Promotion behaviour is derived from that decision:

| GateStatus | Promotion behaviour |
|---|---|
| `PASS` | Allow promotion |
| `WARN` | Allow promotion with caution/manual review |
| `BLOCK` | Stop promotion |
| `UNKNOWN` | Stop promotion by default |

This separation is intentional:

- `UNKNOWN` means PRCP lacks enough evidence.
- `BLOCK` means PRCP has explicit evidence of failure.

Both stop promotion, but for different reasons.