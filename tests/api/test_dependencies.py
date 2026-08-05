from prcp.api.dependencies import get_environment_repository, get_service_repository
from prcp.repository import InMemoryEnvironmentRepository, InMemoryServiceRepository


def test_get_service_repository_returns_same_instance() -> None:
    first_repository = get_service_repository()
    second_repository = get_service_repository()

    assert first_repository is second_repository
    assert isinstance(first_repository, InMemoryServiceRepository)


def test_get_environment_repository_returns_same_instance() -> None:
    first_repository = get_environment_repository()
    second_repository = get_environment_repository()

    assert first_repository is second_repository
    assert isinstance(first_repository, InMemoryEnvironmentRepository)
