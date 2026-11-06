from uuid import uuid4

import pytest

from prcp.exceptions import (
    DuplicateServiceError,
)
from prcp.models import Service, create_service
from prcp.pg_repository import PgServiceRepository


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

    returned_service = serv_repo.get_by_name("signup-api")

    assert returned_service is not None
    assert returned_service.url == "http://api.v1.payment.abc.com"
