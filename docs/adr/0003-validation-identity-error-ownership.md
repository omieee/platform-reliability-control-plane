# ADR-0003: Validation, Identity, and Error Ownership Across Layers

- **Status:** Accepted
- **Date:** 2026-08-05
- **Decision owners:** PRCP maintainers
- **Scope:** Service registration, validation, identity normalization, uniqueness enforcement, and API error translation

## 1. Context / Problem

While implementing service registration, validation, duplicate protection, and consistent API errors, the same rule could often be enforced in more than one layer.

The current request flow is:

```text
HTTP request
→ ServiceCreate validation
→ register_service endpoint
→ create_service domain factory
→ ServiceRepository.save
→ ServiceOut response
```

This created several architectural questions:

1. Why should validation exist in both `ServiceCreate` and `create_service()`?
2. Which layer owns trimming and lowercasing of service names?
3. Which layer owns uniqueness enforcement?
4. Should PRCP-specific exceptions contain HTTP metadata?
5. Why are missing services and duplicate services represented differently internally?
6. How should Pydantic validation locations be exposed to API clients?
7. What changes when the in-memory repository is replaced by PostgreSQL?
8. Which parts of the external API contract must remain stable?

There is already evidence that duplicated validation can drift. The API validator strips whitespace before checking whether a name is blank, while the current domain factory checks truthiness before stripping. Therefore, a whitespace-only name is rejected by the API but may be handled differently when `create_service()` is called directly.

The purpose of this ADR is not to list the current implementation. It assigns ownership of validation, identity, persistence invariants, and error translation across layers.

## 2. Options Considered

### 2.1 Validation ownership

#### Option A: Validate only in the API layer

`ServiceCreate` would reject malformed input, while the domain factory would trust all values passed to it.

**Advantages**

- No duplicated validation.
- Immediate and clear feedback to API clients.
- Simpler domain factory.

**Disadvantages**

- Domain invariants would depend on FastAPI and Pydantic being the only entry path.
- A CLI, background worker, migration, test, or direct Python caller could construct an invalid `Service`.
- The domain model would not protect itself outside the HTTP boundary.

#### Option B: Validate only in the domain layer

The API would pass incoming values to `create_service()`, which would perform all validation.

**Advantages**

- One authoritative validation location.
- Every caller receives the same invariant checks.
- Less risk of duplicated rules drifting.

**Disadvantages**

- The API would provide weaker request-schema documentation.
- Unknown fields, transport-specific typing, and request-shape problems would not be handled as clearly at the boundary.
- API clients would receive less precise validation feedback.

#### Option C: Duplicate every validation rule in both layers

Both `ServiceCreate` and `create_service()` would independently enforce the same rules.

**Advantages**

- Early API rejection.
- Domain protection for non-HTTP callers.

**Disadvantages**

- The same rule has two owners.
- Implementations and messages can drift.
- Changes must be maintained and tested twice.
- The current whitespace-only-name behaviour already demonstrates this risk.

#### Option D: Validate at both boundaries, with explicit ownership

The API validates transport concerns and provides early client feedback. The domain owns invariants and canonical identity that must remain true regardless of entry point.

**Advantages**

- Preserves a strong HTTP boundary.
- Protects the domain from non-HTTP callers.
- Makes ownership explicit instead of blindly duplicating all rules.
- Allows each layer to validate only what it is responsible for.

**Disadvantages**

- Some overlap can still exist.
- Overlapping rules require tests to prevent drift.
- The distinction between request validation and domain invariants must be maintained deliberately.

### 2.2 Service-name normalization

#### Option A: API owns trimming and lowercasing

`ServiceCreate` would produce the canonical service name.

**Advantages**

- The endpoint receives clean input.
- Invalid or blank names can be rejected early.

**Disadvantages**

- Service identity would depend on the HTTP interface.
- A CLI or worker could bypass the normalization rule.
- Non-API callers could create identities that differ from API-created services.

#### Option B: Domain owns trimming and lowercasing

`create_service()` would define the canonical service identity.

**Advantages**

