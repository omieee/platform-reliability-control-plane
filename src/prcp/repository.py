from http import HTTPMethod
from typing import Protocol
from uuid import UUID

from prcp.exceptions import (
    DuplicateEnvironmentError,
    DuplicateProbeError,
    DuplicateServiceError,
)
from prcp.models import Environment, Probe, Service


class EnvironmentRepository(Protocol):
    def save(self, environment: Environment) -> None: ...
    def get_by_name(self, environment_name: str) -> Environment | None: ...
    def list_all(self) -> list[Environment]: ...


class InMemoryEnvironmentRepository:
    def __init__(self) -> None:
        self._environments: dict[str, Environment] = {}

    def save(self, environment: Environment) -> None:
        if environment.name in self._environments:
            raise DuplicateEnvironmentError(environment_name=environment.name)
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
        if service.name in self._services:
            raise DuplicateServiceError(service_name=service.name)
        self._services[service.name] = service

    def get_by_name(self, service_name: str) -> Service | None:
        return self._services.get(service_name)

    def list_all(self) -> list[Service]:
        return list(self._services.values())


ProbeKey = tuple[str, str, HTTPMethod, str]


class ProbeRepository(Protocol):
    def save(self, probe: Probe) -> None: ...
    def get_by_id(self, probe_id: UUID) -> Probe | None: ...
    def list_all(self) -> list[Probe]: ...


class InMemoryProbeRepository:
    def __init__(self) -> None:
        self._probes_by_id: dict[UUID, Probe] = {}
        self._probe_ids_by_key: dict[ProbeKey, UUID] = {}

    def save(self, probe: Probe) -> None:
        key = (
            probe.service.name,
            probe.environment.name,
            probe.method,
            probe.path,
        )

        existing_probe_id = self._probe_ids_by_key.get(key)

        if existing_probe_id is not None:
            raise DuplicateProbeError(existing_probe_id)

        self._probes_by_id[probe.id] = probe
        self._probe_ids_by_key[key] = probe.id

    def get_by_id(self, probe_id: UUID) -> Probe | None:
        return self._probes_by_id.get(probe_id)

    def list_all(self) -> list[Probe]:
        return list(self._probes_by_id.values())
