import psycopg

from prcp.models import Service


class PgServiceRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    def save(self, service: Service) -> None:
        sql = "INSERT INTO service (name, url) values (%s, %s)"
        data = (
            service.name,
            service.url,
        )
        self.conn.execute(query=sql, params=data)
