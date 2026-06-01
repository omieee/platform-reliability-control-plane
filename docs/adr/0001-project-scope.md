# ADR-0001: Define Project Scope as a Platform Reliability Control Plane

## Status

Accepted

## Date

2026-06-01

## Context

Software releases usually move through environments such as dev, preprod, and prod. Before a release is promoted, a platform team needs a reliable way to decide whether the target service or environment is healthy enough to continue.

A simple health check alone is not enough. A release gate must also classify failures such as timeout, connection error, HTTP status mismatch, and unknown result. Without this classification, the system cannot clearly distinguish between a service being unhealthy and the checker itself being unable to reach a reliable conclusion.

This project is intended to model that release/environment reliability decision. It starts with a narrow HTTP probe slice before adding APIs, storage, scheduling, observability, or Kubernetes deployment.

## Decision

We will build this project as a Platform Reliability Control Plane.

The system will eventually evaluate service and environment health and produce gate decisions such as PASS, WARN, BLOCK, or UNKNOWN.

For Week 1, the implementation will stay deliberately small:

- define service, HTTP probe, and probe result structures
- validate basic service and probe input
- run one HTTP check
- classify the result as pass, fail, or unknown
- test the checker without making real network calls

## Current Scope

The current implementation includes only:

- simple Python model helper functions
- string constants for status and failure reasons
- one HTTP checker function
- pytest tests for model creation and HTTP result classification

The current implementation does not include a web API, database, scheduler, metrics endpoint, Docker image, Kubernetes deployment, or Go runner.

## Non-Goals

- This project is not a generic uptime monitor.
- It is not a dashboard-first monitoring system.
- It is not a Kubernetes operator in Phase 1 Week 1.
- It is not a FastAPI CRUD application.
- It is not an AI infrastructure project yet.
- Those may become adjacent later, but the first decision is to model release and environment reliability gates clearly.

## Alternatives Considered

### Generic uptime monitor

Rejected because uptime monitoring alone is too passive and too generic. It does not clearly show release-gate decision-making, failure classification, or platform control-plane thinking.

### FastAPI health-check API first

Rejected for Week 1 because starting with HTTP APIs before the domain model would create shallow backend structure without clarifying the reliability decision model.

### Kubernetes operator first

Rejected because operator work is premature before the domain model, probe behavior, tests, and local control-plane semantics are clear.

## Consequences

This decision keeps the first implementation small but aligned with a larger platform-engineering direction.

Benefits:

- the project has a clear platform reliability identity
- the first code slice is testable without infrastructure
- failure classification starts early
- future API, storage, metrics, and Kubernetes work can be added around a stable core

Costs:

- the Week 1 implementation may look small compared with the final project name
- more advanced features are intentionally deferred
- the project needs strong documentation so the small first slice does not look like a toy health checker

## Validation

This ADR is valid if the Week 1 project can demonstrate:

- service and probe structures exist
- HTTP probe results are classified correctly
- timeout, connection error, and status mismatch are handled differently
- tests run without real network calls
- the README and architecture document explain the release-gate direction

## Follow-ups

Future ADRs should cover:

- sync vs async check execution
- storage model for services and probe results
- retry, timeout, and backoff policy
- Python control plane and Go probe runner boundary
- Kubernetes deployment model