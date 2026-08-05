from prcp.repository import (
    EnvironmentRepository,
    InMemoryEnvironmentRepository,
    InMemoryServiceRepository,
    ServiceRepository,
)

_service_repository = InMemoryServiceRepository()
_environment_repository = InMemoryEnvironmentRepository()


def get_service_repository() -> ServiceRepository:
    return _service_repository


def get_environment_repository() -> EnvironmentRepository:
    return _environment_repository
