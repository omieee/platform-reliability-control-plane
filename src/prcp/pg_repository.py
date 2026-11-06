import psycopg

from prcp.exceptions import (
    DuplicateServiceError,
)
from prcp.models import Service


class PgServiceRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    def save(self, service: Service) -> None:
        if self.get_by_name(service_name=service.name):
            raise DuplicateServiceError(service_name=service.name)
        else:
            sql = "INSERT INTO service (name, url) values (%s, %s)"
            data = (
                service.name,
                service.url,
            )
            self.conn.execute(query=sql, params=data)

    def get_by_name(self, service_name: str) -> Service | None:
        sql = "SELECT name, url FROM service WHERE name = %s"
        data = (service_name,)
        row = self.conn.execute(query=sql, params=data).fetchone()
        return None if row is None else Service(name=row[0], url=row[1])

    def list_all(self) -> list[Service]:
        ret_list = []
        sql = "SELECT name, url FROM service"
        all_rows = self.conn.execute(query=sql).fetchall()
        for _, srv in enumerate(all_rows):
            newServ = Service(name=srv[0], url=srv[1])
            ret_list.append(newServ)
        return ret_list