- Every creation path uses the same identity rule.
- `PAY`, `pay`, and ` Pay ` resolve to the same canonical name.
- Identity does not depend on FastAPI or Pydantic.

**Disadvantages**

- The API may perform some overlapping cleanup for early feedback.
- Care is required to avoid contradictory normalization in the API.

#### Option C: Repository owns normalization

The repository would normalize names before storage.

**Advantages**

- Stored keys would be consistent.

**Disadvantages**

- The `Service` object could remain non-canonical before persistence.
- Identity rules would be coupled to storage.
- Different repository implementations could normalize differently.

### 2.3 Uniqueness enforcement

#### Option A: API checks whether the name already exists before saving

**Advantages**

- Straightforward to implement.
- The API can return `409` before attempting persistence.

**Disadvantages**

- The API does not own persisted state.
- Two concurrent requests can both observe that the name is absent and then both attempt insertion.
- The check is race-prone and cannot be the final authority.

#### Option B: Repository or database enforces uniqueness

**Advantages**

- The component that owns persisted state enforces the invariant.
- The same rule applies to API, CLI, worker, and other callers.
- PostgreSQL can enforce the constraint atomically.

**Disadvantages**

- Storage-specific failures must be translated into application-level errors.
- Repository implementations must preserve the same external behaviour.

### 2.4 PRCP-specific errors and HTTP metadata

#### Option A: PRCP-specific exceptions carry HTTP metadata

For example, `DuplicateServiceError` contains `status`, `title`, and `error_type`.

**Advantages**

- `prcp_error_handler()` can translate all PRCP-specific errors through one generic path.
- No separate exception-to-HTTP mapping table is required.
- Less Phase 1 machinery.

**Disadvantages**

- A non-API exception becomes coupled to HTTP concepts.
- CLI and worker callers carry irrelevant HTTP metadata.
- Supporting another transport may require refactoring.

#### Option B: Keep domain/application exceptions transport-neutral

The API would maintain an explicit mapping from exception type to HTTP response metadata.

**Advantages**

- Domain and application code remain independent of HTTP.
- Other interfaces can reuse the same errors naturally.
- Transport-specific behaviour stays in the API layer.

**Disadvantages**

- Requires additional translation code.
- Error mappings must be maintained separately.
- Adds abstraction before PRCP has another interface.

### 2.5 Missing-service and duplicate-service behaviour

#### Option A: Use application exceptions for both

The repository would raise `ServiceNotFoundError` and `DuplicateServiceError`.

**Advantages**

- Consistent internal error mechanism.
- The API only translates application errors.

**Disadvantages**

- A repository lookup that naturally returns no value would instead use exceptions for normal absence.
- Adds another exception and mapping decision during Phase 1.

#### Option B: Keep the current split

- Duplicate save: repository raises `DuplicateServiceError`.
- Missing lookup: repository returns `None`, and the API raises HTTP `404`.

**Advantages**

- Matches the current repository contract.
- Avoids unnecessary refactoring.
- Duplicate creation remains enforced where persisted state is owned.

**Disadvantages**

- `404` and `409` use different internal mechanisms.
- The API layer interprets one storage result while another is already represented as an application error.

### 2.6 Validation-location representation

#### Option A: Preserve Pydantic’s structured location

Example:

```json
["body", "probes", 0, "timeout"]
```

**Advantages**

- Preserves field names and list indexes without ambiguity.
- Better suited to deeply nested payloads.

**Disadvantages**

- More complex client contract.
- Less convenient for simple logs and form-field mapping.

#### Option B: Convert the location to a dotted string

Example:

```text
body.probes.0.timeout
```

**Advantages**

- Compact and readable.
- Easy to log.
- Easy for simple clients to map to a form field.

**Disadvantages**

- Loses structural precision.
- `0` could represent an array index or a field literally named `"0"`.

## 3. Decision

### 3.1 Validate at both boundaries, with explicit ownership

PRCP will validate at both the API and domain boundaries, but the layers will not be treated as equal owners of every rule.

The API layer owns:

