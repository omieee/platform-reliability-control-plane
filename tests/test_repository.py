from prcp.models import create_environment, create_service
from prcp.repository import InMemoryEnvironmentRepository, InMemoryServiceRepository


def test_new_repository_starts_with_empty_environment() -> None:
    env_repo = InMemoryEnvironmentRepository()

    assert env_repo.list_environment() == []


def test_save_environment_nakes_it_accessible() -> None:
    env_repo = InMemoryEnvironmentRepository()
    environment = create_environment(
        environment_name="preprod",
        region="us-south",
    )

    env_repo.save_envirnmont(environment)

    saved_environment = env_repo.get_environment(environment_name="preprod")

    assert saved_environment == environment


def test_when_environment_is_not_available() -> None:
    repository = InMemoryServiceRepository()

    saved_env = repository.get_service("missing-environment")

    assert saved_env is None


"""
Below is service testing
"""


def test_new_repository_starts_with_empty_services() -> None:
    repository = InMemoryServiceRepository()

    assert repository.list_services() == []


def test_save_service_makes_it_retrievable() -> None:
    repository = InMemoryServiceRepository()
    service = create_service(
        service_name="payment-api",
        service_url="https://payment.example.com",
    )

    repository.save_service(service)

    saved_service = repository.get_service("payment-api")

    assert saved_service == service


def test_get_missing_service_returns_none() -> None:
    repository = InMemoryServiceRepository()

    saved_service = repository.get_service("missing-api")

    assert saved_service is None


def test_list_services_returns_saved_services() -> None:
    repository = InMemoryServiceRepository()
    payment_service = create_service(
        service_name="payment-api",
        service_url="https://payment.example.com",
    )
    billing_service = create_service(
        service_name="billing-api",
        service_url="https://billing.example.com",
    )

    repository.save_service(payment_service)
    repository.save_service(billing_service)

    services = repository.list_services()

    assert payment_service in services
    assert billing_service in services
    assert len(services) == 2


def test_save_service_with_same_name_overwrites_old_service() -> None:
    repository = InMemoryServiceRepository()
    old_service = create_service(
        service_name="payment-api",
        service_url="https://old-payment.example.com",
    )
    new_service = create_service(
        service_name="payment-api",
        service_url="https://new-payment.example.com",
    )

    repository.save_service(old_service)
    repository.save_service(new_service)

    saved_service = repository.get_service("payment-api")

    assert saved_service == new_service
    assert repository.list_services() == [new_service]
