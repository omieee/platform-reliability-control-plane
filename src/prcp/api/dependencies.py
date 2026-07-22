from prcp.repository import InMemoryServiceRepository, ServiceRepository

_service_repository = InMemoryServiceRepository()


def get_service_repository() -> ServiceRepository:
    return _service_repository
