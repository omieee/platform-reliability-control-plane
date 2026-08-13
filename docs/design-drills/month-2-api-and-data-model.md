# Month 02 — API and Data Model

## Purpose

The purpose of this document is to define how probe results help PRCP make a gate decision about whether a rollout can proceed.

A `Probe` represents the health-check relationship between a service and an environment. A `ProbeResult` records what happened when that probe was executed.

The gate decision is derived from one or more `ProbeResult` values.

---

## Operational Contract

When PRCP cannot determine a service's health with enough confidence, it **does not automatically promote the release**.

The cost is that a potentially healthy release may be delayed and require manual investigation, but PRCP avoids automatically promoting a release when health evidence is incomplete or unavailable.

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

`WARN` does **not** mean automatic promotion. It means the available evidence is partially positive but incomplete, so the rollout requires explicit human review before it can proceed.

### BLOCK

At least one confirmed probe failure exists.

The rollout must not proceed.

### UNKNOWN

PRCP does not have enough evidence to determine whether the rollout is healthy.

By default, `UNKNOWN` does **not** permit promotion.

---

## Gate Input Completeness

`decide(results)` remains a pure function and receives only `ProbeResult` values. It does not query the probe repository and does not know how many probes are registered.

The caller is responsible for determining which probes were expected to report before calling `decide()`.

If a registered probe has no result, the caller represents that missing evidence as an `UNKNOWN` probe result before building the list passed to `decide()`.

At the gate-decision boundary, a probe that could not be observed and a probe that produced no result are therefore treated the same way: both contribute `UNKNOWN` evidence. This is intentional because neither provides enough evidence to declare that probe healthy or failed.

The underlying reason should still be preserved where possible so later alerting and runbooks can distinguish, for example, a timeout from a missing execution.

---

## Gate Decision Table

| Probe results | GateStatus | Why |
|---|---|---|
| Empty | `UNKNOWN` | No probe evidence exists, so PRCP cannot determine health. |
| All `PASS` | `PASS` | Every available probe result confirms the expected health condition. |
| `PASS` + one `FAIL` | `BLOCK` | At least one confirmed probe failure is enough to block promotion. |
| `PASS` + one `UNKNOWN` | `WARN` | Some health evidence is positive, but the overall result is incomplete and requires human review. |
| All `UNKNOWN` | `UNKNOWN` | No probe established either confirmed health or confirmed failure. |
| Multiple `FAIL` | `BLOCK` | Confirmed probe failures exist, so promotion must be blocked. |
| Three probes registered but only one `PASS` result returned | `WARN` | Before `decide()` is called, the two missing probe results are represented as `UNKNOWN`; the function therefore evaluates one `PASS` plus two `UNKNOWN` results. |

---

## Promotion Behaviour

`GateStatus` represents the decision produced from probe evidence.

Promotion behaviour is derived from that decision:

| GateStatus | Promotion behaviour |
|---|---|
| `PASS` | Allow automatic promotion |
| `WARN` | Do not auto-promote; require explicit human review/approval |
| `BLOCK` | Stop promotion |
| `UNKNOWN` | Stop promotion by default |

This separation is intentional:

- `UNKNOWN` means PRCP lacks enough evidence.
- `BLOCK` means PRCP has explicit evidence of failure.

`BLOCK` and `UNKNOWN` stop promotion automatically for different reasons. `WARN` pauses automatic promotion and hands the decision to a human because the evidence is partially positive but incomplete.

## Deffered Decisions:

- **Gate evaluation scope / caller:** Deferred until PRCP defines which probe results constitute one gate evaluation and how expected probes with missing results are normalized before calling `decide(results)`.

- **GateDecision output contract:** Evidence attached to a gate decision is deferred until a real consumer exists. The consumer will determine the minimum useful evidence shape, rather than defining it prematurely.

## Log
- **Synchronous probe execution:** `POST /probes/{probe_id}/run` currently performs the HTTP check inside the request handler. This is acceptable for the current scope but will require reconsideration when probe execution becomes slow, concurrent, scheduled, or asynchronous.