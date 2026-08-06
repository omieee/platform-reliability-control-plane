from http import HTTPMethod
from uuid import uuid4

import pytest

from prcp.exceptions import (
    DuplicateEnvironmentError,
    DuplicateProbeError,
    DuplicateServiceError,
)
from prcp.models import (
    Probe,
    create_environment,
    create_http_probe,
    create_service,
)
from prcp.repository import (
    EnvironmentRepository,
    InMemoryEnvironmentRepository,
    InMemoryProbeRepository,
    InMemoryServiceRepository,
    ServiceRepository,
)


def test_new_repository_starts_with_empty_environment() -> None:
    env_repo = InMemoryEnvironmentRepository()

    assert env_repo.list_all() == []


def test_save_environment_makes_it_retrievable() -> None:
    env_repo = InMemoryEnvironmentRepository()
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )

    env_repo.save(environment)

    saved_environment = env_repo.get_by_name(environment_name="preprod")

    assert saved_environment == environment


def test_when_environment_is_not_available() -> None:
    env_repo = InMemoryEnvironmentRepository()

    saved_env = env_repo.get_by_name("missing-environment")

    assert saved_env is None


def test_list_environments_return_saved_environments() -> None:
    env_repo = InMemoryEnvironmentRepository()
    pre_prod = create_environment(
        environment_name="preprod",
        region="us-south",
    )
    prod = create_environment(
        environment_name="prod",
        region="eu-gb",
    )
    env_repo.save(pre_prod)
    env_repo.save(prod)

    envs = env_repo.list_all()

    assert pre_prod in envs
    assert prod in envs


def test_in_memory_environment_repository_matches_protocol() -> None:
    repository: EnvironmentRepository = InMemoryEnvironmentRepository()
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )
    repository.save(environment=environment)

    assert repository.get_by_name("preprod") == environment


def test_new_service_starts_with_empty_service() -> None:
    serv_repo = InMemoryServiceRepository()
    assert serv_repo.list_all() == []


def test_service_save_makes_it_retrievable() -> None:
    serv_repo = InMemoryServiceRepository()

    serv = create_service(
        service_name="payment-api", service_url="http://abc.payment.api"
    )

    serv_repo.save(service=serv)

    assert serv_repo.get_by_name(service_name="payment-api") == serv


def test_in_memory_service_repository_matches_protocol() -> None:
    repository: ServiceRepository = InMemoryServiceRepository()
    service = create_service(
        service_name="payment-api",
        service_url="http://abc.payment.api",
    )
    repository.save(service=service)

    assert repository.get_by_name("payment-api") == service


def test_get_missing_service_returns_none_v_protocol() -> None:
    serv_repo: ServiceRepository = InMemoryServiceRepository()
    serv = create_service(
        service_name="payments-api", service_url="http://api.payment.abc.com"
    )
    serv_repo.save(serv)
    assert serv_repo.get_by_name(service_name="signup-api") is None


def test_list_services_returns_saved_services() -> None:
    serv_repo = InMemoryServiceRepository()
    serv = create_service(
        service_name="payments-api", service_url="http://api.payment.abc.com"
    )
    serv1 = create_service(
        service_name="signup-api", service_url="http://api.signup.abc.com"
    )

    serv_repo.save(serv)
    serv_repo.save(serv1)
    services = serv_repo.list_all()

    assert serv in services
    assert serv1 in services
    assert len(services) == 2


def test_same_service_name_raises_duplicate_error() -> None:
    serv_repo = InMemoryServiceRepository()

    old_serv = create_service(
        service_name="signup-api",
        service_url="http://api.v1.payment.abc.com",
    )
    new_serv = create_service(
        service_name="signup-api",
        service_url="http://api.v2.signup.abc.com",
    )

    serv_repo.save(old_serv)

    with pytest.raises(DuplicateServiceError):
        serv_repo.save(new_serv)

    returned_service = serv_repo.get_by_name("signup-api")

    assert returned_service is not None
    assert returned_service.url == "http://api.v1.payment.abc.com"


def test_same_environment_name_raises_duplicate_error() -> None:
    env_repo = InMemoryEnvironmentRepository()

    old_env = create_environment(environment_name="pre-prod", region="eu-gb")
    new_env = create_environment(environment_name="pre-prod", region="us-south")

    env_repo.save(old_env)

    with pytest.raises(DuplicateEnvironmentError):
        env_repo.save(new_env)

    returned_env = env_repo.get_by_name("pre-prod")

    assert returned_env is not None
    assert returned_env.region == "eu-gb"


def create_test_probe(
    *,
    path: str = "/health",
    method: HTTPMethod = HTTPMethod.GET,
) -> Probe:
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )
    service = create_service(
        service_name="payment-api",
        service_url="https://payment.example.com",
    )

    return create_http_probe(
        environment=environment,
        service=service,
        method=method,
        path=path,
    )


def test_probe_repository_saves_and_gets_probe_by_id() -> None:
    repository = InMemoryProbeRepository()
    probe = create_test_probe()

    repository.save(probe)

    assert repository.get_by_id(probe.id) == probe


def test_probe_repository_returns_none_for_unknown_id() -> None:
    repository = InMemoryProbeRepository()

    assert repository.get_by_id(uuid4()) is None


def test_probe_repository_lists_all_saved_probes() -> None:
    repository = InMemoryProbeRepository()
    health_probe = create_test_probe(path="/health")
    ready_probe = create_test_probe(path="/ready")

    repository.save(health_probe)
    repository.save(ready_probe)

    assert repository.list_all() == [
        health_probe,
        ready_probe,
    ]


def test_probe_repository_rejects_duplicate_composite_key() -> None:
    repository = InMemoryProbeRepository()

    first_probe = create_test_probe(
        method=HTTPMethod.GET,
        path="/health",
    )
    duplicate_probe = create_test_probe(
        method=HTTPMethod.GET,
        path="/health",
    )

    assert first_probe.id != duplicate_probe.id

    repository.save(first_probe)

    with pytest.raises(DuplicateProbeError) as exc_info:
        repository.save(duplicate_probe)

    assert exc_info.value.existing_probe_id == first_probe.id
    assert repository.get_by_id(first_probe.id) == first_probe
    assert repository.get_by_id(duplicate_probe.id) is None
    assert repository.list_all() == [first_probe]
