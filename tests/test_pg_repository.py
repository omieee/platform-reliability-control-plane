from uuid import uuid4

import pytest

from prcp.exceptions import DuplicateEnvironmentError, DuplicateServiceError
from prcp.models import Environment, Service, create_environment, create_service
from prcp.pg_repository import PgEnvironmentRepository, PgServiceRepository


def test_save_service(pg_conn) -> None:
    name = f"test-{uuid4().hex}"
    service = create_service(name, "https://example.com")

    repo = PgServiceRepository(pg_conn)
    repo.save(service)

    row = pg_conn.execute(
        "SELECT name, url FROM service WHERE name = %s",
        (name,),
    ).fetchone()

    assert row == (service.name, service.url)


def test_get_by_name_is_valid(pg_conn) -> None:
    s1name = f"test-{uuid4().hex}"
    service = create_service(s1name, "https://example.com")

    repo = PgServiceRepository(pg_conn)
    repo.save(service)

    row = repo.get_by_name(s1name)

    assert row == Service(name=service.name, url=service.url)


def test_get_by_name_is_not_valid(pg_conn) -> None:
    s1name = f"test-{uuid4().hex}"
    service = create_service(s1name, "https://example.com")

    repo = PgServiceRepository(pg_conn)
    repo.save(service)

    row = repo.get_by_name("om-service-not-exist")
    assert row is None


def test_list_all_includes_saved_services(pg_conn) -> None:
    s1name = f"test-{uuid4().hex}"
    service1 = create_service(s1name, "https://example.com")

    repo = PgServiceRepository(pg_conn)
    repo.save(service1)

    s2name = f"test-{uuid4().hex}"
    service2 = create_service(s2name, "https://example.com")

    repo = PgServiceRepository(pg_conn)
    repo.save(service2)

    row = repo.list_all()
    assert service1 in row
    assert service2 in row


def test_same_service_name_raises_duplicate_error(pg_conn) -> None:
    serv_repo = PgServiceRepository(pg_conn)

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


def test_save_environment(pg_conn) -> None:
    name = f"test-{uuid4().hex}"
    region = "us-south"
    cluster = "pre-prod"
    env = create_environment(environment_name=name, region=region, cluster=cluster)

    repo = PgEnvironmentRepository(pg_conn)
    repo.save(environment=env)
    row = pg_conn.execute(
        "SELECT name, region, cluster FROM environment WHERE name = %s",
        (name,),
    ).fetchone()

    assert row == (env.name, env.region, env.cluster)


def test_get_by_env_name_is_valid(pg_conn) -> None:
    e1name = f"test-{uuid4().hex}"
    env = create_environment(e1name, "us-south", "pre-prod")

    repo = PgEnvironmentRepository(pg_conn)
    repo.save(environment=env)

    row = repo.get_by_name(environment_name=e1name)

    assert row == Environment(name=env.name, region=env.region, cluster=env.cluster)


def test_get_by_env_name_is_not_valid(pg_conn) -> None:
    e1name = f"test-{uuid4().hex}"
    env = create_environment(e1name, "us-southpre-prod")

    repo = PgEnvironmentRepository(pg_conn)
    repo.save(env)

    row = repo.get_by_name("om-environment-not-exist")
    assert row is None


def test_list_all_includes_saved_environment(pg_conn) -> None:
    e1name = f"test-{uuid4().hex}"
    env1 = create_environment(e1name, "us-south", "pre-prod")

    repo = PgEnvironmentRepository(pg_conn)
    repo.save(env1)

    e2name = f"test-{uuid4().hex}"
    env2 = create_environment(e2name, "us-southpre-prod")

    repo = PgEnvironmentRepository(pg_conn)
    repo.save(env2)

    row = repo.list_all()
    assert env1 in row
    assert env2 in row


def test_same_env_name_raises_duplicate_error(pg_conn) -> None:
    env_repo = PgEnvironmentRepository(pg_conn)
    envname = f"test-{uuid4().hex}"
    old_env = create_environment(
        environment_name=envname, region="us-south", cluster="pre-prod"
    )
    new_env = create_environment(
        environment_name=envname, region="us-east", cluster="dev"
    )

    env_repo.save(old_env)

    with pytest.raises(DuplicateEnvironmentError):
        env_repo.save(new_env)
