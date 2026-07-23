import pytest

from prcp.exceptions import DuplicateServiceException
from prcp.models import create_environment, create_service
from prcp.repository import (
    EnvironmentRepository,
    InMemoryEnvironmentRepository,
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


def test_same_environment_name_overwrites_old_environment() -> None:
    env_repo = InMemoryEnvironmentRepository()
    old_env = create_environment(environment_name="pre-prod", region="eu-gb")
    new_env = create_environment(environment_name="pre-prod", region="us-south")
    env_repo.save(old_env)
    env_repo.save(new_env)
    ret_env = env_repo.get_by_name("pre-prod")
    assert ret_env is not None
    assert ret_env.region == "us-south"


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

    with pytest.raises(DuplicateServiceException):
        serv_repo.save(new_serv)

    returned_service = serv_repo.get_by_name("signup-api")

    assert returned_service is not None
    assert returned_service.url == "http://api.v1.payment.abc.com"
