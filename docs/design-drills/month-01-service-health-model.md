# Month 1 Service Health Model

## Purpose

This document defines the raw outcomes produced when PRCP probes a service endpoint.

It does not decide whether a release or promotion should result in `PASS`, `WARN`, `BLOCK`, or `UNKNOWN`. Gate-decision mapping will be designed separately after retry, decision-table, and idempotency rules are studied.

## Probe Result Data

Every probe result should capture:

- Probe timestamp
    
- Target endpoint
    
- HTTP method
    
- Elapsed time or latency
    
- Outcome category
    
- HTTP status code, when a response was received
    
- Error message, when applicable
    
- Configured timeout
    
- Attempt number, when retries are introduced
    

Latency should be recorded for both successful and failed attempts. For failures such as timeout or connection errors, it represents how long the probe ran before failing.

## Successful Probe

### HTTP Response Received

**Meaning:** The target returned a valid HTTP response.

**Data stored:**

- HTTP status code
    
- Response latency
    
- Probe timestamp
    
- Target endpoint
    

Receiving an HTTP response does not automatically mean that the service is healthy. Interpretation of the status code and response body belongs to later decision logic.

## Failure Categories

### Timeout

**Meaning:** The request did not finish within the configured timeout.

**Potentially retryable:** Yes. The final retry policy will be decided later.

**Data stored:**

- Configured timeout
    
- Elapsed time
    
- Target endpoint
    
- Error details
    
- Probe timestamp
    

### DNS Resolution Failure

**Meaning:** The hostname could not be converted into an IP address.

**Potentially retryable:** Yes.

**Data stored:**

- Hostname
    
- Resolver error
    
- Elapsed time
    
- Probe timestamp
    

A DNS failure does not by itself determine whether the monitored service is unhealthy. The failure could come from the service configuration, the DNS system, or the machine running the probe.

### Connection Refused

**Meaning:** The destination host was reached, but the connection was rejected on the requested port.

**Potentially retryable:** Yes.

**Data stored:**

- Host and port
    
- Elapsed time
    
- Connection error
    
- Probe timestamp
    

### TLS Failure

**Meaning:** The HTTPS connection could not be established because certificate validation or the TLS handshake failed.

**Potentially retryable:** Depends on the cause. An expired or invalid certificate is unlikely to recover through an immediate retry.

**Data stored:**

- Target hostname
    
- TLS error
    
- Elapsed time
    
- Probe timestamp
    

### HTTP 4xx Response

**Meaning:** The server returned a client-error response.

Examples include:

- `401` or `403`: authentication or authorization problem
    
- `404`: incorrect endpoint or routing problem
    
- `408`: request timeout
    
- `429`: rate limiting
    

**Potentially retryable:** Depends on the specific status code.

**Data stored:**

- HTTP status code
    
- Response latency
    
- Target endpoint
    
- Probe timestamp
    

A blanket health or gate decision must not be assigned to all `4xx` responses because their causes and recovery behaviour differ.

### HTTP 5xx Response

**Meaning:** The server returned a server-side error response.

**Potentially retryable:** Usually, but this depends on the status code and retry policy.

**Data stored:**

- HTTP status code
    
- Response latency
    
- Target endpoint
    
- Probe timestamp
    

### Invalid or Unexpected Response

**Meaning:** A response was received, but it did not match the expected format or health-check contract.

Examples include:

- Invalid JSON
    
- Missing required field
    
- Unexpected response body
    
- Unsupported content type
    

**Potentially retryable:** Depends on whether the problem is transient or caused by a persistent contract mismatch.

**Data stored:**

- HTTP status code
    
- Response latency
    
- Validation error
    
- Relevant response metadata
    
- Probe timestamp
    

### Internal Probe Error

**Meaning:** PRCP failed while executing or processing the probe because of an internal implementation problem.

**Potentially retryable:** Not automatically.

**Data stored:**

- Exception type
    
- Sanitized error message
    
- Elapsed time
    
- Probe timestamp
    

This category should remain separate from failures produced by the monitored service.

## Scope Boundary

Month 1 defines raw probe outcomes and the information captured for each outcome.

The following concerns are deliberately deferred:

- `PASS`, `WARN`, `BLOCK`, and `UNKNOWN` decisions
    
- Retry count and backoff policy
    
- Failure thresholds
    
- Consecutive-success or consecutive-failure rules
    
- Promotion-gate behaviour
    
- Idempotency
    
- Aggregation across multiple probes