from prcp.models import Environment, Service


class InMemoryEnvironmentRepository:
    def __init__(self) -> None:
        self._environment: dict[str, Environment] = {}

    def save_envirnmont(self, environment: Environment) -> None:
        self._environment[environment.name] = environment

    def get_environment(self, environment_name: str) -> Environment | None:
        return self._environment.get(environment_name)

    def list_environment(self) -> list[Environment]:
        return list[Environment](self._environment.values())


class InMemoryServiceRepository:
    def __init__(self) -> None:
        self._services: dict[str, Service] = {}

    def save_service(self, service: Service) -> None:
        self._services[service.name] = service

    def get_service(self, service_name: str) -> Service | None:
        return self._services.get(service_name)

    def list_services(self) -> list[Service]:
        return list[Service](self._services.values())
