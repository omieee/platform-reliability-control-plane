import os

import psycopg

from prcp.pg_repository import PgServiceRepository
from prcp.repository import (
    EnvironmentRepository,
    InMemoryEnvironmentRepository,
    InMemoryProbeRepository,
    InMemoryProbeResultRepository,
    InMemoryServiceRepository,
    ProbeRepository,
    ProbeResultRepository,
)

_service_repository = InMemoryServiceRepository()
_environment_repository = InMemoryEnvironmentRepository()
_probe_repository = InMemoryProbeRepository()
_probe_result_repository = InMemoryProbeResultRepository()


def get_service_repository():
    with psycopg.connect(os.environ["PRCP_DSN"]) as conn:
        yield PgServiceRepository(conn)


def get_environment_repository() -> EnvironmentRepository:
    return _environment_repository


def get_probe_repository() -> ProbeRepository:
    return _probe_repository


def get_probe_result_repository() -> ProbeResultRepository:
    return _probe_result_repository
