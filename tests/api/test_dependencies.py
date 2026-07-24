from prcp.api.dependencies import get_service_repository
from prcp.repository import InMemoryServiceRepository


def test_get_service_repository_returns_same_instance() -> None:
    first_repository = get_service_repository()
    second_repository = get_service_repository()

    assert first_repository is second_repository
    assert isinstance(first_repository, InMemoryServiceRepository)
