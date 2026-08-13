from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from prcp.api.dependencies import (
    get_environment_repository,
    get_probe_repository,
    get_probe_result_repository,
    get_service_repository,
)
from prcp.api.main import app
from prcp.repository import (
    EnvironmentRepository,
    InMemoryEnvironmentRepository,
    InMemoryProbeRepository,
    InMemoryProbeResultRepository,
    InMemoryServiceRepository,
    ProbeRepository,
    ProbeResultRepository,
    ServiceRepository,
)


@pytest.fixture
def service_repository() -> InMemoryServiceRepository:
    """Create a new empty service repository for every test."""
    return InMemoryServiceRepository()


@pytest.fixture
def environment_repository() -> InMemoryEnvironmentRepository:
    """Create a new empty environment repository for every test."""
    return InMemoryEnvironmentRepository()


@pytest.fixture
def probe_repository() -> InMemoryProbeRepository:
    """Create a new empty probe repository for every test."""
    return InMemoryProbeRepository()


@pytest.fixture
def probe_result_repository() -> InMemoryProbeResultRepository:
    """Create a new empty probe result repository for every test."""
    return InMemoryProbeResultRepository()


@pytest.fixture
def client(
    service_repository: InMemoryServiceRepository,
    environment_repository: InMemoryEnvironmentRepository,
    probe_repository: InMemoryProbeRepository,
    probe_result_repository: InMemoryProbeResultRepository,
) -> Iterator[TestClient]:
    """Replace production repositories with isolated test repositories."""

    def override_get_service_repository() -> ServiceRepository:
        return service_repository

    def override_get_environment_repository() -> EnvironmentRepository:
        return environment_repository

    def override_get_probe_repository() -> ProbeRepository:
        return probe_repository

    def override_get_probe_result_repository() -> ProbeResultRepository:
        return probe_result_repository

    app.dependency_overrides[get_service_repository] = override_get_service_repository
    app.dependency_overrides[get_environment_repository] = (
        override_get_environment_repository
    )
    app.dependency_overrides[get_probe_repository] = override_get_probe_repository
    app.dependency_overrides[get_probe_result_repository] = (
        override_get_probe_result_repository
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_service_repository, None)
    app.dependency_overrides.pop(get_environment_repository, None)
    app.dependency_overrides.pop(get_probe_repository, None)
    app.dependency_overrides.pop(get_probe_result_repository, None)