- request shape
- required and extra fields
- transport-compatible input types
- early and precise feedback to HTTP clients
- conversion from API-specific types, such as Pydantic `HttpUrl`, to plain domain values

The domain layer owns:

- invariants that must hold for every `Service`
- canonical service identity
- protection against invalid construction outside FastAPI

Overlapping validation is allowed only when it protects a distinct boundary. Tests must prevent the two implementations from drifting.

### 3.2 The domain owns canonical service-name identity

`create_service()` owns trimming and lowercasing because those operations determine service identity.

The following inputs must resolve to the same canonical name:

```text
PAY
pay
 Pay 
```

The API may reject a whitespace-only name early, but it must not establish a canonical representation that differs from the domain.

The repository must receive and persist a canonical service name.

### 3.3 The repository owns uniqueness enforcement

`ServiceCreate` and `create_service()` validate only the candidate service. They do not know which services already exist.

The repository owns access to persisted state and is therefore responsible for detecting duplicate service identities.

The API must not be the final authority for uniqueness.

### 3.4 PRCP-specific exceptions may carry HTTP metadata during Phase 1

`DuplicateServiceError` may continue to contain:

- `status`
- `title`
- `error_type`
- `detail`

This allows `prcp_error_handler()` to construct a consistent response without maintaining a separate exception-to-HTTP translation map.

This is an accepted Phase 1 coupling because HTTP is currently the only exposed interface.

Framework-generated errors continue to use separate handlers:

```text
RequestValidationError
→ validation_error_handler
→ 422

PRCPError
→ prcp_error_handler
→ PRCP-specific status, currently 409

StarletteHTTPException
→ http_exception_handler
→ 404, 405, and other HTTP errors
```

`PRCPError` does not own or handle all application errors. It is only the base for PRCP-specific exceptions registered with `prcp_error_handler()`.

### 3.5 Keep the current 404 and 409 split during Phase 1

For duplicate creation:

```text
repository.save
→ DuplicateServiceError
→ prcp_error_handler
→ 409
```

For a missing service:

```text
repository.get_by_name
→ None
→ API raises HTTPException
→ http_exception_handler
→ 404
```

The two cases produce the same external error envelope but use different internal mechanisms.

This inconsistency is accepted for Phase 1. It may be reconsidered if repository operations are later standardized around application-level exceptions.

### 3.6 Expose validation locations as dotted strings

The API contract will represent validation locations as strings such as:

```text
body.url
```

`validation_error_handler()` will convert Pydantic locations such as:

```python
("body", "url")
```

into:

```text
body.url
```

This is a deliberate API design choice because `ValidationIssue.field` is defined as a string. It improves readability, logging, and simple client-side field mapping.

The loss of structural precision for nested lists is accepted during Phase 1.

## 4. Rationale

The selected approach separates four different responsibilities:

```text
API validation
→ Is this HTTP request structurally acceptable?

Domain validation
→ Can this value represent a valid Service?

Repository uniqueness
→ Does this Service conflict with persisted state?

API error translation
→ How should an internal failure be represented over HTTP?
```

The domain owns canonical identity because identity must remain consistent across every current and future entry point.

The repository owns uniqueness because only the persistence boundary knows existing state and can enforce the invariant reliably.

Keeping HTTP metadata on PRCP-specific exceptions avoids adding a translation framework before another transport exists. The coupling is acknowledged rather than treated as ideal architecture.

Keeping the current 404 and 409 split avoids unnecessary refactoring while the repository contract is still small.

Dotted validation paths are sufficient for the current shallow request models and provide a simple external contract.

## 5. Risks and Consequences

### 5.1 Validation rules can drift

Validation exists at more than one boundary. Similar checks may become inconsistent.

The current whitespace-only-name behaviour already demonstrates this risk.

**Mitigation**

- Define one authoritative owner for each invariant.
- Add direct domain tests and API validation tests.
- Avoid duplicating transformations unless they protect a distinct boundary.
- Correct the domain blank-name check so normalization occurs before the invariant is evaluated.

### 5.2 Domain/application errors are coupled to HTTP

