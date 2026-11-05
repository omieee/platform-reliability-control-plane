from uuid import uuid4

from prcp.models import create_service
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
