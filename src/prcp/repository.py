from typing import Protocol

from prcp.models import Environment, Service


class EnvironmentRepository(Protocol):
    def save(self, environment: Environment) -> None: ...
    def get_by_name(self, environment_name: str) -> Environment | None: ...
    def list_all(self) -> list[Environment]: ...


class InMemoryEnvironmentRepository:
    def __init__(self) -> None:
        self._environments: dict[str, Environment] = {}

    def save(self, environment: Environment) -> None:
        self._environments[environment.name] = environment

    def get_by_name(self, environment_name: str) -> Environment | None:
        return self._environments.get(environment_name)

    def list_all(self) -> list[Environment]:
        return list(self._environments.values())


class ServiceRepository(Protocol):
    def save(self, service: Service) -> None: ...
    def get_by_name(self, service_name: str) -> Service | None: ...
    def list_all(self) -> list[Service]: ...


class InMemoryServiceRepository:
    def __init__(self) -> None:
        self._services: dict[str, Service] = {}

    def save(self, service: Service) -> None:
        self._services[service.name] = service

    def get_by_name(self, service_name: str) -> Service | None:
        return self._services.get(service_name)

    def list_all(self) -> list[Service]:
        return list(self._services.values())