`DuplicateServiceError` contains HTTP metadata even though it is outside the API package.

**Consequence**

A CLI, worker, or non-HTTP interface would inherit fields that are irrelevant to it.

**Mitigation**

Accept the coupling during Phase 1. Introduce a transport-neutral error model and API translation map only when a second interface or a larger error hierarchy creates a real need.

### 5.3 Missing and duplicate services use different internal mechanisms

A missing lookup returns `None`; a duplicate save raises `DuplicateServiceError`.

**Consequence**

The application has two patterns for representing failures that eventually become the same external error envelope.

**Mitigation**

Keep the behaviour explicit and tested. Revisit the repository contract if more not-found and conflict cases appear.

### 5.4 Dotted validation paths lose structure

A nested location such as:

```text
body.probes.0.timeout
```

does not distinguish an array index from a field named `"0"`.

**Mitigation**

Keep dotted strings while payloads remain shallow. Change `ValidationIssue.field` to a structured list if nested arrays become part of the public API.

### 5.5 Database identity must match domain identity

If the domain treats `PAY` and `pay` as the same service, PostgreSQL must enforce the same rule.

**Mitigation**

Persist only domain-normalized lowercase names, or introduce an appropriate case-insensitive database constraint. The database and domain must not disagree about canonical identity.

## 6. Phase 2 Changes

The in-memory repository will eventually be replaced by a PostgreSQL-backed repository.

The authoritative uniqueness mechanism will move from:

```text
if service.name in self._services
```

to a PostgreSQL unique constraint or unique index.

The save flow will become:

```text
Attempt INSERT
→ PostgreSQL enforces uniqueness atomically
→ duplicate insert raises a database uniqueness violation
→ PostgresServiceRepository translates it into DuplicateServiceError
→ prcp_error_handler returns the existing 409 contract
```

The repository must not rely on a separate read-before-write uniqueness check because two concurrent requests could both observe that the name is absent and then attempt insertion.

The dictionary pre-check will disappear. PostgreSQL will become the final authority for persisted uniqueness.

Internal implementation may change substantially, but API clients must continue receiving the same external behaviour:

```text
Valid creation          → 201
Duplicate service       → 409
Invalid request         → 422
Missing service         → 404
Unsupported method      → 405
```

The common error response shape must remain stable:

```json
{
  "type": "urn:prcp:error:service-conflict",
  "title": "Service already exists",
  "status": 409,
  "detail": "Service 'pay' already exists",
  "instance": "/services"
}
```

Validation failures may additionally include:

```json
{
  "errors": [
    {
      "field": "body.url",
      "message": "URL scheme should be 'http' or 'https'"
    }
  ]
}
```

API clients must not need to know whether uniqueness was enforced by:

- an in-memory dictionary
- PostgreSQL
- a unique constraint
- a database exception

That separation is the purpose of the repository abstraction and API error translation.

## 7. Follow-up Actions

1. Correct the domain whitespace-only-name validation so it evaluates the normalized value.
2. Add or retain tests proving that `PAY`, `pay`, and ` Pay ` resolve to one canonical identity.
3. Keep full API-body assertions for `409`, `404`, `422`, and `405`.
4. Preserve the existing response contract when PostgreSQL is introduced.
5. Revisit HTTP metadata on `PRCPError` only when a second interface or a larger exception hierarchy justifies the additional translation layer.
6. Revisit dotted validation paths when nested arrays become part of the API.
7. Update `create_http_probe()` when probe work begins so URL validation does not continue using `startswith(("http://", "https://"))`.

## 8. Decision Summary

PRCP will use boundary-specific validation rather than treating one layer as the owner of every check.

- The API validates HTTP request structure and provides early client feedback.
- The domain owns `Service` invariants and canonical identity.
- The repository owns uniqueness against persisted state.
- PRCP-specific exceptions may carry HTTP metadata as an accepted Phase 1 simplification.
- Missing and duplicate services retain their current internal mechanisms during Phase 1.
- Validation locations are exposed as dotted strings.
- PostgreSQL will replace in-memory uniqueness enforcement without changing the external API contract.