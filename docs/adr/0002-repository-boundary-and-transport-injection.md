# ADR-0002: Repository Boundary and HTTP Transport Injection

## Status

Accepted

## Date

2026-06-06

## Context

PRCP currently has typed domain models for services, environments, probes, and probe results.

At this stage, PRCP needs two clean seams:

1. A storage seam, so application code does not depend directly on dictionaries, lists, or a future database implementation.
2. An HTTP transport seam, so probe-checking logic can be tested without making real network calls.

Postgres, FastAPI, persistence, scheduling, and gate-decision aggregation are not part of the current Week 2 scope.

## Decision

### 1. Use repository boundaries for Service and Environment storage

Define lightweight repository contracts for storing and retrieving `Service` and `Environment` objects.

Current implementation:

* `InMemoryServiceRepository`
* `InMemoryEnvironmentRepository`

Current supported operations:

* `save`
* `get_by_name`
* `list_all`

The in-memory repositories store objects in dictionaries keyed by name.

Duplicate names currently overwrite the previous value.

### 2. Use Protocol for repository contracts

Use `typing.Protocol` for repository contracts instead of Abstract Base Classes.

Reason:

* Protocols are lightweight.
* They define the expected method shape.
* They avoid forcing inheritance.
* They are enough for the current storage boundary.

This is mainly a static typing and design seam. It is not runtime persistence.

### 3. Use HTTP transport injection in `http_check`

`http_check` accepts an injected HTTP function, defaulting to `httpx.get`.

Production code can call:

```python
http_check(probe)
```

Tests can call:

```python
http_check(probe, http_get=fake_http_get)
```

This allows checker tests to simulate success, HTTP failure, timeout, and request errors without real network calls or monkeypatching.

## Consequences

### Positive

* Storage behavior is isolated behind repository methods.
* In-memory storage can later be replaced by Postgres with less application-code churn.
* Checker logic is easier to test.
* Unit tests no longer need real HTTP calls.
* The project has clearer seams between domain models, storage, and transport.

### Negative

* There is slightly more structure than direct dictionaries and direct `httpx.get` calls.
* Protocol understanding is still early and will need reinforcement later.
* The in-memory repository does not persist data after process exit.
* Duplicate overwrite behavior is simple and may need stricter rules later.

## Validation Strategy

Repository behavior is tested through:

* empty repository state
* save and retrieve behavior
* missing object returns `None`
* list all objects
* duplicate name overwrite behavior
* protocol compatibility smoke tests

HTTP checker behavior is tested through injected fake HTTP functions for:

* matching expected status
* mismatched status
* custom expected status
* timeout
* request error

## Alternatives Considered

### Direct dictionaries in business logic

Rejected.

This would couple application logic to temporary in-memory storage and make the later Postgres transition messier.

### Direct `httpx.get` inside tests with monkeypatching

Rejected.

Monkeypatching works, but transport injection is clearer and keeps the checker easier to test.

### Abstract Base Classes

Deferred.

ABC would enforce inheritance, but Protocol is lighter and enough for the current Week 2 boundary.

### Postgres repository now

Rejected.

Postgres belongs to a later phase. Adding it now would create scope creep before the basic model, repository, and checker seams are stable.

## Non-Goals

This ADR does not introduce:

* Postgres
* SQLAlchemy
* FastAPI
* async repository methods
* probe result persistence
* gate-decision aggregation
* deployment health policy logic
* Kubernetes integration

## Follow-Up

Later phases may add:

* Postgres-backed repositories
* probe result history repository
* stricter uniqueness rules
* timestamps for probe results
* gate-decision aggregation across multiple probe results
* API-level dependency injection
