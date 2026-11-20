import psycopg

from prcp.exceptions import DuplicateEnvironmentError, DuplicateServiceError
from prcp.models import Environment, Service


class PgServiceRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    def save(self, service: Service) -> None:
        sql = "INSERT INTO service (name, url) values (%s, %s)"
        data = (
            service.name,
            service.url,
        )
        try:
            self.conn.execute(query=sql, params=data)
        except psycopg.errors.UniqueViolation as e:
            raise DuplicateServiceError(service_name=service.name) from e

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


class PgEnvironmentRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    def save(self, environment: Environment) -> None:
        sql = "insert into environment (name, region, cluster) values (%s, %s, %s)"
        data = (environment.name, environment.region, environment.cluster)
        try:
            self.conn.execute(query=sql, params=data)
        except psycopg.errors.UniqueViolation as e:
            raise DuplicateEnvironmentError(environment_name=environment.name) from e

    def get_by_name(self, environment_name: str) -> Environment | None:
        sql = "select name, region, cluster FROM environment where name = %s"
        data = (environment_name,)
        row = self.conn.execute(query=sql, params=data).fetchone()
        return (
            None
            if row is None
            else Environment(name=row[0], region=row[1], cluster=row[2])
        )

    def list_all(self) -> list[Environment]:
        ret_list = []
        sql = "SELECT name, region, cluster FROM environment"
        all_rows = self.conn.execute(query=sql).fetchall()
        for _, env in enumerate(all_rows):
            newEnv = Environment(name=env[0], region=env[1], cluster=env[2])
            ret_list.append(newEnv)
        return ret_list
