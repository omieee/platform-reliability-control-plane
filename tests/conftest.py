from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from prcp.api.dependencies import get_service_repository
from prcp.api.main import app
from prcp.repository import InMemoryServiceRepository, ServiceRepository


@pytest.fixture
def service_repository() -> InMemoryServiceRepository:
    """A new empty repository is created for every test."""
    return InMemoryServiceRepository()


@pytest.fixture
def client(
    service_repository: InMemoryServiceRepository,
) -> Iterator[TestClient]:
    """Replace the production repository with the test repository."""

    def override_get_service_repository() -> ServiceRepository:
        return service_repository

    app.dependency_overrides[get_service_repository] = override_get_service_repository

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_service_repository, None)
