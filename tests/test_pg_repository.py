from uuid import uuid4

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


def test_list_all_returns_correct_count(pg_conn) -> None:
    s1name = f"test-{uuid4().hex}"
    service1 = create_service(s1name, "https://example.com")

    repo = PgServiceRepository(pg_conn)
    repo.save(service1)

    s2name = f"test-{uuid4().hex}"
    service2 = create_service(s2name, "https://example.com")

    repo = PgServiceRepository(pg_conn)
    repo.save(service2)

    row = repo.list_all()
    assert service1 and service2 in row
